@echo off
setlocal

set "PYTHON_EXE=.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    echo.
    echo Nie znaleziono .venv\Scripts\python.exe
    echo Utworz/uzupelnij virtualenv i zainstaluj zaleznosci.
    exit /b 1
)

"%PYTHON_EXE%" -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Brak PyInstaller w .venv.
    echo Uruchom: .venv\Scripts\python.exe -m pip install pyinstaller
    exit /b 1
)

"%PYTHON_EXE%" -m PyInstaller app.spec --clean -y
if errorlevel 1 (
    echo.
    echo Build nie powiodl sie.
    exit /b 1
)

echo.
echo Build zakonczony powodzeniem.
echo EXE: dist\ExcelMapper\ExcelMapper.exe

endlocal
