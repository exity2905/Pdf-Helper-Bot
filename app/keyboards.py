from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


BTN_SCAN = "📸 Скан"
BTN_TOOLS = "🧰 Инструменты"
BTN_HELP = "❓ Помощь"
BTN_BACK = "⬅️ Назад"

BTN_SCAN_DOCUMENT = "📄 Лист / документ"
BTN_ID_DOCUMENT = "🪪 Паспорт / ID"
BTN_PHOTO_TO_PDF = "🖼 Фото в PDF"

BTN_COMPRESS_PDF = "🗜 Сжать PDF"
BTN_SPLIT_PDF = "✂️ Разделить PDF"
BTN_EXTRACT_TEXT = "📝 Достать текст"
BTN_PDF_TO_WORD = "📄 PDF → Word"
BTN_WORD_TO_PDF = "📝 Word → PDF"
BTN_AI_SUMMARY = "🤖 AI-summary"


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=BTN_SCAN),
                KeyboardButton(text=BTN_TOOLS),
            ],
            [
                KeyboardButton(text=BTN_HELP),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери раздел",
    )


def scan_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=BTN_SCAN_DOCUMENT),
                KeyboardButton(text=BTN_ID_DOCUMENT),
            ],
            [
                KeyboardButton(text=BTN_PHOTO_TO_PDF),
            ],
            [
                KeyboardButton(text=BTN_BACK),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Что сканируем?",
    )


def tools_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=BTN_COMPRESS_PDF),
                KeyboardButton(text=BTN_SPLIT_PDF),
            ],
            [
                KeyboardButton(text=BTN_EXTRACT_TEXT),
                KeyboardButton(text=BTN_PDF_TO_WORD),
            ],
            [
                KeyboardButton(text=BTN_WORD_TO_PDF),
                KeyboardButton(text=BTN_AI_SUMMARY),
            ],
            [
                KeyboardButton(text=BTN_BACK),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Что сделать с файлом?",
    )


def pdf_actions_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Сжать PDF", callback_data="pdf:compress"),
                InlineKeyboardButton(text="Разделить", callback_data="pdf:split"),
            ],
            [
                InlineKeyboardButton(text="Достать текст", callback_data="pdf:text"),
                InlineKeyboardButton(text="PDF → Word", callback_data="pdf:word"),
            ],
            [
                InlineKeyboardButton(text="AI-summary", callback_data="pdf:summary"),
            ],
        ]
    )
