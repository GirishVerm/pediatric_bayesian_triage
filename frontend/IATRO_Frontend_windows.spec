# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for IATRO Frontend Application (Windows)

import os
from pathlib import Path

# Get paths relative to this spec file
spec_dir = Path(SPECPATH)
project_root = spec_dir.parent
frontend_dir = spec_dir

block_cipher = None

a = Analysis(
    [os.path.join(frontend_dir, 'main.py')],  # Entry point
    pathex=[
        str(project_root),  # For importing inference module
        str(frontend_dir),  # For importing design_system
    ],
    binaries=[],
    datas=[
        (os.path.join(project_root, 'pediatric.db'), '.'),  # Include database file
    ],
    hiddenimports=[
        'customtkinter',
        'PIL',
        'PIL._tkinter_finder',
        'sqlite3',
        'inference',
        'design_system',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Windows executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='IATRO_Frontend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

