from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QScrollArea,
    QWidget,
    QCheckBox,
    QDialogButtonBox
)


class ExportPresetsDialog(QDialog):

    def __init__(self, presets, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Configure batch export")
        self.resize(420, 420)

        self.presets = presets
        self.checkboxes = []

        main_layout = QVBoxLayout(self)

        info_label = QLabel(
            "Select the presets that should be used\n"
            "during batch export."
        )
        main_layout.addWidget(info_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        for preset in self.presets:
            checkbox = QCheckBox(
                f"{preset['name']} ({preset['width']} x {preset['height']})"
            )
            checkbox.setChecked(preset.get("export_enabled", False))
            self.checkboxes.append((preset, checkbox))
            content_layout.addWidget(checkbox)

        content_layout.addStretch()

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

    def apply_changes(self):
        for preset, checkbox in self.checkboxes:
            preset["export_enabled"] = checkbox.isChecked()