from PySide6.QtWidgets import QMessageBox, QInputDialog, QDialog

from dialogs.export_presets_dialog import ExportPresetsDialog


def _refresh_all_editor_panel_presets(self):

    # Каждая панель помнит выбранный пресет по ссылке, так что после
    # Rename / Update / Delete она сама находит свой пресет (или становится
    # Custom, если его удалили) и заново применяет размер рамки.
    for panel in self.editor_panels:
        panel.refresh_presets()


def sync_top_controls(self):
    """
    Приводит верхний комбобокс и спинбоксы в соответствие с главной панелью.
    Источник правды — editor_panels[0] (selected_preset + crop_area).
    """

    if not self.editor_panels:
        return

    main_panel = self.editor_panels[0]

    index = 0
    if main_panel.selected_preset is not None:
        for i, preset in enumerate(self.presets, start=1):
            if preset is main_panel.selected_preset:
                index = i
                break

    widgets = (self.preset_combo, self.width_spinbox, self.height_spinbox)

    for widget in widgets:
        widget.blockSignals(True)

    self.preset_combo.setCurrentIndex(index)
    self.width_spinbox.setValue(main_panel.crop_area.crop_width)
    self.height_spinbox.setValue(main_panel.crop_area.crop_height)

    for widget in widgets:
        widget.blockSignals(False)


def refresh_preset_combo(self):

    self.preset_combo.blockSignals(True)

    self.preset_combo.clear()
    self.preset_combo.addItem("Select a preset")

    for preset in self.presets:
        label = f"{preset['name']} ({preset['width']} x {preset['height']})"
        self.preset_combo.addItem(label)

    self.preset_combo.blockSignals(False)

    _refresh_all_editor_panel_presets(self)

    self.sync_top_controls()


def get_selected_preset(self):

    index = self.preset_combo.currentIndex()

    if index <= 0:
        return None

    return self.presets[index - 1]


def get_selected_preset_with_index(self):

    combo_index = self.preset_combo.currentIndex()

    if combo_index <= 0:
        return None, None

    list_index = combo_index - 1
    return list_index, self.presets[list_index]


def on_preset_selected(self, index: int):

    if not self.editor_panels:
        return

    if index <= 0:
        # «Select a preset» — не выбор; возвращаем комбобокс к реальному состоянию
        self.sync_top_controls()
        return

    preset = self.presets[index - 1]

    width = preset["width"]
    height = preset["height"]

    self.editor_panels[0].select_preset(preset)
    self.sync_top_controls()

    self.status_label.setText(
        f"Preset applied: {preset['name']} ({width} x {height})"
    )


def add_preset_from_fields(self):

    width = self.width_spinbox.value()
    height = self.height_spinbox.value()

    default_name = f"My preset {width} x {height}"

    name, ok = QInputDialog.getText(
        self,
        "New preset",
        "Enter a name for the new preset:",
        text=default_name
    )

    if not ok:
        self.status_label.setText("Adding the preset has been canceled")
        return

    name = name.strip()

    if not name:
        QMessageBox.warning(
            self,
            "Empty name",
            "Preset name cannot be empty"
        )
        return

    lower_names = [preset["name"].lower() for preset in self.presets]
    if name.lower() in lower_names:
        QMessageBox.warning(
            self,
            "Duplicate name",
            "A preset with this name already exists"
        )
        return

    new_preset = {
        "name": name,
        "width": width,
        "height": height,
        "export_enabled": False,
        "user_defined": True,
    }

    self.presets.append(new_preset)
    self.persist_presets()

    if self.editor_panels:
        self.editor_panels[0].selected_preset = new_preset

    self.refresh_preset_combo()

    self.status_label.setText(
        f"New preset added: {name} ({width} x {height})"
    )


def rename_selected_preset(self):

    index, preset = self.get_selected_preset_with_index()

    if preset is None:
        QMessageBox.information(
            self,
            "No choice",
            "First, select the preset you want to rename"
        )
        return

    if not preset.get("user_defined", False):
        QMessageBox.information(
            self,
            "Cannot be renamed",
            "Built-in presets cannot be renamed.\n"
            "You can only rename items that were created manually"
        )
        return

    old_name = preset["name"]

    new_name, ok = QInputDialog.getText(
        self,
        "Rename preset",
        "Enter a new preset name:",
        text=old_name
    )

    if not ok:
        self.status_label.setText("Preset renaming cancelled")
        return

    new_name = new_name.strip()

    if not new_name:
        QMessageBox.warning(
            self,
            "Empty name",
            "Preset name cannot be empty"
        )
        return

    for i, other_preset in enumerate(self.presets):
        if i != index and other_preset["name"].lower() == new_name.lower():
            QMessageBox.warning(
                self,
                "Duplicate name",
                "A preset with this name already exists"
            )
            return

    preset["name"] = new_name

    self.persist_presets()
    self.refresh_preset_combo()

    self.status_label.setText(
        f"Preset renamed: {old_name} → {new_name}"
    )


def update_selected_preset_from_fields(self):

    index, preset = self.get_selected_preset_with_index()

    if preset is None:
        QMessageBox.information(
            self,
            "No choice",
            "First, select the preset you want to update"
        )
        return

    if not preset.get("user_defined", False):
        QMessageBox.information(
            self,
            "Cannot update",
            "Built-in presets cannot be modified.\n"
            "Only manually created items can be updated"
        )
        return

    new_width = self.width_spinbox.value()
    new_height = self.height_spinbox.value()

    if new_width <= 0 or new_height <= 0:
        QMessageBox.warning(
            self,
            "Incorrect size",
            "Width and height must be greater than zero"
        )
        return

    old_width = preset["width"]
    old_height = preset["height"]

    preset["width"] = new_width
    preset["height"] = new_height

    self.persist_presets()

    # Все панели, где выбран этот пресет, получат новый размер
    self.refresh_preset_combo()

    self.status_label.setText(
        f"Preset '{preset['name']}' updated: "
        f"{old_width}x{old_height} → {new_width}x{new_height}"
    )


def delete_selected_preset(self):

    index = self.preset_combo.currentIndex()

    if index <= 0:
        QMessageBox.information(
            self,
            "No choice",
            "First, select the preset you want to delete"
        )
        return

    preset = self.presets[index - 1]

    if not preset.get("user_defined", False):
        QMessageBox.information(
            self,
            "Cannot be deleted",
            "Built-in presets cannot be deleted.\n"
            "Only those created manually can be deleted"
        )
        return

    answer = QMessageBox.question(
        self,
        "Confirm deletion",
        f"Delete preset '{preset['name']}'?"
    )

    if answer != QMessageBox.Yes:
        self.status_label.setText("Preset deletion canceled")
        return

    del self.presets[index - 1]

    self.persist_presets()

    # Панели, где был выбран удалённый пресет, станут Custom
    # с текущим размером рамки
    self.refresh_preset_combo()

    self.status_label.setText("Custom preset deleted")


def configure_export_presets(self):

    dialog = ExportPresetsDialog(self.presets, self)

    result = dialog.exec()

    if result == QDialog.Accepted:
        dialog.apply_changes()
        self.persist_presets()

        enabled_count = sum(
            1 for preset in self.presets if preset.get("export_enabled", False)
        )

        self.status_label.setText(
            f"Export settings updated. Active presets: {enabled_count}"
        )
    else:
        self.status_label.setText("Export configuration cancelled")