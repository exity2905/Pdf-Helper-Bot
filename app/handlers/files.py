from pathlib import Path

from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile, Message

from app.keyboards import (
    BTN_AI_SUMMARY,
    BTN_BACK,
    BTN_COMPRESS_PDF,
    BTN_EXTRACT_TEXT,
    BTN_HELP,
    BTN_ID_DOCUMENT,
    BTN_PDF_TO_WORD,
    BTN_PHOTO_TO_PDF,
    BTN_SCAN,
    BTN_SCAN_DOCUMENT,
    BTN_SPLIT_PDF,
    BTN_TOOLS,
    BTN_WORD_TO_PDF,
    main_menu_keyboard,
    pdf_actions_keyboard,
    scan_menu_keyboard,
    tools_menu_keyboard,
)
from app.services.converters import ConversionError, pdf_to_word, word_to_pdf
from app.services.image_scan import make_scan_pdf
from app.services.pdf_tools import compress_pdf, extract_pdf_text, split_pdf
from app.services.storage import get_user_dir, last_pdf_path, save_telegram_file


router = Router()
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
WORD_SUFFIXES = {".doc", ".docx"}
USER_MODES: dict[int, str] = {}
USER_PDF_ACTIONS: dict[int, str] = {}

MENU_TEXTS = {
    BTN_SCAN,
    BTN_SCAN_DOCUMENT,
    BTN_ID_DOCUMENT,
    BTN_PHOTO_TO_PDF,
    BTN_TOOLS,
    BTN_COMPRESS_PDF,
    BTN_SPLIT_PDF,
    BTN_EXTRACT_TEXT,
    BTN_PDF_TO_WORD,
    BTN_WORD_TO_PDF,
    BTN_AI_SUMMARY,
    BTN_HELP,
    BTN_BACK,
}

MODE_TO_SCAN_MODE = {
    "document": "document",
    "identity": "identity",
    "photo_pdf": "photo",
}


@router.message(F.text.in_(MENU_TEXTS))
async def handle_main_menu(message: Message) -> None:
    user_id = message.from_user.id
    text = message.text

    if text == BTN_SCAN:
        USER_MODES.pop(user_id, None)
        USER_PDF_ACTIONS.pop(user_id, None)
        await message.answer(
            "📸 <b>Скан</b>\n\n"
            "Что нужно отсканировать?",
            reply_markup=scan_menu_keyboard(),
            parse_mode="HTML",
        )
        return

    if text == BTN_SCAN_DOCUMENT:
        USER_MODES[user_id] = "document"
        USER_PDF_ACTIONS.pop(user_id, None)
        await message.answer(
            "📄 <b>Скан документа</b>\n\n"
            "Отправь фото листа, договора, справки или изображение файлом.",
            reply_markup=scan_menu_keyboard(),
            parse_mode="HTML",
        )
        return

    if text == BTN_ID_DOCUMENT:
        USER_MODES[user_id] = "identity"
        USER_PDF_ACTIONS.pop(user_id, None)
        await message.answer(
            "🪪 <b>Паспорт / ID</b>\n\n"
            "Отправь фото паспорта, ID-карты или удостоверения.\n"
            "💡 Лучше как файл, чтобы Telegram не сжал качество.",
            reply_markup=scan_menu_keyboard(),
            parse_mode="HTML",
        )
        return

    if text == BTN_PHOTO_TO_PDF:
        USER_MODES[user_id] = "photo_pdf"
        USER_PDF_ACTIONS.pop(user_id, None)
        await message.answer(
            "🖼 <b>Фото в PDF</b>\n\n"
            "Отправь фото или изображение файлом, я сохраню его в PDF без жесткой обработки.",
            reply_markup=scan_menu_keyboard(),
            parse_mode="HTML",
        )
        return

    if text == BTN_TOOLS:
        USER_MODES[user_id] = "pdf"
        USER_PDF_ACTIONS.pop(user_id, None)
        await message.answer(
            "🧰 <b>PDF-инструменты</b>\n\n"
            "Выбери действие, потом отправь PDF или Word-файл:",
            reply_markup=tools_menu_keyboard(),
            parse_mode="HTML",
        )
        return

    if text in {
        BTN_COMPRESS_PDF,
        BTN_SPLIT_PDF,
        BTN_EXTRACT_TEXT,
        BTN_PDF_TO_WORD,
        BTN_WORD_TO_PDF,
        BTN_AI_SUMMARY,
    }:
        USER_MODES[user_id] = "pdf"
        USER_PDF_ACTIONS[user_id] = _tool_action_from_button(text)
        file_hint = "Word-документ .doc/.docx" if text == BTN_WORD_TO_PDF else "PDF"
        await message.answer(
            f"🧰 <b>{text}</b>\n\n"
            f"Отправь {file_hint}, и я сразу выполню это действие.",
            reply_markup=tools_menu_keyboard(),
            parse_mode="HTML",
        )
        return

    if text == BTN_HELP:
        await message.answer(_help_text(), reply_markup=main_menu_keyboard(), parse_mode="HTML")
        return

    if text == BTN_BACK:
        USER_MODES.pop(user_id, None)
        USER_PDF_ACTIONS.pop(user_id, None)
        await message.answer(
            "🏠 <b>Главное меню</b>\n\n"
            "Выбери раздел:",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )
        return

    USER_MODES.pop(user_id, None)
    USER_PDF_ACTIONS.pop(user_id, None)
    await message.answer(
        "🏠 <b>Главное меню</b>\n\nВыбери раздел:",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )


