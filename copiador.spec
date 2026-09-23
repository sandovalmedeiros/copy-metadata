# -*- mode: python ; coding: utf-8 -*-
# spec PyInstaller — modo one-dir (decisão D-07 do roadmap; OQ-03 da spec interface).
#
# Build (a partir da raiz do projeto):
#   pip install pyinstaller
#   pyinstaller copiador.spec
#
# Saída: dist/CopiadorMetadados/CopiadorMetadados.exe (pasta completa, sem
# necessidade de Python instalado na máquina de destino).

a = Analysis(
    ["app/main.py"],
    pathex=["."],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="CopiadorMetadados",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="CopiadorMetadados",
)
