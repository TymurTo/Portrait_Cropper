from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtCore import Qt

from app_constants import (
    APP_TITLE,
    DEFAULT_WINDOW_WIDTH,
    DEFAULT_WINDOW_HEIGHT,
)
from app_settings import load_settings, save_settings
from presets.preset_storage import load_presets, save_presets
from ui.main_window_ui import build_main_window_ui
from ui.main_window_presets import (
    refresh_preset_combo,
    get_selected_preset,
    get_selected_preset_with_index,
    on_preset_selected,
    add_preset_from_fields,
    rename_selected_preset,
    update_selected_preset_from_fields,
    delete_selected_preset,
    configure_export_presets,
    sync_top_controls,
)
from ui.main_window_files import (
    open_image,
    save_result,
    export_multiple_sizes,
    get_default_single_save_name,
    get_default_export_set_name,
)
from ui.editor_panel import EditorPanel


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.presets = load_presets()
        self.app_settings = load_settings()

        self.editor_panels = []

        self.setWindowTitle(APP_TITLE)
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)

        build_main_window_ui(self)

        self.connect_signals()

        self.refresh_preset_combo()

        self.setAcceptDrops(True)

        self.create_main_editor()

    def connect_signals(self):

        self.open_button.clicked.connect(self.open_image)
        self.save_button.clicked.connect(self.save_result)
        self.export_set_button.clicked.connect(self.export_multiple_sizes)
        self.configure_export_button.clicked.connect(self.configure_export_presets)

        self.apply_size_button.clicked.connect(self.apply_size)
        self.reset_view_button.clicked.connect(self.reset_view)

        self.preset_combo.currentIndexChanged.connect(self.on_preset_selected)
        self.add_preset_button.clicked.connect(self.add_preset_from_fields)
        self.rename_preset_button.clicked.connect(self.rename_selected_preset)
        self.update_preset_button.clicked.connect(self.update_selected_preset_from_fields)
        self.delete_preset_button.clicked.connect(self.delete_selected_preset)

        self.add_editor_button.clicked.connect(self.add_editor)

    def persist_presets(self):

        save_presets(self.presets)

    def persist_settings(self):

        try:
            save_settings(self.app_settings)
        except OSError:
            QMessageBox.critical(
                self,
                "Error saving settings",
                "Failed to save app_settings.json."
            )

    def get_last_used_dir(self) -> str:

        path = self.app_settings.get("last_used_dir", "")

        if isinstance(path, str) and path:
            import os
            if os.path.isdir(path):
                return path

        return ""

    def set_last_used_dir_from_path(self, file_path: str):

        if not file_path:
            return

        import os

        directory = os.path.dirname(file_path)
        if directory and os.path.isdir(directory):
            self.app_settings["last_used_dir"] = directory
            self.persist_settings()

    def create_main_editor(self):

        panel = EditorPanel("Basic", self.presets, is_main=True)

        # Делаем основную панель визуально крупнее
        panel.setMinimumWidth(520)
        panel.setMinimumHeight(520)

        # Выбор в комбобоксе главной панели -> обновить верхние контролы
        panel.selection_changed.connect(self.sync_top_controls)

        self.editor_panels.append(panel)
        self.main_editor_layout.addWidget(panel)

        self.sync_top_controls()

    def add_editor(self):

        if len(self.editor_panels) >= 3:
            self.status_label.setText("Maximum of 3 editor windows")
            return

        extra_number = len(self.editor_panels)  # 1 -> Доп. 1, 2 -> Доп. 2
        panel = EditorPanel(f"Доп. {extra_number}", self.presets, is_main=False)

        panel.setMinimumWidth(300)
        panel.setMinimumHeight(240)
        panel.setMaximumWidth(420)

        panel.remove_button.clicked.connect(
            lambda _=None, p=panel: self.remove_editor(p)
        )

        # Новое окно получает тот же пресет/размер и то же изображение,
        # что и главное
        if self.editor_panels:
            main_panel = self.editor_panels[0]
            panel.copy_selection_from(main_panel)

            image_path = main_panel.crop_area.image_path
            if image_path:
                panel.crop_area.load_image(image_path)

        self.editor_panels.append(panel)
        self.extra_editors_layout.addWidget(panel)

    def remove_editor(self, panel):

        if panel not in self.editor_panels:
            return

        self.editor_panels.remove(panel)
        panel.setParent(None)
        panel.deleteLater()

        self.status_label.setText("Additional window removed")

    def apply_size(self):

        width = self.width_spinbox.value()
        height = self.height_spinbox.value()

        if self.editor_panels:
            self.editor_panels[0].set_custom_size(width, height)
            self.sync_top_controls()

        self.status_label.setText(
            f"A new frame aspect ratio has been applied: {width} x {height}"
        )

    def reset_view(self):

        for panel in self.editor_panels:
            panel.crop_area.reset_view()

        self.status_label.setText("Image position and scale have been reset in all windows")

    def _extract_first_local_image_from_mime(self, mime_data):

        if not mime_data.hasUrls():
            return None

        image_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}

        for url in mime_data.urls():
            if not url.isLocalFile():
                continue

            local_path = url.toLocalFile()

            import os
            _, ext = os.path.splitext(local_path)

            if ext.lower() in image_extensions:
                return local_path

        return None

    def dragEnterEvent(self, event):

        file_path = self._extract_first_local_image_from_mime(event.mimeData())

        if file_path is not None:
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):

        file_path = self._extract_first_local_image_from_mime(event.mimeData())

        if file_path is not None:
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):

        file_path = self._extract_first_local_image_from_mime(event.mimeData())

        if file_path is None:
            event.ignore()
            return

        success_any = False

        for panel in self.editor_panels:
            success = panel.crop_area.load_image(file_path)
            success_any = success_any or success

        if success_any:
            self.set_last_used_dir_from_path(file_path)
            self.status_label.setText(f"Image uploaded via drag-and-drop: {file_path}")
            event.acceptProposedAction()
        else:
            QMessageBox.critical(
                self,
                "Error",
                "Failed to load the dragged image"
            )
            self.status_label.setText("Error loading the dragged-and-dropped image")
            event.ignore()

    refresh_preset_combo = refresh_preset_combo
    get_selected_preset = get_selected_preset
    get_selected_preset_with_index = get_selected_preset_with_index
    on_preset_selected = on_preset_selected
    add_preset_from_fields = add_preset_from_fields
    rename_selected_preset = rename_selected_preset
    update_selected_preset_from_fields = update_selected_preset_from_fields
    delete_selected_preset = delete_selected_preset
    configure_export_presets = configure_export_presets
    sync_top_controls = sync_top_controls

    open_image = open_image
    save_result = save_result
    export_multiple_sizes = export_multiple_sizes
    get_default_single_save_name = get_default_single_save_name
    get_default_export_set_name = get_default_export_set_name