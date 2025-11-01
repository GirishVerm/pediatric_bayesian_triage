#!/usr/bin/env python3
"""
Load disease priors from CSV into the pediatric.db database.

Usage:
    python load_priors.py disease_priors.csv pediatric.db

CSV format:
    disease_name,age_min_months,age_max_months,region,prevalence,source,year
"""
import csv
import sqlite3
import sys
from pathlib import Path
import argparse


def get_disease_id(conn: sqlite3.Connection, disease_name: str) -> int | None:
    """Get disease ID by name."""
    cur = conn.cursor()
    cur.execute("SELECT id FROM diseases WHERE name=?", (disease_name,))
    row = cur.fetchone()
    return row[0] if row else None


def upsert_prior(
    conn: sqlite3.Connection,
    disease_id: int,
    age_min_months: int | None,
    age_max_months: int | None,
    region: str | None,
    prevalence: float,
    source: str | None,
    year: int | None,
):
    """Upsert a disease prior."""
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO disease_priors(
            disease_id, age_min_months, age_max_months, region, prevalence, source, year
        ) VALUES(?,?,?,?,?,?,?)
        ON CONFLICT(disease_id, age_min_months, age_max_months, region)
        DO UPDATE SET
            prevalence=excluded.prevalence,
            source=excluded.source,
            year=excluded.year
        """,
        (disease_id, age_min_months, age_max_months, region, prevalence, source, year),
    )


def normalize_priors(conn: sqlite3.Connection):
    """Optional: Normalize priors so they sum to 1.0 (currently not needed as inference.py normalizes)."""
    # This is optional - inference.py already normalizes priors
    pass


def main(csv_path: Path, db_path: Path, skip_missing: bool = False):
    """Load priors from CSV into database."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")

    # Ensure schema exists
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS disease_priors (
          id INTEGER PRIMARY KEY,
          disease_id INTEGER NOT NULL REFERENCES diseases(id) ON DELETE CASCADE,
          age_min_months INTEGER,
          age_max_months INTEGER,
          region TEXT,
          prevalence REAL,
          source TEXT,
          year INTEGER,
          UNIQUE(disease_id, age_min_months, age_max_months, region)
        )
        """
    )

    loaded = 0
    skipped = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            disease_name = (row.get("disease_name") or "").strip()
            if not disease_name:
                continue

            disease_id = get_disease_id(conn, disease_name)
            if disease_id is None:
                if not skip_missing:
                    print(f"Skipping (disease not found): {disease_name}")
                skipped += 1
                continue

            # Parse optional fields
            age_min = row.get("age_min_months") or None
            age_max = row.get("age_max_months") or None
            region = (row.get("region") or "").strip() or None
            source = (row.get("source") or "").strip() or None
            year_str = row.get("year") or None

            # Parse prevalence
            try:
                prevalence = float(row.get("prevalence", 0))
            except (ValueError, TypeError):
                print(f"Skipping invalid prevalence for {disease_name}")
                skipped += 1
                continue

            if prevalence <= 0 or prevalence > 1:
                print(f"Warning: prevalence {prevalence} for {disease_name} outside [0,1], skipping")
                skipped += 1
                continue

            # Parse optional integers
            age_min_int = int(age_min) if age_min else None
            age_max_int = int(age_max) if age_max else None
            year_int = int(year_str) if year_str else None

            upsert_prior(
                conn, disease_id, age_min_int, age_max_int, region, prevalence, source, year_int
            )
            loaded += 1

    conn.commit()

    # Show summary
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM disease_priors")
    total_priors = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT disease_id) FROM disease_priors")
    diseases_with_priors = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM diseases")
    total_diseases = cur.fetchone()[0]

    print(f"\nLoaded {loaded} prior rows")
    if skipped > 0:
        print(f"Skipped {skipped} rows")
    print(f"Total priors in DB: {total_priors}")
    print(f"Diseases with priors: {diseases_with_priors}/{total_diseases}")

    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load disease priors from CSV into database")
    parser.add_argument("csv", nargs="?", default="disease_priors.csv", help="CSV file path")
    parser.add_argument("db", nargs="?", default="pediatric.db", help="Database file path")
    parser.add_argument(
        "--skip-missing",
        action="store_true",
        help="Silently skip rows where disease not found",
    )
    args = parser.parse_args()

    main(Path(args.csv), Path(args.db), skip_missing=args.skip_missing)