@router.message(F.photo)
async def handle_photo(message: Message) -> None:
    mode = USER_MODES.get(message.from_user.id)
    if mode == "pdf":
        await message.answer(
            "🧰 Сейчас открыт раздел PDF-инструментов.\nОтправь PDF или выбери другой раздел.",
            reply_markup=tools_menu_keyboard(),
        )
        return

    user_dir = get_user_dir(message.from_user.id)
    photo = message.photo[-1]
    input_path = user_dir / f"photo_{photo.file_unique_id}.jpg"
    output_path = user_dir / f"scan_{photo.file_unique_id}.pdf"

    await save_telegram_file(message.bot, photo.file_id, input_path)
    make_scan_pdf(input_path, output_path, mode=MODE_TO_SCAN_MODE.get(mode))

    await message.answer_document(
        FSInputFile(output_path),
        caption=_scan_result_caption(mode),
        reply_markup=scan_menu_keyboard(),
    )


@router.message(F.document)
async def handle_document(message: Message) -> None:
    document = message.document
    if not document.file_name:
        await message.answer("Пришли файл с названием, чтобы я понял формат.")
        return

    suffix = Path(document.file_name).suffix.lower()
    if suffix in IMAGE_SUFFIXES:
        mode = USER_MODES.get(message.from_user.id)
        if mode == "pdf":
            await message.answer(
                "🧰 Сейчас открыт раздел PDF-инструментов.\nОтправь PDF или выбери другой раздел.",
                reply_markup=tools_menu_keyboard(),
            )
            return

        user_dir = get_user_dir(message.from_user.id)
        input_path = user_dir / f"image_{document.file_unique_id}{suffix}"
        output_path = user_dir / f"scan_{document.file_unique_id}.pdf"

        await save_telegram_file(message.bot, document.file_id, input_path)
        make_scan_pdf(input_path, output_path, mode=MODE_TO_SCAN_MODE.get(mode))

        await message.answer_document(
            FSInputFile(output_path),
            caption=_scan_result_caption(mode),
            reply_markup=scan_menu_keyboard(),
        )
        return

    if suffix in WORD_SUFFIXES:
        user_id = message.from_user.id
        action = USER_PDF_ACTIONS.get(user_id)
        if action and action != "word_pdf":
            await message.answer(
                "Для выбранного действия нужен PDF.\n"
                "Чтобы конвертировать Word в PDF, нажми 📝 Word → PDF.",
                reply_markup=tools_menu_keyboard(),
            )
            return

        user_dir = get_user_dir(user_id)
        input_path = user_dir / f"word_{document.file_unique_id}{suffix}"
        output_path = user_dir / f"{Path(document.file_name).stem}.pdf"

        await save_telegram_file(message.bot, document.file_id, input_path)
        await _run_word_to_pdf(message, input_path, output_path)
        return

    if suffix != ".pdf":
        await message.answer(
            "Пока я принимаю PDF, Word (.doc/.docx) и изображения JPG/PNG/WebP.",
            reply_markup=main_menu_keyboard(),
        )
        return

    user_id = message.from_user.id
    saved_path = last_pdf_path(message.from_user.id)
    await save_telegram_file(message.bot, document.file_id, saved_path)

    action = USER_PDF_ACTIONS.get(user_id)
    if action:
        await _run_pdf_action(message, action, saved_path)
        return

    await message.answer(
        f"📎 <b>PDF получен</b>\n\n{document.file_name}\nЧто сделать?",
        reply_markup=pdf_actions_keyboard(),
        parse_mode="HTML",
    )


