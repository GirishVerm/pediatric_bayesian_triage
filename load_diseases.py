#!/usr/bin/env python3
"""
Load diseases from CSV into the pediatric database.

Usage:
    python load_diseases.py diseases.csv pediatric.db

CSV format:
    name, description, triage_severity, snomed_fsn, snomed_code, icd10_code, notes
"""
import csv
import sqlite3
from pathlib import Path
import argparse


def main(csv_path: Path, db_path: Path, skip_existing: bool = False):
    """Load diseases from CSV into database."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Ensure schema exists
    with open('schema_ontology.sql', 'r') as f:
        schema_sql = f.read()
        conn.executescript(schema_sql)
    
    loaded = 0
    skipped = 0
    
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("name") or "").strip()
            if not name:
                continue
            
            # Check if already exists
            cur = conn.cursor()
            cur.execute("SELECT id FROM diseases WHERE name=?", (name,))
            existing = cur.fetchone()
            
            if existing:
                if skip_existing:
                    skipped += 1
                    continue
                else:
                    # Update existing
                    cur.execute(
                        """
                        UPDATE diseases
                        SET description=?, triage_severity=?, snomed_fsn=?, 
                            snomed_code=?, icd10_code=?, notes=?
                        WHERE name=?
                        """,
                        (
                            row.get("description") or None,
                            float(row.get("triage_severity")) if row.get("triage_severity") else None,
                            row.get("snomed_fsn") or None,
                            row.get("snomed_code") or None,
                            row.get("icd10_code") or None,
                            row.get("notes") or None,
                            name,
                        ),
                    )
                    loaded += 1
            else:
                # Insert new
                cur.execute(
                    """
                    INSERT INTO diseases (name, description, triage_severity, snomed_fsn, snomed_code, icd10_code, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        name,
                        row.get("description") or None,
                        float(row.get("triage_severity")) if row.get("triage_severity") else None,
                        row.get("snomed_fsn") or None,
                        row.get("snomed_code") or None,
                        row.get("icd10_code") or None,
                        row.get("notes") or None,
                    ),
                )
                loaded += 1
    
    conn.commit()
    
    # Show summary
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM diseases")
    total_diseases = cur.fetchone()[0]
    
    print(f"\nLoaded/updated {loaded} diseases")
    if skipped > 0:
        print(f"Skipped {skipped} existing diseases")
    print(f"Total diseases in database: {total_diseases}")
    
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load diseases from CSV into database")
    parser.add_argument("csv", nargs="?", default="diseases_top20.csv", help="CSV file path")
    parser.add_argument("db", nargs="?", default="pediatric_new.db", help="Database file path")
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip diseases that already exist",
    )
    args = parser.parse_args()
    
    main(Path(args.csv), Path(args.db), skip_existing=args.skip_existing)

