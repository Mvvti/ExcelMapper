# Zamowienia

Zamowienia is a desktop application built with Python + pywebview for converting order documents into output Excel files.

## Features

- Excel mode: processes order workbook + price list + facility list + template.
- PDF mode: parses one or multiple PDF orders and generates one combined Excel file.
- Input validation in the UI before running the pipeline.
- Live logs and status indicators for both modes.

## Requirements

- Windows
- Python 3.12
- Dependencies installed in `.venv`

## Run Locally

```bat
.venv\Scripts\python.exe gui_app.py
```

## Build EXE (PyInstaller, onedir)

```bat
build.bat
```

After build, the executable is available at:

```text
dist\Zamowienia\Zamowienia.exe
```

## Project Structure

- `gui_app.py` - desktop entry point and JS API bridge.
- `frontend/` - UI (HTML/CSS/JS).
- `src/` - processing pipelines (Excel + PDF).
- `app.spec` - PyInstaller configuration.
- `build.bat` - one-command build script.

## Notes

- The app does not include customer data files in the repository.
- Provide your own input files (Excel/PDF) and output folder when running.