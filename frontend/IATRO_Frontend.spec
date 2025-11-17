# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for IATRO Frontend Application (macOS)
# For Windows, use IATRO_Frontend_windows.spec

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

# Create executable in onedir mode (required for macOS app bundles)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # Don't bundle binaries - use onedir mode
    name='IATRO_Frontend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window for GUI app
)

# Collect all files for onedir distribution
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='IATRO_Frontend',
)

# macOS app bundle
app = BUNDLE(
    coll,
    name='IATRO_Frontend.app',
    icon=None,
    bundle_identifier='com.iatro.frontend',
    version='1.0.0',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'NSRequiresAquaSystemAppearance': 'False',
    },
)

