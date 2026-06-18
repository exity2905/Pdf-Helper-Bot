from pathlib import Path

import cv2
import img2pdf
import numpy as np
from PIL import Image


def make_scan_pdf(input_path: Path, output_path: Path, mode: str | None = None) -> Path:
    scanned_image = output_path.with_suffix(".jpg")
    make_scan_image(input_path, scanned_image, mode=mode)

    with scanned_image.open("rb") as image_file:
        pdf_bytes = img2pdf.convert(image_file)

    output_path.write_bytes(pdf_bytes)
    return output_path


def make_scan_image(input_path: Path, output_path: Path, mode: str | None = None) -> Path:
    image = cv2.imread(str(input_path))
    if image is None:
        raise ValueError(f"Cannot read image: {input_path}")

    paper, scan_kind = _find_document(image, mode=mode)
    enhanced = _enhance_scan(paper, scan_kind)
    if _is_bad_scan(enhanced):
        enhanced = _enhance_color_scan(paper)

    if len(enhanced.shape) == 2:
        output_image = Image.fromarray(enhanced)
    else:
        output_image = Image.fromarray(cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB))

    output_image.save(output_path, quality=96, optimize=True)
    return output_path


def _find_document(image: np.ndarray, mode: str | None = None) -> tuple[np.ndarray, str]:
    original = image.copy()
    ratio = image.shape[0] / 900.0
    resized = cv2.resize(image, (int(image.shape[1] / ratio), 900))
    resized_area = resized.shape[0] * resized.shape[1]

    if mode == "photo":
        return original, "photo"

    if mode in (None, "identity"):
        identity_crop = _find_identity_document_crop(resized, ratio, original)
        if identity_crop is not None:
            return identity_crop, "identity"

        if mode == "identity":
            return original, "identity"

    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 75, 200)

    contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    for contour in contours:
        if _touches_frame(contour, resized.shape):
            continue

        if cv2.contourArea(contour) < resized_area * 0.25:
            continue

        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        if len(approx) == 4:
            points = approx.reshape(4, 2) * ratio
            transformed = _four_point_transform(original, points)
            if _is_page_like(transformed, original):
                return transformed, "document"

    masked = _find_document_by_color_mask(resized, ratio, original)
    if masked is not None:
        return masked, "document"

    return original, mode or "photo"


def _find_identity_document_crop(
    resized: np.ndarray,
    ratio: float,
    original: np.ndarray,
) -> np.ndarray | None:
    hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
    lab = cv2.cvtColor(resized, cv2.COLOR_BGR2LAB)
    _, saturation, value = cv2.split(hsv)
    lightness, _, lab_blue = cv2.split(lab)
    frame_area = resized.shape[0] * resized.shape[1]

    best_candidate: tuple[float, np.ndarray] | None = None

    for lab_blue_max in (136, 140):
        for saturation_max in (35, 45, 55):
            mask = (
                (saturation < saturation_max)
                & (value > 85)
                & (lightness > 85)
                & (lab_blue < lab_blue_max)
            ).astype("uint8") * 255

            components_count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
            for component_index in range(1, components_count):
                x, y, width, height, area = stats[component_index]
                if area < frame_area * 0.15 or area > frame_area * 0.5:
                    continue

                if _box_touches_frame(x, y, width, height, resized.shape):
                    continue

                aspect_ratio = width / max(height, 1)
                if not 0.55 <= aspect_ratio <= 1.8:
                    continue

                component = (labels == component_index).astype("uint8") * 255
                contours, _ = cv2.findContours(
                    component,
                    cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE,
                )
                if not contours:
                    continue

                contour = max(contours, key=cv2.contourArea)
                hull = cv2.convexHull(contour)
                perimeter = cv2.arcLength(hull, True)
                approx = cv2.approxPolyDP(hull, 0.025 * perimeter, True)
                if len(approx) != 4:
                    continue

                x, y, width, height = cv2.boundingRect(approx)
                crop = resized[y : y + height, x : x + width]
                crop_hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
                crop_saturation = crop_hsv[:, :, 1]
                crop_value = crop_hsv[:, :, 2]
                color_ratio = float(np.mean((crop_saturation > 55) & (crop_value > 80)))
                if color_ratio < 0.06:
                    continue

                score = float(area / frame_area) + color_ratio
                if best_candidate is None or score > best_candidate[0]:
                    best_candidate = (score, approx.reshape(4, 2).astype("float32"))

    if best_candidate is None:
        return None

    points = _repair_identity_quad(best_candidate[1]) * ratio
    return _crop_polygon_on_white(original, points)


