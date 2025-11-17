#!/usr/bin/env python3
"""
Standalone version of IATRO that handles database path correctly
when packaged as an executable
"""

import sys
import os
import sqlite3

# Determine if running as executable or script
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = sys._MEIPASS
    EXE_DIR = os.path.dirname(sys.executable)
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    EXE_DIR = BASE_DIR

# Try to find database in multiple locations
DB_PATHS = [
    os.path.join(BASE_DIR, "pediatric.db"),  # Bundled with executable
    os.path.join(EXE_DIR, "pediatric.db"),   # Same directory as executable
    os.path.join(os.getcwd(), "pediatric.db"),  # Current working directory
    "pediatric.db"  # Current directory
]

def find_database():
    """Find the database file"""
    for db_path in DB_PATHS:
        if os.path.exists(db_path):
            return db_path
    return None

def main():
    """Main entry point"""
    # Find database
    db_path = find_database()
    
    if db_path is None:
        print("ERROR: Could not find pediatric.db")
        print("Please ensure pediatric.db is in the same directory as the executable.")
        print("\nSearched locations:")
        for path in DB_PATHS:
            print(f"  - {path}")
        sys.exit(1)
    
    # Import the inference module after finding database
    # Add current directory to path to ensure imports work
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)
    
    # Import and run inference with database path
    try:
        from inference_improved import main as inference_main
        
        # Override default database path in sys.argv
        original_argv = sys.argv[:]
        sys.argv = [sys.argv[0], "--db", db_path] + sys.argv[1:]
        
        # Run inference
        inference_main()
        
        # Restore original argv (probably not needed, but safe)
        sys.argv = original_argv
        
    except ImportError as e:
        print(f"ERROR: Could not import inference_improved: {e}")
        print(f"Python path: {sys.path}")
        sys.exit(1)

if __name__ == "__main__":
    main()

