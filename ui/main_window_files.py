import os

from PySide6.QtWidgets import QFileDialog, QMessageBox

from crop_area import CropArea
from presets.preset_utils import make_safe_filename_part


def _make_non_conflicting_path(path: str) -> str:

    if not os.path.exists(path):
        return path

    base, ext = os.path.splitext(path)
    counter = 1

    while True:
        new_path = f"{base}_{counter}{ext}"
        if not os.path.exists(new_path):
            return new_path
        counter += 1


def _render_for_preset(source_area, width, height):
    """
    Рендерит текущее изображение главного окна под размер пресета.

    Пресеты бывают с разным соотношением сторон, поэтому просто масштабировать
    рамку главного окна нельзя (получится искажение). Вместо этого берём
    временный CropArea такого же размера, ставим в него рамку пресета и
    переносим туда ту же точку фокуса и тот же масштаб, что выбрал
    пользователь в главном окне.
    """

    _, source_draw = source_area.get_display_pixmap_and_rect()
    source_crop = source_area.get_crop_rect()

    if source_draw is None or source_draw.width() <= 0 or source_draw.height() <= 0:
        return None

    # Центр рамки в долях изображения
    focus_x = (source_crop.center().x() - source_draw.left()) / source_draw.width()
    focus_y = (source_crop.center().y() - source_draw.top()) / source_draw.height()

    temp = CropArea()
    temp.resize(source_area.size())
    temp.pixmap = source_area.pixmap
    temp.scale_factor = source_area.scale_factor
    temp.set_crop_size(width, height)

    _, draw = temp.get_display_pixmap_and_rect()
    crop = temp.get_crop_rect()

    temp.offset_x += (crop.center().x() - focus_x * draw.width()) - draw.left()
    temp.offset_y += (crop.center().y() - focus_y * draw.height()) - draw.top()
    temp.clamp_offsets()

    result = temp.render_cropped_pixmap(width, height)

    temp.deleteLater()

    return result


def get_default_single_save_name(self, selected_filter: str) -> str:

    preset = self.get_selected_preset()

    if self.editor_panels:
        width = self.editor_panels[0].crop_area.crop_width
        height = self.editor_panels[0].crop_area.crop_height
    else:
        width = self.width_spinbox.value()
        height = self.height_spinbox.value()

    extension = ".png" if "png" in selected_filter.lower() else ".jpg"

    if preset is not None:
        preset_name = make_safe_filename_part(preset["name"])
        return f"portrait_{preset_name}_{width}x{height}{extension}"

    return f"portrait_{width}x{height}{extension}"


def get_default_export_set_name(self, selected_filter: str) -> str:

    # Имя пресета добавляется к каждому файлу набора отдельно
    extension = ".png" if "png" in selected_filter.lower() else ".jpg"

    return f"portrait_set{extension}"


def open_image(self):

    start_dir = self.get_last_used_dir()

    file_path, _ = QFileDialog.getOpenFileName(
        self,
        "Select an image",
        start_dir,
        "Изображения (*.png *.jpg *.jpeg *.bmp *.webp)"
    )

    if not file_path:
        self.status_label.setText("The opening has been cancelled")
        return

    success_any = False

    for panel in self.editor_panels:
        success = panel.crop_area.load_image(file_path)
        success_any = success_any or success

    if success_any:
        self.set_last_used_dir_from_path(file_path)
        self.status_label.setText(f"Image uploaded: {file_path}")
    else:
        self.status_label.setText("Error loading image")
        QMessageBox.critical(self, "Error", "Failed to load the image")