def _repair_identity_quad(points: np.ndarray) -> np.ndarray:
    rect = _order_points(points)
    top_left, top_right, bottom_right, bottom_left = rect

    page_height = max(
        np.linalg.norm(bottom_left - top_left),
        np.linalg.norm(bottom_right - top_right),
    )
    if top_left[1] > top_right[1] + page_height * 0.12:
        target_y = top_right[1]
        dy = top_left[1] - bottom_left[1]
        if abs(dy) > 1:
            ratio = (target_y - bottom_left[1]) / dy
            target_x = bottom_left[0] + ratio * (top_left[0] - bottom_left[0])
            top_left = np.array([target_x, target_y], dtype="float32")
        else:
            top_left = np.array([top_left[0], target_y], dtype="float32")

    repaired = np.array([top_left, top_right, bottom_right, bottom_left], dtype="float32")
    width = max(
        np.linalg.norm(top_right - top_left),
        np.linalg.norm(bottom_right - bottom_left),
    )
    right_inset = width * 0.035
    repaired[1][0] -= right_inset
    repaired[2][0] -= right_inset
    return _expand_polygon(repaired, 1.005)


def _expand_polygon(points: np.ndarray, scale: float) -> np.ndarray:
    center = points.mean(axis=0)
    return ((points - center) * scale) + center


def _crop_polygon_on_white(image: np.ndarray, points: np.ndarray) -> np.ndarray | None:
    x, y, width, height = cv2.boundingRect(points.astype("int32"))
    padding = int(max(width, height) * 0.025)
    x = max(0, x - padding)
    y = max(0, y - padding)
    width = min(image.shape[1] - x, width + padding * 2)
    height = min(image.shape[0] - y, height + padding * 2)

    crop = image[y : y + height, x : x + width]
    if crop.size == 0:
        return None

    local_points = points.copy()
    local_points[:, 0] -= x
    local_points[:, 1] -= y

    mask = np.zeros(crop.shape[:2], dtype="uint8")
    cv2.fillConvexPoly(mask, local_points.astype("int32"), 255)

    result = np.full_like(crop, 255)
    result[mask == 255] = crop[mask == 255]
    return result


def _find_document_by_color_mask(
    resized: np.ndarray,
    ratio: float,
    original: np.ndarray,
) -> np.ndarray | None:
    hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
    lab = cv2.cvtColor(resized, cv2.COLOR_BGR2LAB)
    _, saturation, value = cv2.split(hsv)
    lightness, _, lab_blue = cv2.split(lab)
    frame_area = resized.shape[0] * resized.shape[1]

    best_candidate: tuple[float, np.ndarray] | None = None

    for lab_blue_max in (132, 136, 140):
        for saturation_max in (35, 45, 55):
            mask = (
                (saturation < saturation_max)
                & (value > 85)
                & (lightness > 85)
                & (lab_blue < lab_blue_max)
            ).astype("uint8") * 255

            components_count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
            for component_index in range(1, components_count):
                x, y, width, height, area = stats[component_index]
                if area < frame_area * 0.18 or area > frame_area * 0.85:
                    continue

                if _box_touches_frame(x, y, width, height, resized.shape):
                    continue

                aspect_ratio = width / max(height, 1)
                if not 0.35 <= aspect_ratio <= 1.2:
                    continue

                component = (labels == component_index).astype("uint8") * 255
                contours, _ = cv2.findContours(
                    component,
                    cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE,
                )
                if not contours:
                    continue

                contour = max(contours, key=cv2.contourArea)
                hull = cv2.convexHull(contour)
                perimeter = cv2.arcLength(hull, True)
                approx = cv2.approxPolyDP(hull, 0.03 * perimeter, True)
                if len(approx) != 4:
                    continue

                score = float(area / frame_area)
                if best_candidate is None or score > best_candidate[0]:
                    best_candidate = (score, approx.reshape(4, 2).astype("float32"))

    if best_candidate is None:
        return None

    points = best_candidate[1] * ratio
    transformed = _four_point_transform(original, points)
    if _is_page_like(transformed, original):
        return transformed

    return None


def _four_point_transform(image: np.ndarray, points: np.ndarray) -> np.ndarray:
    rect = _order_points(points)
    top_left, top_right, bottom_right, bottom_left = rect

    width_a = np.linalg.norm(bottom_right - bottom_left)
    width_b = np.linalg.norm(top_right - top_left)
    max_width = int(max(width_a, width_b))

    height_a = np.linalg.norm(top_right - bottom_right)
    height_b = np.linalg.norm(top_left - bottom_left)
    max_height = int(max(height_a, height_b))

    destination = np.array(
        [
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1],
        ],
        dtype="float32",
    )

    matrix = cv2.getPerspectiveTransform(rect, destination)
    return cv2.warpPerspective(image, matrix, (max_width, max_height))


