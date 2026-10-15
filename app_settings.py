import json
import os

from app_constants import SETTINGS_FILE


def get_default_settings():
    """
    Возвращает словарь настроек по умолчанию.

    Пока нам нужна только одна настройка:
    - last_used_dir: последняя папка, с которой работал пользователь

    Позже сюда легко можно добавить:
    - последний формат сохранения
    - размер окна
    - последний выбранный пресет
    и т.д.
    """
    return {
        "last_used_dir": ""
    }


def load_settings():

    if not os.path.exists(SETTINGS_FILE):
        settings = get_default_settings()
        save_settings(settings)
        return settings

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        settings = get_default_settings()
        save_settings(settings)
        return settings

    if not isinstance(data, dict):
        settings = get_default_settings()
        save_settings(settings)
        return settings

    settings = get_default_settings()
    settings["last_used_dir"] = str(data.get("last_used_dir", "")).strip()

    return settings


def save_settings(settings: dict):

    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(settings, file, ensure_ascii=False, indent=4)