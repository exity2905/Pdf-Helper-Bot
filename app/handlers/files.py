from html import escape
from pathlib import Path
import shutil

from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile, Message

from app.i18n import BUTTON_KEY_BY_LABEL, button, button_key, t
from app.keyboards import (
    main_menu_keyboard,
    merge_menu_keyboard,
    pdf_actions_keyboard,
    scan_menu_keyboard,
    tools_menu_keyboard,
)
from app.services.converters import ConversionError, pdf_to_word, word_to_pdf
from app.services.image_scan import make_scan_pdf
from app.services.pdf_tools import compress_pdf, extract_pdf_text, merge_pdfs, split_pdf
from app.services.preferences import get_user_lang
from app.services.storage import get_user_dir, last_pdf_path, save_telegram_file


router = Router()
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
WORD_SUFFIXES = {".doc", ".docx"}
USER_MODES: dict[int, str] = {}
USER_PDF_ACTIONS: dict[int, str] = {}
USER_MERGE_FILES: dict[int, list[Path]] = {}

MENU_KEYS = {
    "scan",
    "scan_document",
    "id_document",
    "photo_to_pdf",
    "tools",
    "compress_pdf",
    "split_pdf",
    "merge_pdf",
    "merge_now",
    "extract_text",
    "pdf_to_word",
    "word_to_pdf",
    "ai_summary",
    "help",
    "back",
}
MENU_TEXTS = {
    label
    for label, key in BUTTON_KEY_BY_LABEL.items()
    if key in MENU_KEYS
}
TOOL_KEYS = {
    "compress_pdf",
    "split_pdf",
    "merge_pdf",
    "extract_text",
    "pdf_to_word",
    "word_to_pdf",
    "ai_summary",
}

MODE_TO_SCAN_MODE = {
    "document": "document",
    "identity": "identity",
    "photo_pdf": "photo",
}


@router.message(F.text.in_(MENU_TEXTS))
async def handle_main_menu(message: Message) -> None:
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    key = button_key(message.text)

    if key == "scan":
        USER_MODES.pop(user_id, None)
        USER_PDF_ACTIONS.pop(user_id, None)
        USER_MERGE_FILES.pop(user_id, None)
        await message.answer(
            t(lang, "scan_menu"),
            reply_markup=scan_menu_keyboard(lang),
            parse_mode="HTML",
        )
        return

    if key == "scan_document":
        USER_MODES[user_id] = "document"
        USER_PDF_ACTIONS.pop(user_id, None)
        USER_MERGE_FILES.pop(user_id, None)
        await message.answer(
            t(lang, "scan_document"),
            reply_markup=scan_menu_keyboard(lang),
            parse_mode="HTML",
        )
        return

    if key == "id_document":
        USER_MODES[user_id] = "identity"
        USER_PDF_ACTIONS.pop(user_id, None)
        USER_MERGE_FILES.pop(user_id, None)
        await message.answer(
            t(lang, "id_document"),
            reply_markup=scan_menu_keyboard(lang),
            parse_mode="HTML",
        )
        return

    if key == "photo_to_pdf":
        USER_MODES[user_id] = "photo_pdf"
        USER_PDF_ACTIONS.pop(user_id, None)
        USER_MERGE_FILES.pop(user_id, None)
        await message.answer(
            t(lang, "photo_to_pdf"),
            reply_markup=scan_menu_keyboard(lang),
            parse_mode="HTML",
        )
        return

    if key == "tools":
        USER_MODES[user_id] = "pdf"
        USER_PDF_ACTIONS.pop(user_id, None)
        USER_MERGE_FILES.pop(user_id, None)
        await message.answer(
            t(lang, "tools_menu"),
            reply_markup=tools_menu_keyboard(lang),
            parse_mode="HTML",
        )
        return

    if key == "merge_now":
        await _finish_merge(message, lang)
        return

    if key in TOOL_KEYS:
        USER_MODES[user_id] = "pdf"
        USER_PDF_ACTIONS[user_id] = _tool_action_from_button_key(key)
        if key == "merge_pdf":
            USER_MERGE_FILES[user_id] = []
            await message.answer(
                t(lang, "merge_start"),
                reply_markup=merge_menu_keyboard(lang),
                parse_mode="HTML",
            )
            return

        USER_MERGE_FILES.pop(user_id, None)
        file_hint = t(lang, "word_file_hint") if key == "word_to_pdf" else t(lang, "pdf_file_hint")
        await message.answer(
            t(
                lang,
                "tool_prompt",
                title=button(lang, key),
                file_hint=file_hint,
            ),
            reply_markup=tools_menu_keyboard(lang),
            parse_mode="HTML",
        )
        return

    if key == "help":
        await message.answer(t(lang, "help_text"), reply_markup=main_menu_keyboard(lang), parse_mode="HTML")
        return

    if key == "back":
        USER_MODES.pop(user_id, None)
        USER_PDF_ACTIONS.pop(user_id, None)
        USER_MERGE_FILES.pop(user_id, None)
        await message.answer(
            t(lang, "main_menu"),
            reply_markup=main_menu_keyboard(lang),
            parse_mode="HTML",
        )
        return

    USER_MODES.pop(user_id, None)
    USER_PDF_ACTIONS.pop(user_id, None)
    USER_MERGE_FILES.pop(user_id, None)
    await message.answer(
        t(lang, "main_menu"),
        reply_markup=main_menu_keyboard(lang),
        parse_mode="HTML",
    )


