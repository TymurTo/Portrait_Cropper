# Portrait Cropper

A desktop app built with **Python + PySide6 (Qt)** for quickly cutting a single image into portraits of different sizes. Open an image once, move and zoom it in several windows, each with its own preset (for example full-length, medium and small portrait), and save the results.

Originally made for Pathfinder portrait sizes (see the built-in presets), but it works for any fixed aspect ratio.

## Features

- Open images: `png`, `jpg`, `jpeg`, `bmp`, `webp`, via a file dialog or by dragging and dropping into the window.
- Crop frame with a rule-of-thirds grid and a size label.
- Drag the image with the left mouse button, zoom with the mouse wheel **towards the cursor position**.
  The image always covers the frame, so the result never has empty margins.
- Up to **3 editor windows** at once (one main and two additional), each with its own preset.
- Size presets: built-in (read-only) and user-defined (add, rename, update size, delete).
- Save the main window's result as PNG or JPEG.
- "Export as a set" saves the results of all windows at once.
- Remembers the last used folder.

## Installation and launch

Requires Python 3.9+.

```bash
git clone <repository-url>
cd Portrait_Cropper

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

pip install PySide6
python main.py
```

## Usage

1. Click **Open** (or drag a file into the window). The image is loaded into all open windows.
2. Choose a preset from the window's dropdown, or set **Width / Height** and click **Apply size**.
3. Mouse wheel zooms, left button pans. **Reset view** restores the initial position and scale.
4. **Add window** adds another window with a different frame size (3 windows maximum); **✖** closes an additional window.
5. **Save** saves the main window's result, **Export as a set** saves the results of all windows. Files are named
   `<name>_panel<N>_<width>x<height>.png`; if a file already exists, a suffix `_1`, `_2`, etc. is added.

### Presets

| Button          | Action                                                           |
|-----------------|------------------------------------------------------------------|
| Add preset      | Creates a preset from the current Width / Height values          |
| Rename preset   | Renames a user-defined preset                                    |
| Update preset   | Writes the current Width / Height into a user-defined preset     |
| Delete preset   | Deletes a user-defined preset (with confirmation)                |
| Set up export   | Dialog with `export_enabled` checkboxes for presets              |

Built-in presets (`user_defined: false`) are protected from modification and deletion.

## Configuration files

Both files are created automatically on first launch and are stored **in the current working directory** (run the app from the project folder).

- `presets.json`: the preset list with `name`, `width`, `height`, `export_enabled`, `user_defined`.
  If the file is corrupted or empty, the defaults from `presets/preset_defaults.py` are restored.
- `app_settings.json`: user settings (currently only `last_used_dir`).

## Project structure

```
Portrait_Cropper/
├── main.py                  # entry point
├── app_constants.py         # constants: window size, zoom limit, settings file names
├── app_settings.py          # loading/saving app_settings.json
├── crop_area.py             # CropArea widget: mouse events, zoom, state
├── crop_logic/
│   ├── image_transform.py   # geometry: frame, scale, offset limits
│   ├── crop_paint.py        # painting: image, dimming overlay, grid, labels
│   └── crop_render.py       # cutting out the final QPixmap of the target size
├── presets/
│   ├── preset_defaults.py   # built-in presets
│   ├── preset_storage.py    # loading/saving presets.json
│   └── preset_utils.py      # preset validation, safe file names
├── dialogs/
│   └── export_presets_dialog.py  # export configuration dialog
└── ui/
    ├── main_window.py           # main window, drag-and-drop, editor window management
    ├── main_window_ui.py        # UI construction (top bar, containers)
    ├── main_window_files.py     # open, save, export
    ├── main_window_presets.py   # preset operations
    └── editor_panel.py          # editor panel: title, preset selector, CropArea
```

### How it works

- `CropArea` holds the state: the source `QPixmap`, the scale (`scale_factor`) and the offset (`offset_x`, `offset_y`).
- `crop_logic` is a set of functions that take a `CropArea` and compute geometry. The crop frame is fitted into the widget with a `CROP_MARGIN` margin and keeps the preset's aspect ratio.
- The minimum zoom is calculated so that the image always fully covers the frame; the maximum is set by `MAX_SCALE`.
- On save, the area under the frame is converted to coordinates of the original image, cut out, and scaled to the preset size.

## Known limitations

- "Export as a set" saves results per **open window**, not per preset with the `export_enabled` flag. The "Set up export" dialog does not affect export yet.
- EXIF auto-rotation is not applied: photos from a phone may open rotated.
- An additional window added **after** an image has been loaded stays empty until the file is opened again.
- Zooming and dragging may be slow on very large images.
- There are no automated tests.

## Tech stack

- Python 3.9+
- [PySide6](https://doc.qt.io/qtforpython-6/) (Qt for Python)
