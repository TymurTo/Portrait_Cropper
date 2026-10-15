from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QMouseEvent, QWheelEvent, QPixmap

from app_constants import (
    DEFAULT_CROP_WIDTH,
    DEFAULT_CROP_HEIGHT,
    MAX_SCALE,
)
from crop_logic.image_transform import (
    get_crop_rect,
    get_base_fitted_size,
    get_min_scale_for_crop,
    get_display_pixmap_and_rect,
    clamp_offsets,
    ensure_image_covers_crop,
)
from crop_logic.crop_render import render_cropped_pixmap
from crop_logic.crop_paint import paint_crop_area


class CropArea(QWidget):

    def __init__(self):
        super().__init__()

        self.pixmap = None

        self.crop_width = DEFAULT_CROP_WIDTH
        self.crop_height = DEFAULT_CROP_HEIGHT

        self.offset_x = 0.0
        self.offset_y = 0.0

        self.scale_factor = 1.0

        self.max_scale = MAX_SCALE

        self.dragging = False

        self.last_mouse_pos = QPointF()

        self.setMinimumSize(500, 350)

        self.setStyleSheet("background-color: #2b2b2b;")

        self.setMouseTracking(True)

    def load_image(self, file_path: str) -> bool:

        pixmap = QPixmap(file_path)

        if pixmap.isNull():
            return False

        self.pixmap = pixmap

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale_factor = 1.0

        self.ensure_image_covers_crop()

        self.update()

        return True

    def clear_image(self):

        self.pixmap = None
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale_factor = 1.0
        self.update()

    def set_crop_size(self, width: int, height: int):

        if width <= 0 or height <= 0:
            return

        self.crop_width = width
        self.crop_height = height

        self.ensure_image_covers_crop()
        self.update()

    def reset_view(self):

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale_factor = 1.0

        self.ensure_image_covers_crop()
        self.update()


    get_crop_rect = get_crop_rect
    get_base_fitted_size = get_base_fitted_size
    get_min_scale_for_crop = get_min_scale_for_crop
    get_display_pixmap_and_rect = get_display_pixmap_and_rect
    clamp_offsets = clamp_offsets
    ensure_image_covers_crop = ensure_image_covers_crop
    render_cropped_pixmap = render_cropped_pixmap

    def resizeEvent(self, event):

        super().resizeEvent(event)

        if self.pixmap is not None:
            self.ensure_image_covers_crop()

    def paintEvent(self, event):

        paint_crop_area(self, event)

    def mousePressEvent(self, event: QMouseEvent):

        if event.button() == Qt.LeftButton and self.pixmap is not None:
            self.dragging = True
            self.last_mouse_pos = event.position()

            # Меняем курсор на "сжатую руку".
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event: QMouseEvent):

        if self.dragging and self.pixmap is not None:
            current_pos = event.position()
            delta = current_pos - self.last_mouse_pos

            self.offset_x += delta.x()
            self.offset_y += delta.y()

            self.last_mouse_pos = current_pos

            self.clamp_offsets()

            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):

        if event.button() == Qt.LeftButton:
            self.dragging = False

            # Возвращаем обычный курсор.
            self.setCursor(Qt.ArrowCursor)

    def wheelEvent(self, event: QWheelEvent):

        if self.pixmap is None:
            return

        _, old_draw_rect = self.get_display_pixmap_and_rect()

        if old_draw_rect is None or old_draw_rect.width() <= 0 or old_draw_rect.height() <= 0:
            return

        cursor_pos = event.position()

        rel_x = (cursor_pos.x() - old_draw_rect.left()) / old_draw_rect.width()
        rel_y = (cursor_pos.y() - old_draw_rect.top()) / old_draw_rect.height()

        delta = event.angleDelta().y()
        zoom_step = 1.1

        old_scale = self.scale_factor

        if delta > 0:
            new_scale = self.scale_factor * zoom_step
        else:
            new_scale = self.scale_factor / zoom_step

        min_scale = self.get_min_scale_for_crop()
        new_scale = max(min_scale, min(self.max_scale, new_scale))

        if new_scale == old_scale:
            return

        self.scale_factor = new_scale

        _, new_draw_rect = self.get_display_pixmap_and_rect()
        if new_draw_rect is None:
            return

        desired_left = cursor_pos.x() - rel_x * new_draw_rect.width()
        desired_top = cursor_pos.y() - rel_y * new_draw_rect.height()

        base_left = new_draw_rect.left() - self.offset_x
        base_top = new_draw_rect.top() - self.offset_y

        self.offset_x = desired_left - base_left
        self.offset_y = desired_top - base_top

        self.clamp_offsets()

        self.update()