def _scan_result_caption(mode: str | None) -> str:
    if mode == "document":
        return "✅ Готово. Сделал скан документа."
    if mode == "identity":
        return "✅ Готово. Сделал скан паспорта / ID."
    if mode == "photo_pdf":
        return "✅ Готово. Сделал PDF из фото."
    return "✅ Готово. Сделал PDF-скан."


def _tool_action_from_button(text: str) -> str:
    if text == BTN_COMPRESS_PDF:
        return "compress"
    if text == BTN_SPLIT_PDF:
        return "split"
    if text == BTN_EXTRACT_TEXT:
        return "text"
    if text == BTN_PDF_TO_WORD:
        return "word"
    if text == BTN_WORD_TO_PDF:
        return "word_pdf"
    if text == BTN_AI_SUMMARY:
        return "summary"
    return "menu"


def _help_text() -> str:
    return (
        "❓ <b>Помощь</b>\n\n"
        "📸 <b>Скан</b>\n"
        "Сначала выбери, что сканируешь: лист, паспорт / ID или обычное фото в PDF.\n\n"
        "🧰 <b>Инструменты</b>\n"
        "Выбери действие, потом отправь PDF или Word-файл. Бот выполнит действие сразу.\n\n"
        "💡 Для лучшего качества отправляй фото как файл, а не как обычное фото."
    )


async def _run_word_to_pdf(message: Message, input_path: Path, output_path: Path) -> None:
    try:
        word_to_pdf(input_path, output_path)
    except ConversionError as exc:
        await message.answer(
            "Не получилось сделать PDF из Word.\n"
            f"Причина: {str(exc)[:700]}",
            reply_markup=tools_menu_keyboard(),
        )
        return

    await message.answer_document(
        FSInputFile(output_path),
        caption="✅ Готово. Word конвертирован в PDF.",
        reply_markup=tools_menu_keyboard(),
    )


async def _run_pdf_action(message: Message, action: str, input_path: Path) -> None:
    if action == "compress":
        output_path = input_path.with_name("compressed.pdf")
        compress_pdf(input_path, output_path)
        await message.answer_document(
            FSInputFile(output_path),
            caption="✅ Готово. PDF сжат.",
            reply_markup=tools_menu_keyboard(),
        )
        return

    if action == "split":
        output_dir = get_user_dir(message.from_user.id) / "pages"
        pages = split_pdf(input_path, output_dir)
        await message.answer(
            f"✅ Готово. Разделил PDF на страниц: {len(pages)}.",
            reply_markup=tools_menu_keyboard(),
        )
        for page in pages[:10]:
            await message.answer_document(FSInputFile(page))
        if len(pages) > 10:
            await message.answer("Первые 10 страниц отправил. Остальные лежат на сервере.")
        return

    if action == "text":
        text = extract_pdf_text(input_path).strip()
        if not text:
            await message.answer(
                "Текст не найден. Возможно, это скан. Тут нужен OCR.",
                reply_markup=tools_menu_keyboard(),
            )
            return

        preview = text[:3500]
        await message.answer(preview, reply_markup=tools_menu_keyboard())
        if len(text) > len(preview):
            await message.answer("Текст длинный, показал первые 3500 символов.")
        return

    if action == "word":
        output_path = input_path.with_suffix(".docx")
        try:
            pdf_to_word(input_path, output_path)
        except ConversionError as exc:
            await message.answer(
                "Не получилось сделать Word из PDF.\n"
                f"Причина: {str(exc)[:700]}",
                reply_markup=tools_menu_keyboard(),
            )
            return

        await message.answer_document(
            FSInputFile(output_path),
            caption="✅ Готово. PDF конвертирован в Word.",
            reply_markup=tools_menu_keyboard(),
        )
        return

    if action == "word_pdf":
        await message.answer(
            "Для Word → PDF отправь файл .doc или .docx.",
            reply_markup=tools_menu_keyboard(),
        )
        return

    if action == "summary":
        await message.answer(
            "🤖 AI-summary подключим после добавления OpenAI API.",
            reply_markup=tools_menu_keyboard(),
        )
        return

    await message.answer(
        "PDF получил. Выбери действие:",
        reply_markup=pdf_actions_keyboard(),
    )


