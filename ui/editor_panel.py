from PySide6.QtCore import Signal
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
    """
    Панель редактора.

    Источник правды для размера рамки: self.selected_preset + crop_area.

    - selected_preset — это сам словарь пресета из общего списка presets
      (ссылка, а не индекс). Поэтому Rename / Update меняют тот же объект,
      а Delete легко обнаружить: объекта больше нет в списке.
    - selected_preset is None означает «Custom»: размер задан вручную
      (кнопка Apply size) и хранится только в crop_area.

    Комбобокс панели — только отображение этого состояния. Его пункт 0 —
    «Custom», пункты 1..N — пресеты.
    """

    # Испускается, когда пользователь сам выбрал пункт в комбобоксе панели
    selection_changed = Signal()

    def __init__(self, title: str, presets: list, is_main=False):
        super().__init__()

        self.presets = presets
        self.is_main = is_main
        self.selected_preset = presets[0] if presets else None

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

        self.preset_combo.currentIndexChanged.connect(self._on_combo_changed)

    # ---------- подписи ----------

    @staticmethod
    def _preset_label(preset: dict) -> str:
        return f"{preset['name']} ({preset['width']}x{preset['height']})"

    def _custom_label(self) -> str:
        if self.selected_preset is None:
            return f"Custom ({self.crop_area.crop_width}x{self.crop_area.crop_height})"
        return "Custom size"

    # ---------- состояние ----------

    def _preset_still_exists(self, preset) -> bool:
        return any(p is preset for p in self.presets)

    def refresh_presets(self):
        """
        Перестраивает комбобокс по актуальному списку пресетов и
        приводит размер рамки в соответствие с выбранным пресетом.
        Вызывается после любых изменений списка (Add / Rename / Update / Delete).
        """

        # Выбранный пресет удалили: остаёмся на текущем размере как Custom
        if self.selected_preset is not None and not self._preset_still_exists(self.selected_preset):
            self.selected_preset = None

        self.preset_combo.blockSignals(True)
        self.preset_combo.clear()
        self.preset_combo.addItem(self._custom_label())

        selected_index = 0
        for i, preset in enumerate(self.presets, start=1):
            self.preset_combo.addItem(self._preset_label(preset))
            if preset is self.selected_preset:
                selected_index = i

        self.preset_combo.setCurrentIndex(selected_index)
        self.preset_combo.blockSignals(False)

        # Размер мог измениться (Update) — применяем всегда
        if self.selected_preset is not None:
            self.crop_area.set_crop_size(
                self.selected_preset["width"],
                self.selected_preset["height"]
            )

    def select_preset(self, preset):
        """Программно выбрать пресет (или None — Custom)."""

        self.selected_preset = preset
        self.refresh_presets()

    def set_custom_size(self, width: int, height: int):
        """Задать произвольный размер: пресет не выбран."""

        self.selected_preset = None
        self.crop_area.set_crop_size(width, height)
        self.refresh_presets()

    def copy_selection_from(self, other: "EditorPanel"):
        """Повторить выбор другой панели (пресет или Custom-размер)."""

        if other.selected_preset is not None:
            self.select_preset(other.selected_preset)
        else:
            self.set_custom_size(
                other.crop_area.crop_width,
                other.crop_area.crop_height
            )

    def _on_combo_changed(self, index: int):

        if index <= 0:
            # «Custom»: размер рамки остаётся как есть
            self.selected_preset = None
        elif index - 1 < len(self.presets):
            self.selected_preset = self.presets[index - 1]
            self.crop_area.set_crop_size(
                self.selected_preset["width"],
                self.selected_preset["height"]
            )

        self.preset_combo.setItemText(0, self._custom_label())
        self.selection_changed.emit()