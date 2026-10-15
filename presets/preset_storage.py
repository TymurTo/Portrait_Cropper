import json
import os

from app_constants import PRESETS_FILE
from presets.preset_defaults import get_default_presets
from presets.preset_utils import normalize_preset

def load_presets():

    if not os.path.exists(PRESETS_FILE):
        presets = get_default_presets()
        save_presets(presets)
        return presets

    try:
        with open(PRESETS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        presets = get_default_presets()
        save_presets(presets)
        return presets

    if not isinstance(data, list):
        presets = get_default_presets()
        save_presets(presets)
        return presets

    normalized_presets = []

    for item in data:
        preset = normalize_preset(item)
        if preset is not None:
            normalized_presets.append(preset)

    if not normalized_presets:
        normalized_presets = get_default_presets()
        save_presets(normalized_presets)

    return normalized_presets

def save_presets(presets):

    with open(PRESETS_FILE, "w", encoding="utf-8") as file:
        json.dump(presets, file, ensure_ascii=False, indent=4)