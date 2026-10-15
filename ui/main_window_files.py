import os

from PySide6.QtWidgets import QFileDialog, QMessageBox

from presets.preset_utils import make_safe_filename_part


def _make_non_conflicting_path(path: str) -> str:
    """
    Если файл уже существует, создает новый путь с суффиксом:
    _1, _2, _3 и т.д.

    Пример:
        image.png
        image_1.png
        image_2.png
    """
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
    """
    Строит имя файла по умолчанию для обычного сохранения.
    """
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
    """
    Строит базовое имя по умолчанию для пакетного экспорта.
    """
    preset = self.get_selected_preset()
    extension = ".png" if "png" in selected_filter.lower() else ".jpg"

    if preset is not None:
        preset_name = make_safe_filename_part(preset["name"])
        return f"portrait_set_{preset_name}{extension}"

    return f"portrait_set{extension}"


def open_image(self):
    """
    Открывает изображение с диска и загружает его
    во все активные панели редактора.
    """
    start_dir = self.get_last_used_dir()

    file_path, _ = QFileDialog.getOpenFileName(
        self,
        "Выберите изображение",
        start_dir,
        "Изображения (*.png *.jpg *.jpeg *.bmp *.webp)"
    )

    if not file_path:
        self.status_label.setText("Открытие отменено.")
        return

    success_any = False

    for panel in self.editor_panels:
        success = panel.crop_area.load_image(file_path)
        success_any = success_any or success

    if success_any:
        self.set_last_used_dir_from_path(file_path)
        self.status_label.setText(f"Изображение загружено: {file_path}")
    else:
        self.status_label.setText("Ошибка загрузки изображения.")
        QMessageBox.critical(self, "Ошибка", "Не удалось загрузить изображение.")


def save_result(self):
    """
    Сохраняет результат только из основной панели редактора.

    Если файл с таким именем уже существует,
    автоматически создается новое имя без перезаписи.
    """
    if not self.editor_panels:
        QMessageBox.warning(self, "Нет редактора", "Нет активных окон редактора.")
        return

    main_panel = self.editor_panels[0]
    crop_area = main_panel.crop_area

    if crop_area.pixmap is None:
        QMessageBox.warning(self, "Нет изображения", "Сначала загрузите изображение.")
        self.status_label.setText("Сохранение невозможно: изображение не загружено.")
        return

    result_pixmap = crop_area.render_cropped_pixmap()

    if result_pixmap is None:
        QMessageBox.critical(
            self,
            "Ошибка",
            "Не удалось подготовить изображение для сохранения."
        )
        self.status_label.setText("Ошибка подготовки результата.")
        return

    default_filter = "PNG (*.png)"
    default_name = self.get_default_single_save_name(default_filter)

    start_dir = self.get_last_used_dir()
    initial_path = os.path.join(start_dir, default_name) if start_dir else default_name

    file_path, selected_filter = QFileDialog.getSaveFileName(
        self,
        "Сохранить портрет",
        initial_path,
        "PNG (*.png);;JPEG (*.jpg *.jpeg)",
        default_filter
    )

    if not file_path:
        self.status_label.setText("Сохранение отменено.")
        return

    lower_path = file_path.lower()

    if "png" in selected_filter.lower() and not lower_path.endswith(".png"):
        file_path += ".png"
    elif "jpeg" in selected_filter.lower() or "jpg" in selected_filter.lower():
        if not (lower_path.endswith(".jpg") or lower_path.endswith(".jpeg")):
            file_path += ".jpg"

    # ВАЖНО: если такой файл уже есть, подбираем свободное имя
    file_path = _make_non_conflicting_path(file_path)

    success = result_pixmap.save(file_path)

    if success:
        self.set_last_used_dir_from_path(file_path)
        self.status_label.setText(f"Файл сохранен: {file_path}")
        QMessageBox.information(
            self,
            "Готово",
            f"Портрет сохранен.\n\nРазмер: {crop_area.crop_width} x {crop_area.crop_height}"
        )
    else:
        self.status_label.setText("Ошибка сохранения файла.")
        QMessageBox.critical(self, "Ошибка", "Не удалось сохранить файл.")


def export_multiple_sizes(self):
    """
    Экспортирует все активные панели редактора.

    Если файлы с такими именами уже существуют,
    автоматически создаются новые имена без перезаписи.
    """
    if not self.editor_panels:
        QMessageBox.warning(self, "Нет редакторов", "Нет активных окон редактора.")
        self.status_label.setText("Экспорт невозможен: нет активных редакторов.")
        return

    panels_with_image = [
        panel for panel in self.editor_panels
        if panel.crop_area.pixmap is not None
    ]

    if not panels_with_image:
        QMessageBox.warning(
            self,
            "Нет изображения",
            "Сначала загрузите изображение."
        )
        self.status_label.setText("Экспорт невозможен: изображение не загружено.")
        return

    default_filter = "PNG (*.png)"
    default_name = self.get_default_export_set_name(default_filter)

    start_dir = self.get_last_used_dir()
    initial_path = os.path.join(start_dir, default_name) if start_dir else default_name

    file_path, selected_filter = QFileDialog.getSaveFileName(
        self,
        "Экспорт набором",
        initial_path,
        "PNG (*.png);;JPEG (*.jpg *.jpeg)",
        default_filter
    )

    if not file_path:
        self.status_label.setText("Экспорт набором отменен.")
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

        # ВАЖНО: не перезаписываем существующий файл
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
