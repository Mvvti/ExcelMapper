# ExcelMapper

Desktopowa aplikacja Python + pywebview do przetwarzania zamówień Excel i generowania pliku wynikowego.

## Wymagania

- Windows
- Python 3.12
- Zależności zainstalowane w `.venv`

## Uruchomienie lokalne

```bat
.venv\Scripts\python.exe gui_app.py
```

## Build EXE (PyInstaller, onedir)

```bat
build.bat
```

Po buildzie aplikacja jest dostępna pod:

```text
dist\ExcelMapper\ExcelMapper.exe
```

## Struktura

- `gui_app.py` - backend i API dla frontendu
- `frontend/` - UI (HTML/CSS/JS)
- `src/` - pipeline przetwarzania danych
- `app.spec` - konfiguracja PyInstaller
- `hooks/hook_base_path.py` - runtime hook dla ścieżki bazowej