def save_result(self):

    if not self.editor_panels:
        QMessageBox.warning(self, "No editor", "There are no active editor windows")
        return

    main_panel = self.editor_panels[0]
    crop_area = main_panel.crop_area

    if crop_area.pixmap is None:
        QMessageBox.warning(self, "No image", "First, upload an image")
        self.status_label.setText("Saving is not possible: the image has not been loaded")
        return

    result_pixmap = crop_area.render_cropped_pixmap()

    if result_pixmap is None:
        QMessageBox.critical(
            self,
            "Error",
            "Failed to prepare the image for saving"
        )
        self.status_label.setText("Error preparing the result")
        return

    default_filter = "PNG (*.png)"
    default_name = self.get_default_single_save_name(default_filter)

    start_dir = self.get_last_used_dir()
    initial_path = os.path.join(start_dir, default_name) if start_dir else default_name

    file_path, selected_filter = QFileDialog.getSaveFileName(
        self,
        "Save portrait",
        initial_path,
        "PNG (*.png);;JPEG (*.jpg *.jpeg)",
        default_filter
    )

    if not file_path:
        self.status_label.setText("Saving cancelled.")
        return

    lower_path = file_path.lower()

    if "png" in selected_filter.lower() and not lower_path.endswith(".png"):
        file_path += ".png"
    elif "jpeg" in selected_filter.lower() or "jpg" in selected_filter.lower():
        if not (lower_path.endswith(".jpg") or lower_path.endswith(".jpeg")):
            file_path += ".jpg"

    file_path = _make_non_conflicting_path(file_path)

    success = result_pixmap.save(file_path)

    if success:
        self.set_last_used_dir_from_path(file_path)
        self.status_label.setText(f"File saved: {file_path}")
        QMessageBox.information(
            self,
            "Ready",
            f"Portrait saved.\n\nSize: {crop_area.crop_width} x {crop_area.crop_height}"
        )
    else:
        self.status_label.setText("Error saving file")
        QMessageBox.critical(self, "Error", "Failed to save the file.")


def export_multiple_sizes(self):

    if not self.editor_panels:
        QMessageBox.warning(self, "No editors", "No active editor windows")
        self.status_label.setText("Export is not possible: no active editors")
        return

    source_area = self.editor_panels[0].crop_area

    if source_area.pixmap is None:
        QMessageBox.warning(
            self,
            "No image",
            "First, upload an image"
        )
        self.status_label.setText("Export is not possible: the image has not been loaded")
        return

    presets_to_export = [
        preset for preset in self.presets
        if preset.get("export_enabled", False)
    ]

    if not presets_to_export:
        QMessageBox.warning(
            self,
            "No presets selected",
            "No presets are enabled for export.\n"
            "Use \"Set up export\" to choose them."
        )
        self.status_label.setText("Export is not possible: no presets enabled")
        return

    default_filter = "PNG (*.png)"
    default_name = self.get_default_export_set_name(default_filter)

    start_dir = self.get_last_used_dir()
    initial_path = os.path.join(start_dir, default_name) if start_dir else default_name

    file_path, selected_filter = QFileDialog.getSaveFileName(
        self,
        "Export as a set",
        initial_path,
        "PNG (*.png);;JPEG (*.jpg *.jpeg)",
        default_filter
    )

    if not file_path:
        self.status_label.setText("Export as a set has been cancelled")
        return

    extension = ".png" if "png" in selected_filter.lower() else ".jpg"
    base_path, _ = os.path.splitext(file_path)

    saved_files = []

    for preset in presets_to_export:
        width = preset["width"]
        height = preset["height"]

        result_pixmap = _render_for_preset(source_area, width, height)

        if result_pixmap is None:
            continue

        preset_name = make_safe_filename_part(preset["name"])
        export_path = f"{base_path}_{preset_name}_{width}x{height}{extension}"

        export_path = _make_non_conflicting_path(export_path)

        if result_pixmap.save(export_path):
            saved_files.append(export_path)

    if saved_files:
        self.set_last_used_dir_from_path(saved_files[0])

        self.status_label.setText(f"Files exported: {len(saved_files)}")
        QMessageBox.information(
            self,
            "Ready",
            "Export via set is complete\n\n" + "\n".join(saved_files)
        )
    else:
        self.status_label.setText("Failed to export the set of files")
        QMessageBox.critical(self, "Error", "Failed to export files")
