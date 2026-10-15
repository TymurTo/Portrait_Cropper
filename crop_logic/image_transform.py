from PySide6.QtCore import Qt, QRectF

from app_constants import CROP_MARGIN

def get_crop_rect(crop_area) -> QRectF:

    widget_width = crop_area.width()
    widget_height = crop_area.height()

    margin = CROP_MARGIN

    available_width = max(1, widget_width - margin * 2)
    available_height = max(1, widget_height - margin * 2)

    aspect_ratio = crop_area.crop_width / crop_area.crop_height

    rect_width = available_width
    rect_height = rect_width / aspect_ratio

    if rect_height > available_height:
        rect_height = available_height
        rect_width = rect_height * aspect_ratio

    x = (widget_width - rect_width) / 2
    y = (widget_height - rect_height) / 2

    return QRectF(x, y, rect_width, rect_height)


def get_base_fitted_size(crop_area):

    if crop_area.pixmap is None:
        return 0, 0

    area_width = crop_area.width()
    area_height = crop_area.height()

    base_pixmap = crop_area.pixmap.scaled(
        area_width,
        area_height,
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation
    )

    return base_pixmap.width(), base_pixmap.height()


def get_min_scale_for_crop(crop_area) -> float:

    if crop_area.pixmap is None:
        return 1.0

    base_w, base_h = get_base_fitted_size(crop_area)
    crop_rect = get_crop_rect(crop_area)

    if base_w <= 0 or base_h <= 0:
        return 1.0

    scale_x = crop_rect.width() / base_w
    scale_y = crop_rect.height() / base_h

    min_scale = max(scale_x, scale_y)
    return max(0.0001, min_scale)


def get_display_pixmap_and_rect(crop_area):

    if crop_area.pixmap is None:
        return None, None

    area_width = crop_area.width()
    area_height = crop_area.height()

    base_pixmap = crop_area.pixmap.scaled(
        area_width,
        area_height,
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation
    )

    scaled_width = max(1, int(base_pixmap.width() * crop_area.scale_factor))
    scaled_height = max(1, int(base_pixmap.height() * crop_area.scale_factor))

    scaled_pixmap = base_pixmap.scaled(
        scaled_width,
        scaled_height,
        Qt.IgnoreAspectRatio,
        Qt.SmoothTransformation
    )

    base_x = (area_width - scaled_pixmap.width()) / 2
    base_y = (area_height - scaled_pixmap.height()) / 2

    x = base_x + crop_area.offset_x
    y = base_y + crop_area.offset_y

    draw_rect = QRectF(
        x,
        y,
        scaled_pixmap.width(),
        scaled_pixmap.height()
    )

    return scaled_pixmap, draw_rect


def clamp_offsets(crop_area):

    if crop_area.pixmap is None:
        return

    _, draw_rect = get_display_pixmap_and_rect(crop_area)
    crop_rect = get_crop_rect(crop_area)

    if draw_rect is None:
        return

    if draw_rect.width() <= crop_rect.width():
        ideal_x = crop_rect.center().x() - draw_rect.width() / 2
        area_width = crop_area.width()
        base_x = (area_width - draw_rect.width()) / 2
        crop_area.offset_x = ideal_x - base_x
    else:
        if draw_rect.left() > crop_rect.left():
            crop_area.offset_x -= (draw_rect.left() - crop_rect.left())

        if draw_rect.right() < crop_rect.right():
            crop_area.offset_x += (crop_rect.right() - draw_rect.right())

    _, draw_rect = get_display_pixmap_and_rect(crop_area)

    if draw_rect.height() <= crop_rect.height():
        ideal_y = crop_rect.center().y() - draw_rect.height() / 2
        area_height = crop_area.height()
        base_y = (area_height - draw_rect.height()) / 2
        crop_area.offset_y = ideal_y - base_y
    else:
        if draw_rect.top() > crop_rect.top():
            crop_area.offset_y -= (draw_rect.top() - crop_rect.top())

        if draw_rect.bottom() < crop_rect.bottom():
            crop_area.offset_y += (crop_rect.bottom() - draw_rect.bottom())


def ensure_image_covers_crop(crop_area):

    if crop_area.pixmap is None:
        return

    min_scale = get_min_scale_for_crop(crop_area)

    if crop_area.scale_factor < min_scale:
        crop_area.scale_factor = min_scale

    if crop_area.scale_factor > crop_area.max_scale:
        crop_area.scale_factor = crop_area.max_scale

    clamp_offsets(crop_area)