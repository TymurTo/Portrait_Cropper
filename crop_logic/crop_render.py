from PySide6.QtCore import Qt, QRect

from crop_logic.image_transform import get_crop_rect, get_display_pixmap_and_rect

def render_cropped_pixmap(crop_area, target_width=None, target_height=None):

    if crop_area.pixmap is None:
        return None

    if target_width is None:
        target_width = crop_area.crop_width
    if target_height is None:
        target_height = crop_area.crop_height

    crop_rect = get_crop_rect(crop_area)
    _, draw_rect = get_display_pixmap_and_rect(crop_area)

    if draw_rect is None or draw_rect.width() <= 0 or draw_rect.height() <= 0:
        return None

    original_width = crop_area.pixmap.width()
    original_height = crop_area.pixmap.height()

    src_x = (crop_rect.left() - draw_rect.left()) * original_width / draw_rect.width()
    src_y = (crop_rect.top() - draw_rect.top()) * original_height / draw_rect.height()
    src_w = crop_rect.width() * original_width / draw_rect.width()
    src_h = crop_rect.height() * original_height / draw_rect.height()

    src_x = max(0, int(round(src_x)))
    src_y = max(0, int(round(src_y)))
    src_w = max(1, int(round(src_w)))
    src_h = max(1, int(round(src_h)))

    if src_x + src_w > original_width:
        src_w = original_width - src_x

    if src_y + src_h > original_height:
        src_h = original_height - src_y

    if src_w <= 0 or src_h <= 0:
        return None

    source_rect = QRect(src_x, src_y, src_w, src_h)
    cropped = crop_area.pixmap.copy(source_rect)

    final_pixmap = cropped.scaled(
        target_width,
        target_height,
        Qt.IgnoreAspectRatio,
        Qt.SmoothTransformation
    )

    return final_pixmap