def _order_points(points: np.ndarray) -> np.ndarray:
    rect = np.zeros((4, 2), dtype="float32")
    point_sum = points.sum(axis=1)
    point_diff = np.diff(points, axis=1)

    rect[0] = points[np.argmin(point_sum)]
    rect[2] = points[np.argmax(point_sum)]
    rect[1] = points[np.argmin(point_diff)]
    rect[3] = points[np.argmax(point_diff)]
    return rect


def _touches_frame(contour: np.ndarray, shape: tuple[int, ...], margin: int = 3) -> bool:
    x, y, width, height = cv2.boundingRect(contour)
    return _box_touches_frame(x, y, width, height, shape, margin)


def _box_touches_frame(
    x: int,
    y: int,
    width: int,
    height: int,
    shape: tuple[int, ...],
    margin: int = 3,
) -> bool:
    frame_height, frame_width = shape[:2]
    return (
        x <= margin
        or y <= margin
        or x + width >= frame_width - margin
        or y + height >= frame_height - margin
    )


def _enhance_scan(image: np.ndarray, scan_kind: str = "document") -> np.ndarray:
    if scan_kind == "identity":
        return _enhance_color_scan(image)

    if scan_kind == "photo":
        return _enhance_color_scan(image)

    return _enhance_text_scan(image)


def _enhance_text_scan(image: np.ndarray) -> np.ndarray:
    image = _upscale_for_scan(image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    enhanced = cv2.convertScaleAbs(gray, alpha=1.12, beta=8)
    blurred = cv2.GaussianBlur(enhanced, (0, 0), 0.9)
    return cv2.addWeighted(enhanced, 1.35, blurred, -0.35, 0)


def _enhance_color_scan(image: np.ndarray) -> np.ndarray:
    image = _upscale_for_scan(image)
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    lightness, channel_a, channel_b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=1.8, tileGridSize=(8, 8))
    lightness = clahe.apply(lightness)

    enhanced = cv2.merge((lightness, channel_a, channel_b))
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

    blurred = cv2.GaussianBlur(enhanced, (0, 0), 1.1)
    return cv2.addWeighted(enhanced, 1.25, blurred, -0.25, 0)


def _upscale_for_scan(image: np.ndarray, target_short_side: int = 1800) -> np.ndarray:
    height, width = image.shape[:2]
    short_side = min(height, width)
    if short_side >= target_short_side:
        return image

    scale = target_short_side / short_side
    size = (int(width * scale), int(height * scale))
    return cv2.resize(image, size, interpolation=cv2.INTER_CUBIC)


def _deskew_image(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    min_line_length = max(80, int(image.shape[1] * 0.3))
    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        threshold=80,
        minLineLength=min_line_length,
        maxLineGap=25,
    )
    if lines is None:
        return image

    weighted_angles: list[tuple[float, float]] = []
    for line in lines[:, 0]:
        x1, y1, x2, y2 = line
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0:
            continue

        angle = float(np.degrees(np.arctan2(dy, dx)))
        if -12 <= angle <= 12:
            length = float(np.hypot(dx, dy))
            weighted_angles.append((angle, length))

    if not weighted_angles:
        return image

    angles = np.array([angle for angle, _ in weighted_angles])
    weights = np.array([weight for _, weight in weighted_angles])
    order = np.argsort(angles)
    sorted_angles = angles[order]
    sorted_weights = weights[order]
    midpoint = sorted_weights.sum() / 2
    angle = float(sorted_angles[np.searchsorted(np.cumsum(sorted_weights), midpoint)])

    if abs(angle) < 0.4:
        return image

    return _rotate_image(image, angle)


def _rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    height, width = image.shape[:2]
    center = (width / 2, height / 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    cos = abs(matrix[0, 0])
    sin = abs(matrix[0, 1])
    new_width = int((height * sin) + (width * cos))
    new_height = int((height * cos) + (width * sin))
    matrix[0, 2] += (new_width / 2) - center[0]
    matrix[1, 2] += (new_height / 2) - center[1]

    border_value = [245, 245, 245]
    return cv2.warpAffine(
        image,
        matrix,
        (new_width, new_height),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=border_value,
    )


def _is_page_like(candidate: np.ndarray, original: np.ndarray) -> bool:
    height, width = candidate.shape[:2]
    original_height, original_width = original.shape[:2]

    if width < original_width * 0.35 or height < original_height * 0.35:
        return False

    aspect_ratio = width / height
    return 0.45 <= aspect_ratio <= 1.7


def _is_bad_scan(image: np.ndarray) -> bool:
    height, width = image.shape[:2]
    if width < 300 or height < 300:
        return True

    gray = image if len(image.shape) == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    white_ratio = float(np.mean(gray > 248))
    contrast = float(gray.std())
    return white_ratio > 0.98 or contrast < 8
