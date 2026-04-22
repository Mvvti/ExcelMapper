# -*- mode: python ; coding: utf-8 -*-
import os


datas = [
    ('frontend', 'frontend'),
]
if os.path.isdir('assets'):
    datas.append(('assets', 'assets'))


a = Analysis(
    ['gui_app.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'webview',
        'webview.platforms.winforms',
        'webview.platforms.edgechromium',
        'clr',
        'pythoncom',
        'win32api',
        'win32con',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['hooks/hook_base_path.py'],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ExcelMapper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)

# Note: on Windows, EXE icon typically requires an .ico file.

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ExcelMapper',
)
