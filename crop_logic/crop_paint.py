from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPen

from crop_logic.image_transform import get_crop_rect, get_display_pixmap_and_rect, get_min_scale_for_crop

def paint_crop_area(crop_area, event):

    painter = QPainter(crop_area)

    painter.fillRect(crop_area.rect(), QColor("#2b2b2b"))

    if crop_area.pixmap is None:
        painter.setPen(QColor("#dddddd"))
        painter.drawText(
            crop_area.rect(),
            Qt.AlignCenter,
            "Upload an image\n\n"
            "Mouse wheel — zoom to cursor\n"
            "Left mouse button — dragging"
        )
    else:
        scaled_pixmap, draw_rect = get_display_pixmap_and_rect(crop_area)
        painter.drawPixmap(
            int(draw_rect.x()),
            int(draw_rect.y()),
            scaled_pixmap
        )

    crop_rect = get_crop_rect(crop_area)

    overlay_color = QColor(0, 0, 0, 120)

    painter.fillRect(0, 0, crop_area.width(), int(crop_rect.top()), overlay_color)
    painter.fillRect(
        0,
        int(crop_rect.bottom()),
        crop_area.width(),
        crop_area.height() - int(crop_rect.bottom()),
        overlay_color
    )
    painter.fillRect(
        0,
        int(crop_rect.top()),
        int(crop_rect.left()),
        int(crop_rect.height()),
        overlay_color
    )
    painter.fillRect(
        int(crop_rect.right()),
        int(crop_rect.top()),
        crop_area.width() - int(crop_rect.right()),
        int(crop_rect.height()),
        overlay_color
    )

    pen = QPen(QColor("#ffffff"))
    pen.setWidth(2)
    painter.setPen(pen)
    painter.drawRect(crop_rect)

    grid_pen = QPen(QColor(255, 255, 255, 120))
    grid_pen.setWidth(1)
    painter.setPen(grid_pen)

    x1 = crop_rect.left() + crop_rect.width() / 3
    x2 = crop_rect.left() + crop_rect.width() * 2 / 3
    y1 = crop_rect.top() + crop_rect.height() / 3
    y2 = crop_rect.top() + crop_rect.height() * 2 / 3

    painter.drawLine(int(x1), int(crop_rect.top()), int(x1), int(crop_rect.bottom()))
    painter.drawLine(int(x2), int(crop_rect.top()), int(x2), int(crop_rect.bottom()))
    painter.drawLine(int(crop_rect.left()), int(y1), int(crop_rect.right()), int(y1))
    painter.drawLine(int(crop_rect.left()), int(y2), int(crop_rect.right()), int(y2))

    painter.setPen(QColor("#ffffff"))

    size_text = f"{crop_area.crop_width} x {crop_area.crop_height}"
    size_rect = QRectF(crop_rect.left(), crop_rect.top() - 30, crop_rect.width(), 20)
    painter.drawText(size_rect, Qt.AlignCenter, size_text)

    if crop_area.pixmap is not None:
        zoom_text = f"Zoom: {crop_area.scale_factor:.2f}x"
        zoom_rect = QRectF(10, 10, 180, 25)
        painter.drawText(zoom_rect, Qt.AlignLeft | Qt.AlignVCenter, zoom_text)

        min_scale_text = f"Min zoom: {get_min_scale_for_crop(crop_area):.2f}x"
        min_zoom_rect = QRectF(10, 35, 220, 25)
        painter.drawText(min_zoom_rect, Qt.AlignLeft | Qt.AlignVCenter, min_scale_text)

    painter.setPen(QColor("#555555"))
    painter.drawRect(crop_area.rect().adjusted(0, 0, -1, -1))