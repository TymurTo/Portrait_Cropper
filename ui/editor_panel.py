from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton
)

from crop_area import CropArea


class EditorPanel(QWidget):

    def __init__(self, title: str, presets: list, is_main=False):
        super().__init__()

        self.presets = presets
        self.is_main = is_main

        self.layout = QVBoxLayout()
        self.top_bar = QHBoxLayout()

        self.title_label = QLabel(title)
        self.preset_combo = QComboBox()
        self.remove_button = QPushButton("✖")
        self.remove_button.setVisible(not is_main)

        self.top_bar.addWidget(self.title_label)
        self.top_bar.addStretch()
        self.top_bar.addWidget(self.preset_combo)
        self.top_bar.addWidget(self.remove_button)

        self.crop_area = CropArea()

        self.layout.addLayout(self.top_bar)
        self.layout.addWidget(self.crop_area)
        self.setLayout(self.layout)

        if is_main:
            self.setMinimumWidth(520)
        else:
            self.setMinimumWidth(300)
            self.setMaximumWidth(420)

        self.refresh_presets()

        if self.presets:
            self.preset_combo.setCurrentIndex(0)
            self.apply_selected_preset()

    def refresh_presets(self):

        current_index = self.preset_combo.currentIndex()

        self.preset_combo.blockSignals(True)
        self.preset_combo.clear()

        for preset in self.presets:
            label = f"{preset['name']} ({preset['width']}x{preset['height']})"
            self.preset_combo.addItem(label)

        if self.presets:
            if 0 <= current_index < len(self.presets):
                self.preset_combo.setCurrentIndex(current_index)
            else:
                self.preset_combo.setCurrentIndex(0)

        self.preset_combo.blockSignals(False)

    def apply_selected_preset(self):

        index = self.preset_combo.currentIndex()
        if index < 0 or index >= len(self.presets):
            return

        preset = self.presets[index]

        self.crop_area.set_crop_size(
            preset["width"],
            preset["height"]
        )