DEFAULT_LANG = "uk"
SUPPORTED_LANGS = {"uk", "ru", "en"}

LANGUAGE_LABELS = {
    "uk": "🇺🇦 Українська",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
}

LANGUAGE_BY_LABEL = {label: lang for lang, label in LANGUAGE_LABELS.items()}

BUTTONS = {
    "uk": {
        "scan": "📸 Скан",
        "tools": "🧰 Інструменти",
        "help": "❓ Допомога",
        "back": "⬅️ Назад",
        "scan_document": "📄 Лист / документ",
        "id_document": "🪪 Паспорт / ID",
        "photo_to_pdf": "🖼 Фото в PDF",
        "compress_pdf": "🗜 Стиснути PDF",
        "split_pdf": "✂️ Розділити PDF",
        "extract_text": "📝 Дістати текст",
        "pdf_to_word": "📄 PDF → Word",
        "word_to_pdf": "📝 Word → PDF",
        "ai_summary": "🤖 AI-summary",
    },
    "ru": {
        "scan": "📸 Скан",
        "tools": "🧰 Инструменты",
        "help": "❓ Помощь",
        "back": "⬅️ Назад",
        "scan_document": "📄 Лист / документ",
        "id_document": "🪪 Паспорт / ID",
        "photo_to_pdf": "🖼 Фото в PDF",
        "compress_pdf": "🗜 Сжать PDF",
        "split_pdf": "✂️ Разделить PDF",
        "extract_text": "📝 Достать текст",
        "pdf_to_word": "📄 PDF → Word",
        "word_to_pdf": "📝 Word → PDF",
        "ai_summary": "🤖 AI-summary",
    },
    "en": {
        "scan": "📸 Scan",
        "tools": "🧰 Tools",
        "help": "❓ Help",
        "back": "⬅️ Back",
        "scan_document": "📄 Page / document",
        "id_document": "🪪 Passport / ID",
        "photo_to_pdf": "🖼 Photo to PDF",
        "compress_pdf": "🗜 Compress PDF",
        "split_pdf": "✂️ Split PDF",
        "extract_text": "📝 Extract text",
        "pdf_to_word": "📄 PDF → Word",
        "word_to_pdf": "📝 Word → PDF",
        "ai_summary": "🤖 AI summary",
    },
}

BUTTON_KEY_BY_LABEL = {
    label: key
    for labels in BUTTONS.values()
    for key, label in labels.items()
}