@router.message(F.photo)
async def handle_photo(message: Message) -> None:
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    mode = USER_MODES.get(user_id)

    if mode == "pdf":
        await message.answer(
            t(lang, "pdf_mode_active"),
            reply_markup=tools_menu_keyboard(lang),
        )
        return

    user_dir = get_user_dir(user_id)
    photo = message.photo[-1]
    input_path = user_dir / f"photo_{photo.file_unique_id}.jpg"
    output_path = user_dir / f"scan_{photo.file_unique_id}.pdf"

    await save_telegram_file(message.bot, photo.file_id, input_path)
    make_scan_pdf(input_path, output_path, mode=MODE_TO_SCAN_MODE.get(mode))

    await message.answer_document(
        FSInputFile(output_path),
        caption=_scan_result_caption(mode, lang),
        reply_markup=scan_menu_keyboard(lang),
    )


@router.message(F.document)
async def handle_document(message: Message) -> None:
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    document = message.document

    if not document.file_name:
        await message.answer(t(lang, "need_filename"))
        return

    suffix = Path(document.file_name).suffix.lower()
    if suffix in IMAGE_SUFFIXES:
        mode = USER_MODES.get(user_id)
        if mode == "pdf":
            await message.answer(
                t(lang, "pdf_mode_active"),
                reply_markup=tools_menu_keyboard(lang),
            )
            return

        user_dir = get_user_dir(user_id)
        input_path = user_dir / f"image_{document.file_unique_id}{suffix}"
        output_path = user_dir / f"scan_{document.file_unique_id}.pdf"

        await save_telegram_file(message.bot, document.file_id, input_path)
        make_scan_pdf(input_path, output_path, mode=MODE_TO_SCAN_MODE.get(mode))

        await message.answer_document(
            FSInputFile(output_path),
            caption=_scan_result_caption(mode, lang),
            reply_markup=scan_menu_keyboard(lang),
        )
        return

    if suffix in WORD_SUFFIXES:
        action = USER_PDF_ACTIONS.get(user_id)
        if action and action != "word_pdf":
            await message.answer(
                t(lang, "need_pdf_for_action"),
                reply_markup=tools_menu_keyboard(lang),
            )
            return

        user_dir = get_user_dir(user_id)
        input_path = user_dir / f"word_{document.file_unique_id}{suffix}"
        output_path = user_dir / f"{Path(document.file_name).stem}.pdf"

        await save_telegram_file(message.bot, document.file_id, input_path)
        await _run_word_to_pdf(message, input_path, output_path, lang)
        return

    if suffix != ".pdf":
        await message.answer(
            t(lang, "unsupported_file"),
            reply_markup=main_menu_keyboard(lang),
        )
        return

    action = USER_PDF_ACTIONS.get(user_id)
    if action == "merge":
        merge_files = USER_MERGE_FILES.setdefault(user_id, [])
        user_dir = get_user_dir(user_id)
        merge_dir = user_dir / "merge"
        input_path = merge_dir / f"merge_{len(merge_files) + 1:03}_{document.file_unique_id}.pdf"

        await save_telegram_file(message.bot, document.file_id, input_path)
        merge_files.append(input_path)

        await message.answer(
            t(
                lang,
                "merge_added",
                count=len(merge_files),
                filename=escape(document.file_name),
            ),
            reply_markup=merge_menu_keyboard(lang),
            parse_mode="HTML",
        )
        return

    saved_path = last_pdf_path(user_id)
    await save_telegram_file(message.bot, document.file_id, saved_path)

    if action:
        await _run_pdf_action(message, action, saved_path, lang)
        return

    await message.answer(
        t(lang, "pdf_received", filename=escape(document.file_name)),
        reply_markup=pdf_actions_keyboard(lang),
        parse_mode="HTML",
    )


