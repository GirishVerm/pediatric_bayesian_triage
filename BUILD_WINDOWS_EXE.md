# Building Windows EXE from IATRO_original.spec

## Prerequisites

1. Windows machine (Windows 10/11)
2. Python 3.10+ installed
3. PyInstaller installed: `pip install pyinstaller`

## Build Steps

### Step 1: Copy Files to Windows Machine

Copy these files to your Windows machine:
- `IATRO_original.spec`
- `inference.py` (already modified for PyInstaller)
- `pediatric.db`

### Step 2: Build the Executable

Open Command Prompt or PowerShell in the directory with the files:

```cmd
pyinstaller --clean IATRO_original.spec
```

### Step 3: Find the Executable

The executable will be created at:
```
dist\IATRO_original.exe
```

### Step 4: Test the Executable

```cmd
dist\IATRO_original.exe --preview 3
```

## What Gets Created

- **Executable**: `dist/IATRO_original.exe` (~10-15 MB)
- **Standalone**: No Python installation required
- **Database**: `pediatric.db` is bundled inside

## Distribution

Share `IATRO_original.exe` with medical students. They can run it directly without installing Python.

## Troubleshooting

**Antivirus warnings:**
- Some antivirus software may flag PyInstaller executables
- This is a false positive - you can whitelist it or sign the executable

**Database not found:**
- The database is bundled inside the executable
- If you get database errors, rebuild with `--clean` flag

## Alternative: Build Script

You can also use a build script similar to `build_original_executable.py` but adapted for Windows.




