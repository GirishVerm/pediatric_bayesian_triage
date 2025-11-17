#!/usr/bin/env python3
"""
Build script to create standalone executable for IATRO using inference.py (original)
Creates .app bundle for macOS or .exe for Windows
"""

import os
import sys
import subprocess
import platform

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

def build_executable():
    """Build the executable"""
    system = platform.system()
    
    print(f"Building executable for {system}...")
    print(f"Current directory: {os.getcwd()}")
    
    # Check if database exists
    if not os.path.exists("pediatric.db"):
        print("ERROR: pediatric.db not found!")
        print("Please ensure pediatric.db is in the current directory.")
        return False
    
    # Use the spec file for consistent builds
    cmd = ["pyinstaller", "--clean", "IATRO_original.spec"]
    
    print("\nUsing IATRO_original.spec for building...")
    print("Building IATRO with inference.py (original version)...")
    if system == "Darwin":
        print("After building, you can create a .dmg using:")
        print("  cd dist")
        print("  hdiutil create -volname IATRO_original -srcfolder IATRO_original -ov -format UDZO IATRO_original.dmg")
    
    print(f"\nRunning: {' '.join(cmd)}\n")
    
    try:
        subprocess.check_call(cmd)
        print("\n✓ Build successful!")
        print(f"\nExecutable location:")
        if system == "Darwin":
            print("  dist/IATRO_original/IATRO_original")
            print("\nTo create a .dmg file:")
            print("  cd dist")
            print("  hdiutil create -volname IATRO_original -srcfolder IATRO_original -ov -format UDZO IATRO_original.dmg")
        elif system == "Windows":
            print("  dist/IATRO_original.exe")
        else:
            print("  dist/IATRO_original/IATRO_original")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed: {e}")
        return False

def main():
    print("=" * 60)
    print("IATRO Executable Builder (Original Version)")
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
    
    # Build executable
    if build_executable():
        print("\n" + "=" * 60)
        print("Build complete!")
        print("=" * 60)
    else:
        print("\nBuild failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()




