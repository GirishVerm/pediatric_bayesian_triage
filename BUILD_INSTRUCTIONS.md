# Building IATRO Executable

This guide explains how to build IATRO as a standalone executable for distribution to medical students.

## Prerequisites

1. Python 3.10+ installed
2. PyInstaller installed: `pip install pyinstaller`
3. `pediatric.db` file in the project directory

## Quick Build

### Option 1: Using the build script (Recommended)

```bash
python build_executable.py
```

This will:
- Check if PyInstaller is installed
- Build the executable with the database bundled
- Provide instructions for creating a .dmg (macOS) or .exe (Windows)

### Option 2: Using PyInstaller directly

#### For macOS (.app bundle):
```bash
pyinstaller IATRO.spec
```

Then create a .dmg:
```bash
cd dist
hdiutil create -volname IATRO -srcfolder IATRO -ov -format UDZO IATRO.dmg
```

#### For Windows (.exe):
```bash
pyinstaller IATRO.spec
```

The executable will be in `dist/IATRO.exe`

## What Gets Built

- **Executable**: `dist/IATRO` (macOS/Linux) or `dist/IATRO.exe` (Windows)
- **Database**: `pediatric.db` is bundled inside the executable
- **Standalone**: No Python installation required on the target machine

## Testing the Executable

After building, test it:

```bash
# macOS/Linux
./dist/IATRO

# Windows
dist\IATRO.exe
```

Or with preview mode:
```bash
./dist/IATRO --preview 10
```

## Distribution

### macOS
1. Build the executable: `python build_executable.py`
2. Create .dmg: Follow instructions in build output
3. Share the .dmg file

### Windows
1. Build the executable: `python build_executable.py`
2. Share the `dist/IATRO.exe` file (may need to zip it)

### Linux
1. Build the executable: `python build_executable.py`
2. Share the `dist/IATRO` file (may need to zip it)

## Troubleshooting

### Database not found error
- Ensure `pediatric.db` is in the project root directory
- The database is automatically bundled with the executable

### PyInstaller not found
```bash
pip install pyinstaller
```

### Large executable size
- This is normal - PyInstaller bundles Python interpreter
- macOS: ~15-20 MB
- Windows: ~10-15 MB

### Antivirus warnings (Windows)
- Some antivirus software may flag PyInstaller executables
- This is a false positive - you can whitelist it or sign the executable

## Notes

- The executable is self-contained and doesn't require Python
- The database is bundled inside the executable
- All standard library modules are included
- No external dependencies required (only uses Python standard library)