def _scan_result_caption(mode: str | None, lang: str) -> str:
    if mode == "document":
        return t(lang, "scan_document_done")
    if mode == "identity":
        return t(lang, "scan_identity_done")
    if mode == "photo_pdf":
        return t(lang, "photo_pdf_done")
    return t(lang, "scan_done")


def _tool_action_from_button_key(key: str | None) -> str:
    if key == "compress_pdf":
        return "compress"
    if key == "split_pdf":
        return "split"
    if key == "merge_pdf":
        return "merge"
    if key == "extract_text":
        return "text"
    if key == "pdf_to_word":
        return "word"
    if key == "word_to_pdf":
        return "word_pdf"
    if key == "ai_summary":
        return "summary"
    return "menu"


async def _run_word_to_pdf(message: Message, input_path: Path, output_path: Path, lang: str) -> None:
    try:
        word_to_pdf(input_path, output_path)
    except ConversionError as exc:
        await message.answer(
            t(lang, "word_to_pdf_failed", reason=str(exc)[:700]),
            reply_markup=tools_menu_keyboard(lang),
        )
        return

    await message.answer_document(
        FSInputFile(output_path),
        caption=t(lang, "word_to_pdf_done"),
        reply_markup=tools_menu_keyboard(lang),
    )


async def _finish_merge(message: Message, lang: str) -> None:
    user_id = message.from_user.id
    merge_files = USER_MERGE_FILES.get(user_id, [])

    if len(merge_files) < 2:
        await message.answer(
            t(lang, "merge_need_two"),
            reply_markup=merge_menu_keyboard(lang),
        )
        return

    output_path = get_user_dir(user_id) / "merged.pdf"
    try:
        merge_pdfs(merge_files, output_path)
    except Exception as exc:
        await message.answer(
            t(lang, "merge_failed", reason=str(exc)[:700]),
            reply_markup=merge_menu_keyboard(lang),
        )
        return

    USER_PDF_ACTIONS.pop(user_id, None)
    USER_MERGE_FILES.pop(user_id, None)

    await message.answer_document(
        FSInputFile(output_path),
        caption=t(lang, "merge_done", count=len(merge_files)),
        reply_markup=tools_menu_keyboard(lang),
    )


async def _run_pdf_action(message: Message, action: str, input_path: Path, lang: str) -> None:
    if action == "compress":
        output_path = input_path.with_name("compressed.pdf")
        compress_pdf(input_path, output_path)
        await message.answer_document(
            FSInputFile(output_path),
            caption=t(lang, "pdf_compressed"),
            reply_markup=tools_menu_keyboard(lang),
        )
        return

    if action == "split":
        output_dir = get_user_dir(message.from_user.id) / "pages"
        pages = split_pdf(input_path, output_dir)
        await message.answer(
            t(lang, "pdf_split", count=len(pages)),
            reply_markup=tools_menu_keyboard(lang),
        )
        for page in pages[:10]:
            await message.answer_document(FSInputFile(page))
        if len(pages) > 10:
            await message.answer(t(lang, "first_pages_sent"))
        return

    if action == "merge":
        await message.answer(
            t(lang, "merge_start"),
            reply_markup=merge_menu_keyboard(lang),
            parse_mode="HTML",
        )
        return

    if action == "text":
        text = extract_pdf_text(input_path).strip()
        if not text:
            await message.answer(
                t(lang, "text_not_found"),
                reply_markup=tools_menu_keyboard(lang),
            )
            return

        preview = text[:3500]
        await message.answer(preview, reply_markup=tools_menu_keyboard(lang))
        if len(text) > len(preview):
            await message.answer(t(lang, "text_long"))
        return

    if action == "word":
        output_path = input_path.with_suffix(".docx")
        try:
            pdf_to_word(input_path, output_path)
        except ConversionError as exc:
            await message.answer(
                t(lang, "pdf_to_word_failed", reason=str(exc)[:700]),
                reply_markup=tools_menu_keyboard(lang),
            )
            return

        await message.answer_document(
            FSInputFile(output_path),
            caption=t(lang, "pdf_to_word_done"),
            reply_markup=tools_menu_keyboard(lang),
        )
        return

    if action == "word_pdf":
        await message.answer(
            t(lang, "send_word_for_pdf"),
            reply_markup=tools_menu_keyboard(lang),
        )
        return

    if action == "summary":
        await message.answer(
            t(lang, "summary_soon"),
            reply_markup=tools_menu_keyboard(lang),
        )
        return

    await message.answer(
        t(lang, "choose_pdf_action"),
        reply_markup=pdf_actions_keyboard(lang),
    )