TEXTS = {
    "uk": {
        "choose_language": (
            "👋 Вітаю! Я PDF Helper Bot.\n\n"
            "🌐 Оберіть мову інтерфейсу.\n"
            "Українська встановлена як стандартна."
        ),
        "language_saved": (
            "✅ Мову змінено на українську.\n\n"
            "🏠 <b>Головне меню</b>\n\n"
            "Оберіть розділ:"
        ),
        "help_command": (
            "✨ Як користуватись\n\n"
            "1. Оберіть розділ: 📸 Скан або 🧰 Інструменти.\n"
            "2. Натисніть потрібну дію.\n"
            "3. Надішліть фото, зображення файлом, PDF або Word.\n\n"
            "💡 Для кращої якості надсилайте фото як файл.\n"
            "🌐 Змінити мову можна через /start."
        ),
        "scan_menu": "📸 <b>Скан</b>\n\nЩо потрібно відсканувати?",
        "scan_document": (
            "📄 <b>Скан документа</b>\n\n"
            "Надішліть фото листа, договору, довідки або зображення файлом."
        ),
        "id_document": (
            "🪪 <b>Паспорт / ID</b>\n\n"
            "Надішліть фото паспорта, ID-картки або посвідчення.\n"
            "💡 Краще як файл, щоб Telegram не стискав якість."
        ),
        "photo_to_pdf": (
            "🖼 <b>Фото в PDF</b>\n\n"
            "Надішліть фото або зображення файлом, я збережу його в PDF без жорсткої обробки."
        ),
        "tools_menu": (
            "🧰 <b>PDF-інструменти</b>\n\n"
            "Оберіть дію, потім надішліть PDF або Word-файл:"
        ),
        "tool_prompt": "🧰 <b>{title}</b>\n\nНадішліть {file_hint}, і я одразу виконаю цю дію.",
        "word_file_hint": "Word-документ .doc/.docx",
        "pdf_file_hint": "PDF",
        "main_menu": "🏠 <b>Головне меню</b>\n\nОберіть розділ:",
        "pdf_mode_active": "🧰 Зараз відкритий розділ PDF-інструментів.\nНадішліть PDF або оберіть інший розділ.",
        "need_filename": "Надішліть файл із назвою, щоб я зрозумів формат.",
        "need_pdf_for_action": (
            "Для обраної дії потрібен PDF.\n"
            "Щоб конвертувати Word у PDF, натисніть 📝 Word → PDF."
        ),
        "unsupported_file": "Поки я приймаю PDF, Word (.doc/.docx) і зображення JPG/PNG/WebP.",
        "pdf_received": "📎 <b>PDF отримано</b>\n\n{filename}\nЩо зробити?",
        "scan_document_done": "✅ Готово. Зробив скан документа.",
        "scan_identity_done": "✅ Готово. Зробив скан паспорта / ID.",
        "photo_pdf_done": "✅ Готово. Зробив PDF із фото.",
        "scan_done": "✅ Готово. Зробив PDF-скан.",
        "help_text": (
            "❓ <b>Допомога</b>\n\n"
            "📸 <b>Скан</b>\n"
            "Спочатку оберіть, що скануєте: лист, паспорт / ID або звичайне фото в PDF.\n\n"
            "🧰 <b>Інструменти</b>\n"
            "Оберіть дію, потім надішліть PDF або Word-файл. Бот виконає дію одразу.\n\n"
            "💡 Для кращої якості надсилайте фото як файл."
        ),
        "word_to_pdf_failed": "Не вдалося зробити PDF із Word.\nПричина: {reason}",
        "word_to_pdf_done": "✅ Готово. Word конвертовано в PDF.",
        "pdf_compressed": "✅ Готово. PDF стиснуто.",
        "pdf_split": "✅ Готово. Розділив PDF на сторінок: {count}.",
        "first_pages_sent": "Перші 10 сторінок надіслав. Решта лежить на сервері.",
        "text_not_found": "Текст не знайдено. Можливо, це скан. Тут потрібен OCR.",
        "text_long": "Текст довгий, показав перші 3500 символів.",
        "pdf_to_word_failed": "Не вдалося зробити Word із PDF.\nПричина: {reason}",
        "pdf_to_word_done": "✅ Готово. PDF конвертовано в Word.",
        "send_word_for_pdf": "Для Word → PDF надішліть файл .doc або .docx.",
        "summary_soon": "🤖 AI-summary підключимо після додавання OpenAI API.",
        "choose_pdf_action": "PDF отримав. Оберіть дію:",
        "send_pdf_first": "Спочатку надішліть PDF.",
        "unknown_text": "🏠 Оберіть розділ кнопкою нижче.",
        "main_placeholder": "Оберіть розділ",
        "scan_placeholder": "Що скануємо?",
        "tools_placeholder": "Що зробити з файлом?",
        "language_placeholder": "Оберіть мову",
    },
    "ru": {
        "choose_language": (
            "👋 Привет! Я PDF Helper Bot.\n\n"
            "🌐 Выбери язык интерфейса.\n"
            "Украинский установлен как стандартный."
        ),
        "language_saved": (
            "✅ Язык изменён на русский.\n\n"
            "🏠 <b>Главное меню</b>\n\n"
            "Выбери раздел:"
        ),
        "help_command": (
            "✨ Как пользоваться\n\n"
            "1. Выбери раздел: 📸 Скан или 🧰 Инструменты.\n"
            "2. Нажми нужное действие.\n"
            "3. Отправь фото, изображение файлом, PDF или Word.\n\n"
            "💡 Для лучшего качества отправляй фото как файл.\n"
            "🌐 Изменить язык можно через /start."
        ),
        "scan_menu": "📸 <b>Скан</b>\n\nЧто нужно отсканировать?",
        "scan_document": (
            "📄 <b>Скан документа</b>\n\n"
            "Отправь фото листа, договора, справки или изображение файлом."
        ),
        "id_document": (
            "🪪 <b>Паспорт / ID</b>\n\n"
            "Отправь фото паспорта, ID-карты или удостоверения.\n"
            "💡 Лучше как файл, чтобы Telegram не сжал качество."
        ),
        "photo_to_pdf": (
            "🖼 <b>Фото в PDF</b>\n\n"
            "Отправь фото или изображение файлом, я сохраню его в PDF без жёсткой обработки."
        ),
        "tools_menu": (
            "🧰 <b>PDF-инструменты</b>\n\n"
            "Выбери действие, потом отправь PDF или Word-файл:"
        ),
        "tool_prompt": "🧰 <b>{title}</b>\n\nОтправь {file_hint}, и я сразу выполню это действие.",
        "word_file_hint": "Word-документ .doc/.docx",
        "pdf_file_hint": "PDF",
        "main_menu": "🏠 <b>Главное меню</b>\n\nВыбери раздел:",
        "pdf_mode_active": "🧰 Сейчас открыт раздел PDF-инструментов.\nОтправь PDF или выбери другой раздел.",
        "need_filename": "Пришли файл с названием, чтобы я понял формат.",
        "need_pdf_for_action": (
            "Для выбранного действия нужен PDF.\n"
            "Чтобы конвертировать Word в PDF, нажми 📝 Word → PDF."
        ),
        "unsupported_file": "Пока я принимаю PDF, Word (.doc/.docx) и изображения JPG/PNG/WebP.",
        "pdf_received": "📎 <b>PDF получен</b>\n\n{filename}\nЧто сделать?",
        "scan_document_done": "✅ Готово. Сделал скан документа.",
        "scan_identity_done": "✅ Готово. Сделал скан паспорта / ID.",
        "photo_pdf_done": "✅ Готово. Сделал PDF из фото.",
        "scan_done": "✅ Готово. Сделал PDF-скан.",
        "help_text": (
            "❓ <b>Помощь</b>\n\n"
            "📸 <b>Скан</b>\n"
            "Сначала выбери, что сканируешь: лист, паспорт / ID или обычное фото в PDF.\n\n"
            "🧰 <b>Инструменты</b>\n"
            "Выбери действие, потом отправь PDF или Word-файл. Бот выполнит действие сразу.\n\n"
            "💡 Для лучшего качества отправляй фото как файл."
        ),
        "word_to_pdf_failed": "Не получилось сделать PDF из Word.\nПричина: {reason}",
        "word_to_pdf_done": "✅ Готово. Word конвертирован в PDF.",
        "pdf_compressed": "✅ Готово. PDF сжат.",
        "pdf_split": "✅ Готово. Разделил PDF на страниц: {count}.",
        "first_pages_sent": "Первые 10 страниц отправил. Остальные лежат на сервере.",
        "text_not_found": "Текст не найден. Возможно, это скан. Тут нужен OCR.",
        "text_long": "Текст длинный, показал первые 3500 символов.",
        "pdf_to_word_failed": "Не получилось сделать Word из PDF.\nПричина: {reason}",
        "pdf_to_word_done": "✅ Готово. PDF конвертирован в Word.",
        "send_word_for_pdf": "Для Word → PDF отправь файл .doc или .docx.",
        "summary_soon": "🤖 AI-summary подключим после добавления OpenAI API.",
        "choose_pdf_action": "PDF получил. Выбери действие:",
        "send_pdf_first": "Сначала отправь PDF.",
        "unknown_text": "🏠 Выбери раздел кнопкой ниже.",
        "main_placeholder": "Выбери раздел",
        "scan_placeholder": "Что сканируем?",
        "tools_placeholder": "Что сделать с файлом?",
        "language_placeholder": "Выбери язык",
    },
    "en": {
        "choose_language": (
            "👋 Hi! I am PDF Helper Bot.\n\n"
            "🌐 Choose the interface language.\n"
            "Ukrainian is the default language."
        ),
        "language_saved": (
            "✅ Language changed to English.\n\n"
            "🏠 <b>Main menu</b>\n\n"
            "Choose a section:"
        ),
        "help_command": (
            "✨ How to use\n\n"
            "1. Choose a section: 📸 Scan or 🧰 Tools.\n"
            "2. Press the action you need.\n"
            "3. Send a photo, image file, PDF or Word document.\n\n"
            "💡 For better quality, send photos as files.\n"
            "🌐 You can change the language with /start."
        ),
        "scan_menu": "📸 <b>Scan</b>\n\nWhat do you want to scan?",
        "scan_document": (
            "📄 <b>Document scan</b>\n\n"
            "Send a photo of a page, contract, certificate, or send an image as a file."
        ),
        "id_document": (
            "🪪 <b>Passport / ID</b>\n\n"
            "Send a photo of a passport, ID card, or other identity document.\n"
            "💡 It is better to send it as a file so Telegram does not compress the quality."
        ),
        "photo_to_pdf": (
            "🖼 <b>Photo to PDF</b>\n\n"
            "Send a photo or image file, and I will save it as a PDF without heavy processing."
        ),
        "tools_menu": (
            "🧰 <b>PDF tools</b>\n\n"
            "Choose an action, then send a PDF or Word file:"
        ),
        "tool_prompt": "🧰 <b>{title}</b>\n\nSend {file_hint}, and I will run this action right away.",
        "word_file_hint": "a Word document .doc/.docx",
        "pdf_file_hint": "a PDF",
        "main_menu": "🏠 <b>Main menu</b>\n\nChoose a section:",
        "pdf_mode_active": "🧰 PDF tools are open now.\nSend a PDF or choose another section.",
        "need_filename": "Send a file with a name so I can detect the format.",
        "need_pdf_for_action": (
            "The selected action needs a PDF.\n"
            "To convert Word to PDF, press 📝 Word → PDF."
        ),
        "unsupported_file": "For now I accept PDF, Word (.doc/.docx), and JPG/PNG/WebP images.",
        "pdf_received": "📎 <b>PDF received</b>\n\n{filename}\nWhat should I do?",
        "scan_document_done": "✅ Done. I made a document scan.",
        "scan_identity_done": "✅ Done. I made a passport / ID scan.",
        "photo_pdf_done": "✅ Done. I made a PDF from the photo.",
        "scan_done": "✅ Done. I made a PDF scan.",
        "help_text": (
            "❓ <b>Help</b>\n\n"
            "📸 <b>Scan</b>\n"
            "First choose what you are scanning: a page, passport / ID, or regular photo to PDF.\n\n"
            "🧰 <b>Tools</b>\n"
            "Choose an action, then send a PDF or Word file. The bot will run the action immediately.\n\n"
            "💡 For better quality, send photos as files."
        ),
        "word_to_pdf_failed": "Could not create a PDF from Word.\nReason: {reason}",
        "word_to_pdf_done": "✅ Done. Word has been converted to PDF.",
        "pdf_compressed": "✅ Done. PDF compressed.",
        "pdf_split": "✅ Done. Split PDF into pages: {count}.",
        "first_pages_sent": "I sent the first 10 pages. The rest are stored on the server.",
        "text_not_found": "Text was not found. This may be a scan. OCR is needed here.",
        "text_long": "The text is long, I showed the first 3500 characters.",
        "pdf_to_word_failed": "Could not create Word from PDF.\nReason: {reason}",
        "pdf_to_word_done": "✅ Done. PDF has been converted to Word.",
        "send_word_for_pdf": "For Word → PDF, send a .doc or .docx file.",
        "summary_soon": "🤖 AI summary will be connected after adding the OpenAI API.",
        "choose_pdf_action": "PDF received. Choose an action:",
        "send_pdf_first": "Send a PDF first.",
        "unknown_text": "🏠 Choose a section with the button below.",
        "main_placeholder": "Choose a section",
        "scan_placeholder": "What are we scanning?",
        "tools_placeholder": "What should I do with the file?",
        "language_placeholder": "Choose language",
    },
}


def normalize_lang(lang: str | None) -> str:
    if lang in SUPPORTED_LANGS:
        return lang
    return DEFAULT_LANG


def button(lang: str, key: str) -> str:
    lang = normalize_lang(lang)
    return BUTTONS[lang][key]


def button_key(label: str | None) -> str | None:
    if label is None:
        return None
    return BUTTON_KEY_BY_LABEL.get(label)


def language_by_label(label: str | None) -> str | None:
    if label is None:
        return None
    return LANGUAGE_BY_LABEL.get(label)


def t(lang: str, key: str, **kwargs: object) -> str:
    lang = normalize_lang(lang)
    template = TEXTS[lang][key]
    if kwargs:
        return template.format(**kwargs)
    return template
