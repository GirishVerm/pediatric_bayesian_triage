#!/usr/bin/env python3
import csv
import sqlite3
import sys
from pathlib import Path
import argparse

DB_PATH = Path("pediatric.db")
CSV_PATH = Path("evidence_template.csv")


def get_id(conn: sqlite3.Connection, table: str, name_col: str, name_val: str):
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM {table} WHERE {name_col}=?", (name_val,))
    row = cur.fetchone()
    return row[0] if row else None


def upsert_evidence(conn: sqlite3.Connection, disease_id: int, phenotype_id: int, row: dict):
    sens = row.get("sensitivity")
    spec = row.get("specificity")
    lr_pos = row.get("lr_pos")
    lr_neg = row.get("lr_neg")

    def f(x):
        try:
            return float(x) if x not in (None, "") else None
        except Exception:
            return None

    sens = f(sens)
    spec = f(spec)
    lr_pos = f(lr_pos)
    lr_neg = f(lr_neg)

    # Derive LRs if missing and sens/spec present
    if lr_pos is None and sens is not None and spec is not None and spec < 1:
        lr_pos = sens / (1 - spec) if (1 - spec) > 0 else None
    if lr_neg is None and sens is not None and spec is not None and spec > 0:
        lr_neg = (1 - sens) / spec if spec > 0 else None

    cur = conn.cursor()
    # Check existing row
    cur.execute(
        """
        SELECT id FROM disease_phenotype_evidence
        WHERE disease_id=? AND phenotype_id=? AND IFNULL(age_min_months,-1)=IFNULL(?, -1)
          AND IFNULL(age_max_months,-1)=IFNULL(?, -1) AND IFNULL(setting,'')=IFNULL(?, '') AND IFNULL(region,'')=IFNULL(?, '')
        """,
        (
            disease_id,
            phenotype_id,
            int(row.get("age_min_months")) if row.get("age_min_months") else None,
            int(row.get("age_max_months")) if row.get("age_max_months") else None,
            (row.get("setting") or None),
            (row.get("region") or None),
        ),
    )
    exists = cur.fetchone()
    if exists:
        eid = exists[0]
        cur.execute(
            """
            UPDATE disease_phenotype_evidence
            SET sensitivity=?, specificity=?, lr_pos=?, lr_neg=?, source_pmid=?, guideline_org=?, year=?, study_design=?, evidence_grade=?, extraction_date=?, notes=?
            WHERE id=?
            """,
            (
                sens,
                spec,
                lr_pos,
                lr_neg,
                (row.get("source_pmid") or None),
                (row.get("guideline_org") or None),
                int(row.get("year")) if row.get("year") else None,
                (row.get("study_design") or None),
                (row.get("evidence_grade") or None),
                (row.get("extraction_date") or None),
                (row.get("notes") or None),
                eid,
            ),
        )
    else:
        cur.execute(
            """
            INSERT INTO disease_phenotype_evidence(
              disease_id, phenotype_id, age_min_months, age_max_months, setting, region,
              sensitivity, specificity, lr_pos, lr_neg, source_pmid, guideline_org, year, study_design, evidence_grade, extraction_date, notes
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                disease_id,
                phenotype_id,
                int(row.get("age_min_months")) if row.get("age_min_months") else None,
                int(row.get("age_max_months")) if row.get("age_max_months") else None,
                (row.get("setting") or None),
                (row.get("region") or None),
                sens,
                spec,
                lr_pos,
                lr_neg,
                (row.get("source_pmid") or None),
                (row.get("guideline_org") or None),
                int(row.get("year")) if row.get("year") else None,
                (row.get("study_design") or None),
                (row.get("evidence_grade") or None),
                (row.get("extraction_date") or None),
                (row.get("notes") or None),
            ),
        )


def main(csv_path: Path = CSV_PATH, db_path: Path = DB_PATH, skip_missing: bool = False):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            disease = (row.get("disease_name") or "").strip()
            phen = (row.get("phenotype_label") or "").strip()
            if not disease or not phen:
                continue
            did = get_id(conn, "diseases", "name", disease)
            pid = get_id(conn, "phenotypes", "name", phen)
            if did is None or pid is None:
                if not skip_missing:
                    print(f"Skipping (not found): {disease} / {phen if phen else ''}")
                continue
            upsert_evidence(conn, did, pid, row)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", nargs="?", default=str(CSV_PATH))
    parser.add_argument("db", nargs="?", default=str(DB_PATH))
    parser.add_argument("--skip-missing", action="store_true", help="Silently skip rows where disease or phenotype not found")
    args = parser.parse_args()

    main(Path(args.csv), Path(args.db), skip_missing=args.skip_missing)