@router.callback_query(F.data == "pdf:compress")
async def on_compress_pdf(callback: CallbackQuery) -> None:
    input_path = last_pdf_path(callback.from_user.id)
    output_path = input_path.with_name("compressed.pdf")

    if not input_path.exists():
        await callback.answer("Сначала отправь PDF.", show_alert=True)
        return

    compress_pdf(input_path, output_path)
    await callback.message.answer_document(
        FSInputFile(output_path),
        caption="✅ Готово. PDF сжат.",
        reply_markup=tools_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "pdf:split")
async def on_split_pdf(callback: CallbackQuery) -> None:
    input_path = last_pdf_path(callback.from_user.id)
    output_dir = get_user_dir(callback.from_user.id) / "pages"

    if not input_path.exists():
        await callback.answer("Сначала отправь PDF.", show_alert=True)
        return

    pages = split_pdf(input_path, output_dir)
    await callback.message.answer(
        f"✅ Готово. Разделил PDF на страниц: {len(pages)}.",
        reply_markup=tools_menu_keyboard(),
    )

    for page in pages[:10]:
        await callback.message.answer_document(FSInputFile(page))

    if len(pages) > 10:
        await callback.message.answer("Первые 10 страниц отправил. Остальные лежат на сервере.")

    await callback.answer()


@router.callback_query(F.data == "pdf:text")
async def on_extract_text(callback: CallbackQuery) -> None:
    input_path = last_pdf_path(callback.from_user.id)

    if not input_path.exists():
        await callback.answer("Сначала отправь PDF.", show_alert=True)
        return

    text = extract_pdf_text(input_path).strip()
    if not text:
        await callback.message.answer(
            "Текст не найден. Возможно, это скан. Тут нужен OCR.",
            reply_markup=tools_menu_keyboard(),
        )
        await callback.answer()
        return

    preview = text[:3500]
    await callback.message.answer(preview, reply_markup=tools_menu_keyboard())
    if len(text) > len(preview):
        await callback.message.answer("Текст длинный, показал первые 3500 символов.")
    await callback.answer()


@router.callback_query(F.data == "pdf:word")
async def on_pdf_to_word(callback: CallbackQuery) -> None:
    input_path = last_pdf_path(callback.from_user.id)
    output_path = input_path.with_suffix(".docx")

    if not input_path.exists():
        await callback.answer("Сначала отправь PDF.", show_alert=True)
        return

    try:
        pdf_to_word(input_path, output_path)
    except ConversionError as exc:
        await callback.message.answer(
            "Не получилось сделать Word из PDF.\n"
            f"Причина: {str(exc)[:700]}",
            reply_markup=tools_menu_keyboard(),
        )
        await callback.answer()
        return

    await callback.message.answer_document(
        FSInputFile(output_path),
        caption="✅ Готово. PDF конвертирован в Word.",
        reply_markup=tools_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "pdf:summary")
async def on_pdf_summary(callback: CallbackQuery) -> None:
    await callback.message.answer(
        "🤖 AI-summary подключим после добавления OpenAI API.",
        reply_markup=tools_menu_keyboard(),
    )
    await callback.answer()


@router.message(F.text)
async def handle_unknown_text(message: Message) -> None:
    await message.answer(
        "🏠 Выбери раздел кнопкой ниже.",
        reply_markup=main_menu_keyboard(),
    )
