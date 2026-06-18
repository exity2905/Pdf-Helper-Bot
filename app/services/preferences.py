import json
from pathlib import Path

from app.config import RUNTIME_DIR
from app.i18n import DEFAULT_LANG, SUPPORTED_LANGS


PREFERENCES_PATH = RUNTIME_DIR / "preferences.json"
_PREFERENCES: dict[str, str] | None = None


def get_user_lang(user_id: int) -> str:
    preferences = _load_preferences()
    return preferences.get(str(user_id), DEFAULT_LANG)


def set_user_lang(user_id: int, lang: str) -> None:
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG

    preferences = _load_preferences()
    preferences[str(user_id)] = lang
    _save_preferences(preferences)


def _load_preferences() -> dict[str, str]:
    global _PREFERENCES
    if _PREFERENCES is not None:
        return _PREFERENCES

    if not PREFERENCES_PATH.exists():
        _PREFERENCES = {}
        return _PREFERENCES

    try:
        data = json.loads(PREFERENCES_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        _PREFERENCES = {}
        return _PREFERENCES

    _PREFERENCES = {
        str(user_id): lang
        for user_id, lang in data.items()
        if lang in SUPPORTED_LANGS
    }
    return _PREFERENCES


def _save_preferences(preferences: dict[str, str]) -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    PREFERENCES_PATH.write_text(
        json.dumps(preferences, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
