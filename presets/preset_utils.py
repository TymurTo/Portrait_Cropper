def normalize_preset(raw_preset):

    if not isinstance(raw_preset, dict):
        return None

    name = str(raw_preset.get("name", "")).strip()

    try:
        width = int(raw_preset.get("width", 0))
        height = int(raw_preset.get("height", 0))
    except (TypeError, ValueError):
        return None

    if not name:
        return None

    if width <= 0 or height <= 0:
        return None

    return {
        "name": name,
        "width": width,
        "height": height,
        "export_enabled": bool(raw_preset.get("export_enabled", False)),
        "user_defined": bool(raw_preset.get("user_defined", False)),
    }


def make_safe_filename_part(text: str) -> str:

    safe = "".join(
        ch if ch.isalnum() or ch in (" ", "_", "-") else "_"
        for ch in text
    ).strip()

    safe = safe.replace(" ", "_")

    if not safe:
        safe = "preset"

    return safe