#!/usr/bin/env python3
"""
Build script to create standalone executables for IATRO Frontend
Creates .app bundle for macOS (DMG) and .exe for Windows
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """Install PyInstaller"""
    print("Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def check_dependencies():
    """Check if required packages are installed"""
    required = ['customtkinter', 'PIL']
    missing = []
    for pkg in required:
        try:
            __import__(pkg if pkg != 'PIL' else 'PIL')
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"ERROR: Missing required packages: {', '.join(missing)}")
        print("Please install them with:")
        print(f"  pip install {' '.join(missing)}")
        return False
    return True

def check_database():
    """Check if database file exists"""
    frontend_dir = Path(__file__).parent
    project_root = frontend_dir.parent
    db_path = project_root / "pediatric.db"
    
    if not db_path.exists():
        print(f"ERROR: pediatric.db not found at {db_path}!")
        print("Please ensure pediatric.db is in the project root directory.")
        return False
    return True

def build_macos_app():
    """Build macOS .app bundle"""
    print("\n" + "=" * 60)
    print("Building macOS Application Bundle")
    print("=" * 60)
    
    frontend_dir = Path(__file__).parent
    spec_file = frontend_dir / "IATRO_Frontend.spec"
    
    cmd = ["pyinstaller", "--clean", "--noconfirm", str(spec_file)]
    
    print(f"\nRunning: {' '.join(cmd)}\n")
    
    try:
        subprocess.check_call(cmd, cwd=str(frontend_dir))
        print("\n✓ macOS build successful!")
        
        # Check if .app was created
        dist_dir = frontend_dir / "dist"
        app_path = dist_dir / "IATRO_Frontend.app"
        
        if app_path.exists():
            print(f"\nApplication bundle created at: {app_path}")
            return True
        else:
            print("\nWarning: .app bundle not found in expected location")
            return False
    except subprocess.CalledProcessError as e:
        print(f"\n✗ macOS build failed: {e}")
        return False

def create_dmg():
    """Create DMG file from .app bundle"""
    print("\n" + "=" * 60)
    print("Creating DMG File")
    print("=" * 60)
    
    frontend_dir = Path(__file__).parent
    dist_dir = frontend_dir / "dist"
    app_path = dist_dir / "IATRO_Frontend.app"
    dmg_path = dist_dir / "IATRO_Frontend.dmg"
    
    if not app_path.exists():
        print("ERROR: .app bundle not found. Build failed.")
        return False
    
    # Remove existing DMG if present
    if dmg_path.exists():
        print(f"Removing existing DMG: {dmg_path}")
        dmg_path.unlink()
    
    # Create DMG using hdiutil
    cmd = [
        "hdiutil", "create",
        "-volname", "IATRO Frontend",
        "-srcfolder", str(app_path),
        "-ov",
        "-format", "UDZO",
        str(dmg_path)
    ]
    
    print(f"\nRunning: {' '.join(cmd)}\n")
    
    try:
        subprocess.check_call(cmd)
        print(f"\n✓ DMG created successfully at: {dmg_path}")
        print(f"  Size: {dmg_path.stat().st_size / (1024*1024):.1f} MB")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ DMG creation failed: {e}")
        return False

def build_windows_exe():
    """Build Windows .exe (note: requires Windows OS)"""
    print("\n" + "=" * 60)
    print("Building Windows Executable")
    print("=" * 60)
    
    system = platform.system()
    if system != "Windows":
        print("WARNING: Windows executable can only be built on Windows.")
        print("The spec file has been created and can be used on a Windows machine.")
        print("\nTo build on Windows, run:")
        print("  cd frontend")
        print("  pyinstaller --clean --noconfirm IATRO_Frontend_windows.spec")
        print("\nThe .exe will be created in frontend/dist/IATRO_Frontend.exe")
        return False
    
    frontend_dir = Path(__file__).parent
    spec_file = frontend_dir / "IATRO_Frontend_windows.spec"
    
    cmd = ["pyinstaller", "--clean", "--noconfirm", str(spec_file)]
    
    print(f"\nRunning: {' '.join(cmd)}\n")
    
    try:
        subprocess.check_call(cmd, cwd=str(frontend_dir))
        print("\n✓ Windows build successful!")
        
        exe_path = frontend_dir / "dist" / "IATRO_Frontend.exe"
        if exe_path.exists():
            print(f"\nExecutable created at: {exe_path}")
            print(f"  Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
            return True
        else:
            print("\nWarning: .exe not found in expected location")
            return False
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Windows build failed: {e}")
        return False

def main():
    print("=" * 60)
    print("IATRO Frontend Executable Builder")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    if not check_pyinstaller():
        print("PyInstaller not found.")
        response = input("Install PyInstaller? (y/n): ")
        if response.lower() == 'y':
            install_pyinstaller()
        else:
            print("PyInstaller is required. Install it with:")
            print("  pip install pyinstaller")
            return
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check database
    if not check_database():
        return
    
    system = platform.system()
    success = True
    
    # Build macOS app and DMG
    if system == "Darwin":
        if build_macos_app():
            create_dmg()
        else:
            success = False
        
        # Also create Windows build instructions
        print("\n" + "=" * 60)
        print("Windows Build Instructions")
        print("=" * 60)
        print("To build Windows .exe, run on a Windows machine:")
        print("  cd frontend")
        print("  pyinstaller --clean --noconfirm IATRO_Frontend_windows.spec")
        print("\nThe .exe will be in frontend/dist/IATRO_Frontend.exe")
    
    # Build Windows exe if on Windows
    elif system == "Windows":
        if build_windows_exe():
            print("\n✓ Windows executable built successfully!")
        else:
            success = False
    
    # Other systems
    else:
        print(f"\nBuilding for {system}...")
        frontend_dir = Path(__file__).parent
        spec_file = frontend_dir / "IATRO_Frontend.spec"
        cmd = ["pyinstaller", "--clean", "--noconfirm", str(spec_file)]
        
        try:
            subprocess.check_call(cmd, cwd=str(frontend_dir))
            print("\n✓ Build successful!")
        except subprocess.CalledProcessError as e:
            print(f"\n✗ Build failed: {e}")
            success = False
    
    if success:
        print("\n" + "=" * 60)
        print("Build Complete!")
        print("=" * 60)
        frontend_dir = Path(__file__).parent
        dist_dir = frontend_dir / "dist"
        print(f"\nOutput directory: {dist_dir}")
    else:
        print("\nBuild completed with errors. Please check the messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()

