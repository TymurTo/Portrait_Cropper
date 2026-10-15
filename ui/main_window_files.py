import os

from PySide6.QtWidgets import QFileDialog, QMessageBox

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

    preset = self.get_selected_preset()
    extension = ".png" if "png" in selected_filter.lower() else ".jpg"

    if preset is not None:
        preset_name = make_safe_filename_part(preset["name"])
        return f"portrait_set_{preset_name}{extension}"

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

    panels_with_image = [
        panel for panel in self.editor_panels
        if panel.crop_area.pixmap is not None
    ]

    if not panels_with_image:
        QMessageBox.warning(
            self,
            "No image",
            "First, upload an image"
        )
        self.status_label.setText("Export is not possible: the image has not been loaded")
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

    for i, panel in enumerate(self.editor_panels):
        crop = panel.crop_area

        if crop.pixmap is None:
            continue

        width = crop.crop_width
        height = crop.crop_height

        result_pixmap = crop.render_cropped_pixmap(width, height)

        if result_pixmap is None:
            continue

        export_path = f"{base_path}_panel{i + 1}_{width}x{height}{extension}"

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
