from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QLabel,
    QSpinBox,
    QHBoxLayout,
    QVBoxLayout,
    QComboBox,
)


def build_main_window_ui(window):

    window.central_widget = QWidget()
    window.setCentralWidget(window.central_widget)

    window.main_layout = QVBoxLayout()

    window.top_panel_layout = QHBoxLayout()

    window.open_button = QPushButton("Open")
    window.save_button = QPushButton("Save")
    window.export_set_button = QPushButton("Export as a set")
    window.configure_export_button = QPushButton("Set up export")
    window.add_editor_button = QPushButton("Add window")

    window.preset_label = QLabel("Preset:")
    window.preset_combo = QComboBox()

    window.add_preset_button = QPushButton("Add preset")
    window.rename_preset_button = QPushButton("Rename preset")
    window.update_preset_button = QPushButton("Update preset")
    window.delete_preset_button = QPushButton("Delete preset")

    window.width_label = QLabel("Width:")
    window.width_spinbox = QSpinBox()
    window.width_spinbox.setRange(1, 10000)
    window.width_spinbox.setValue(256)

    window.height_label = QLabel("Height:")
    window.height_spinbox = QSpinBox()
    window.height_spinbox.setRange(1, 10000)
    window.height_spinbox.setValue(512)

    window.apply_size_button = QPushButton("Apply size")
    window.reset_view_button = QPushButton("Reset view")

    window.top_panel_layout.addWidget(window.open_button)
    window.top_panel_layout.addWidget(window.save_button)
    window.top_panel_layout.addWidget(window.export_set_button)
    window.top_panel_layout.addWidget(window.configure_export_button)
    window.top_panel_layout.addWidget(window.add_editor_button)

    window.top_panel_layout.addSpacing(20)

    window.top_panel_layout.addWidget(window.preset_label)
    window.top_panel_layout.addWidget(window.preset_combo)
    window.top_panel_layout.addWidget(window.add_preset_button)
    window.top_panel_layout.addWidget(window.rename_preset_button)
    window.top_panel_layout.addWidget(window.update_preset_button)
    window.top_panel_layout.addWidget(window.delete_preset_button)

    window.top_panel_layout.addSpacing(20)

    window.top_panel_layout.addWidget(window.width_label)
    window.top_panel_layout.addWidget(window.width_spinbox)
    window.top_panel_layout.addWidget(window.height_label)
    window.top_panel_layout.addWidget(window.height_spinbox)
    window.top_panel_layout.addWidget(window.apply_size_button)

    window.top_panel_layout.addSpacing(20)
    window.top_panel_layout.addWidget(window.reset_view_button)
    window.top_panel_layout.addStretch()

    window.editors_container = QWidget()

    window.editors_outer_layout = QVBoxLayout()

    window.editors_center_layout = QHBoxLayout()

    window.editors_main_layout = QHBoxLayout()

    window.main_editor_layout = QVBoxLayout()

    window.extra_editors_layout = QVBoxLayout()

    window.editors_main_layout.addLayout(window.main_editor_layout, 2)
    window.editors_main_layout.addLayout(window.extra_editors_layout, 1)

    window.editors_center_layout.addStretch()
    window.editors_center_layout.addLayout(window.editors_main_layout, 1)
    window.editors_center_layout.addStretch()

    window.editors_outer_layout.addStretch()
    window.editors_outer_layout.addLayout(window.editors_center_layout)
    window.editors_outer_layout.addStretch()

    window.editors_container.setLayout(window.editors_outer_layout)

    window.status_label = QLabel(
        "Done. You can open a single image and edit it in multiple windows"
    )
    window.status_label.setStyleSheet("""
        color: #444444;
        padding: 6px;
    """)

    # Сборка общего интерфейса
    window.main_layout.addLayout(window.top_panel_layout)
    window.main_layout.addWidget(window.editors_container)
    window.main_layout.addWidget(window.status_label)

    window.central_widget.setLayout(window.main_layout)