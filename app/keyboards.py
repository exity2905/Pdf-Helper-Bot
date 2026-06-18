from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.i18n import LANGUAGE_LABELS, button, t


def language_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=LANGUAGE_LABELS["uk"]),
                KeyboardButton(text=LANGUAGE_LABELS["ru"]),
            ],
            [
                KeyboardButton(text=LANGUAGE_LABELS["en"]),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder=t("uk", "language_placeholder"),
    )


def main_menu_keyboard(lang: str = "uk") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=button(lang, "scan")),
                KeyboardButton(text=button(lang, "tools")),
            ],
            [
                KeyboardButton(text=button(lang, "help")),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder=t(lang, "main_placeholder"),
    )


def scan_menu_keyboard(lang: str = "uk") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=button(lang, "scan_document")),
                KeyboardButton(text=button(lang, "id_document")),
            ],
            [
                KeyboardButton(text=button(lang, "photo_to_pdf")),
            ],
            [
                KeyboardButton(text=button(lang, "back")),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder=t(lang, "scan_placeholder"),
    )


def tools_menu_keyboard(lang: str = "uk") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=button(lang, "compress_pdf")),
                KeyboardButton(text=button(lang, "split_pdf")),
            ],
            [
                KeyboardButton(text=button(lang, "merge_pdf")),
            ],
            [
                KeyboardButton(text=button(lang, "extract_text")),
                KeyboardButton(text=button(lang, "pdf_to_word")),
            ],
            [
                KeyboardButton(text=button(lang, "word_to_pdf")),
                KeyboardButton(text=button(lang, "ai_summary")),
            ],
            [
                KeyboardButton(text=button(lang, "back")),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder=t(lang, "tools_placeholder"),
    )


def merge_menu_keyboard(lang: str = "uk") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=button(lang, "merge_now")),
            ],
            [
                KeyboardButton(text=button(lang, "back")),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder=t(lang, "tools_placeholder"),
    )


def pdf_actions_keyboard(lang: str = "uk") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=button(lang, "compress_pdf"), callback_data="pdf:compress"),
                InlineKeyboardButton(text=button(lang, "split_pdf"), callback_data="pdf:split"),
            ],
            [
                InlineKeyboardButton(text=button(lang, "merge_pdf"), callback_data="pdf:merge_start"),
            ],
            [
                InlineKeyboardButton(text=button(lang, "extract_text"), callback_data="pdf:text"),
                InlineKeyboardButton(text=button(lang, "pdf_to_word"), callback_data="pdf:word"),
            ],
            [
                InlineKeyboardButton(text=button(lang, "ai_summary"), callback_data="pdf:summary"),
            ],
        ]
    )
