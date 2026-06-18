def build_summary_prompt(text: str) -> str:
    return (
        "Сделай краткое и понятное summary документа. "
        "Выдели важные даты, суммы, обязательства и риски.\n\n"
        f"{text}"
    )
