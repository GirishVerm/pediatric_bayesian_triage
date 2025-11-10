#!/usr/bin/env python3
"""
Setup a new pediatric database with the top 20 diseases.

Usage:
    python setup_new_db.py [db_name]
    
This will:
1. Create a new database file
2. Initialize schema
3. Load diseases from diseases_top20.csv
4. Ready for priors and evidence loading
"""
import sqlite3
import sys
from pathlib import Path
from load_diseases import main as load_diseases

def setup_database(db_path: str = "pediatric_new.db"):
    """Initialize a new database with schema and diseases."""
    
    print(f"Setting up new database: {db_path}")
    
    # Remove existing database if it exists (optional - comment out if you want to keep)
    db_file = Path(db_path)
    if db_file.exists():
        response = input(f"Database {db_path} already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return
        db_file.unlink()
        print(f"Removed existing {db_path}")
    
    # Create database and load schema
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    
    print("Loading schema...")
    with open('schema_ontology.sql', 'r') as f:
        schema_sql = f.read()
        conn.executescript(schema_sql)
    
    conn.commit()
    conn.close()
    
    print("Schema loaded successfully.")
    
    # Load diseases
    diseases_csv = Path("diseases_top20.csv")
    if not diseases_csv.exists():
        print(f"Error: {diseases_csv} not found!")
        return
    
    print(f"\nLoading diseases from {diseases_csv}...")
    load_diseases(diseases_csv, Path(db_path), skip_existing=False)
    
    print(f"\n{'='*80}")
    print(f"Database setup complete: {db_path}")
    print(f"\nNext steps:")
    print(f"  1. Review and update priors_top20.csv with validated prevalence data")
    print(f"  2. Load priors: python load_priors.py priors_top20.csv {db_path}")
    print(f"  3. Add evidence to evidence_top20.csv")
    print(f"  4. Load evidence: python load_evidence.py evidence_top20.csv {db_path}")
    print(f"{'='*80}")

if __name__ == "__main__":
    db_name = sys.argv[1] if len(sys.argv) > 1 else "pediatric_new.db"
    setup_database(db_name)

