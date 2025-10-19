#!/usr/bin/env python3
import csv
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("pediatric.db")
SCHEMA_PATH = Path("schema_ontology.sql")
CSV_PATH = Path("top20_disease_phenotypes_hpo.csv")


def ensure_schema(conn: sqlite3.Connection):
    # Create missing tables (no destructive changes)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    # Migrate existing tables to add missing columns
    def table_columns(table: str) -> set[str]:
        cur = conn.cursor()
        cur.execute(f"PRAGMA table_info({table})")
        return {row[1] for row in cur.fetchall()}

    def add_column(table: str, col: str, col_type: str):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")

    # Diseases expected columns
    expected_disease_cols = {
        "name": "TEXT",
        "snomed_fsn": "TEXT",
        "snomed_code": "TEXT",
        "icd10_code": "TEXT",
        "description": "TEXT",
        "triage_severity": "REAL",
        "notes": "TEXT",
    }
    try:
        existing = table_columns("diseases")
        for col, ctype in expected_disease_cols.items():
            if col not in existing:
                add_column("diseases", col, ctype)
    except sqlite3.OperationalError:
        # Table may not exist yet, schema creation above should have created it
        pass


def upsert_disease(conn: sqlite3.Connection, name: str, snomed_fsn: str, snomed_code: str):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO diseases(name, snomed_fsn, snomed_code)
        VALUES(?,?,?)
        ON CONFLICT(name) DO UPDATE SET snomed_fsn=excluded.snomed_fsn, snomed_code=excluded.snomed_code
        """,
        (name, snomed_fsn or None, snomed_code or None),
    )
    cur.execute("SELECT id FROM diseases WHERE name=?", (name,))
    return cur.fetchone()[0]


def upsert_phenotype(conn: sqlite3.Connection, name: str, hpo_code: str):
    cur = conn.cursor()
    # Try by HPO code if present
    if hpo_code:
        cur.execute(
            """
            INSERT INTO phenotypes(name, type, hpo_code)
            VALUES(?,?,?)
            ON CONFLICT(hpo_code) DO UPDATE SET name=excluded.name
            """,
            (name, "symptom", hpo_code),
        )
        cur.execute("SELECT id FROM phenotypes WHERE hpo_code=?", (hpo_code,))
    else:
        cur.execute(
            """
            INSERT INTO phenotypes(name, type)
            VALUES(?,?)
            """,
            (name, "symptom"),
        )
        cur.execute("SELECT id FROM phenotypes WHERE name=?", (name,))
    return cur.fetchone()[0]


def link_stub_evidence(conn: sqlite3.Connection, disease_id: int, phenotype_id: int, age_min: str, age_max: str, setting: str):
    # Create a stub evidence row without LRs; avoids duplicates via UNIQUE
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO disease_phenotype_evidence(
                disease_id, phenotype_id, age_min_months, age_max_months, setting
            ) VALUES(?,?,?,?,?)
            """,
            (
                disease_id,
                phenotype_id,
                int(age_min) if age_min else None,
                int(age_max) if age_max else None,
                setting or None,
            ),
        )
    except sqlite3.IntegrityError:
        pass


def main(csv_path: Path = CSV_PATH, db_path: Path = DB_PATH):
    conn = sqlite3.connect(db_path)
    ensure_schema(conn)

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            disease = (row.get("disease_name") or "").strip()
            phen = (row.get("phenotype_label") or "").strip()
            if not disease or not phen:
                continue
            did = upsert_disease(conn, disease, (row.get("snomed_fsn") or "").strip(), (row.get("snomed_id") or "").strip())
            pid = upsert_phenotype(conn, phen, (row.get("hpo_id") or "").strip())
            link_stub_evidence(
                conn,
                did,
                pid,
                (row.get("age_min_months") or "").strip(),
                (row.get("age_max_months") or "").strip(),
                (row.get("setting") or "").strip(),
            )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    csv_arg = Path(sys.argv[1]) if len(sys.argv) > 1 else CSV_PATH
    db_arg = Path(sys.argv[2]) if len(sys.argv) > 2 else DB_PATH
    main(csv_arg, db_arg)