@router.callback_query(F.data == "pdf:compress")
async def on_compress_pdf(callback: CallbackQuery) -> None:
    lang = get_user_lang(callback.from_user.id)
    input_path = last_pdf_path(callback.from_user.id)
    output_path = input_path.with_name("compressed.pdf")

    if not input_path.exists():
        await callback.answer(t(lang, "send_pdf_first"), show_alert=True)
        return

    compress_pdf(input_path, output_path)
    await callback.message.answer_document(
        FSInputFile(output_path),
        caption=t(lang, "pdf_compressed"),
        reply_markup=tools_menu_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "pdf:split")
async def on_split_pdf(callback: CallbackQuery) -> None:
    lang = get_user_lang(callback.from_user.id)
    input_path = last_pdf_path(callback.from_user.id)
    output_dir = get_user_dir(callback.from_user.id) / "pages"

    if not input_path.exists():
        await callback.answer(t(lang, "send_pdf_first"), show_alert=True)
        return

    pages = split_pdf(input_path, output_dir)
    await callback.message.answer(
        t(lang, "pdf_split", count=len(pages)),
        reply_markup=tools_menu_keyboard(lang),
    )

    for page in pages[:10]:
        await callback.message.answer_document(FSInputFile(page))

    if len(pages) > 10:
        await callback.message.answer(t(lang, "first_pages_sent"))

    await callback.answer()


@router.callback_query(F.data == "pdf:merge_start")
async def on_merge_pdf_start(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    lang = get_user_lang(user_id)
    input_path = last_pdf_path(user_id)

    if not input_path.exists():
        await callback.answer(t(lang, "send_pdf_first"), show_alert=True)
        return

    merge_dir = get_user_dir(user_id) / "merge"
    merge_dir.mkdir(parents=True, exist_ok=True)
    first_path = merge_dir / "merge_001_current.pdf"
    shutil.copy2(input_path, first_path)

    USER_MODES[user_id] = "pdf"
    USER_PDF_ACTIONS[user_id] = "merge"
    USER_MERGE_FILES[user_id] = [first_path]

    await callback.message.answer(
        t(lang, "merge_started_with_current"),
        reply_markup=merge_menu_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "pdf:text")
async def on_extract_text(callback: CallbackQuery) -> None:
    lang = get_user_lang(callback.from_user.id)
    input_path = last_pdf_path(callback.from_user.id)

    if not input_path.exists():
        await callback.answer(t(lang, "send_pdf_first"), show_alert=True)
        return

    text = extract_pdf_text(input_path).strip()
    if not text:
        await callback.message.answer(
            t(lang, "text_not_found"),
            reply_markup=tools_menu_keyboard(lang),
        )
        await callback.answer()
        return

    preview = text[:3500]
    await callback.message.answer(preview, reply_markup=tools_menu_keyboard(lang))
    if len(text) > len(preview):
        await callback.message.answer(t(lang, "text_long"))
    await callback.answer()


@router.callback_query(F.data == "pdf:word")
async def on_pdf_to_word(callback: CallbackQuery) -> None:
    lang = get_user_lang(callback.from_user.id)
    input_path = last_pdf_path(callback.from_user.id)
    output_path = input_path.with_suffix(".docx")

    if not input_path.exists():
        await callback.answer(t(lang, "send_pdf_first"), show_alert=True)
        return

    try:
        pdf_to_word(input_path, output_path)
    except ConversionError as exc:
        await callback.message.answer(
            t(lang, "pdf_to_word_failed", reason=str(exc)[:700]),
            reply_markup=tools_menu_keyboard(lang),
        )
        await callback.answer()
        return

    await callback.message.answer_document(
        FSInputFile(output_path),
        caption=t(lang, "pdf_to_word_done"),
        reply_markup=tools_menu_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "pdf:summary")
async def on_pdf_summary(callback: CallbackQuery) -> None:
    lang = get_user_lang(callback.from_user.id)
    await callback.message.answer(
        t(lang, "summary_soon"),
        reply_markup=tools_menu_keyboard(lang),
    )
    await callback.answer()


@router.message(F.text)
async def handle_unknown_text(message: Message) -> None:
    lang = get_user_lang(message.from_user.id)
    await message.answer(
        t(lang, "unknown_text"),
        reply_markup=main_menu_keyboard(lang),
    )
