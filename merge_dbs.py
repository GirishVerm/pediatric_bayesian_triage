#!/usr/bin/env python3
"""
Merge two pediatric databases into one.

Usage:
    python merge_dbs.py db1.db db2.db merged.db
"""
import sqlite3
import sys
from pathlib import Path


def get_table_columns(conn, table_name):
    """Get column names for a table."""
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cur.fetchall()]


def merge_diseases(db1_conn, db2_conn, merged_conn):
    """Merge diseases from both databases."""
    cur1 = db1_conn.cursor()
    cur2 = db2_conn.cursor()
    cur_merged = merged_conn.cursor()
    
    # Get all diseases from DB1
    cur1.execute("SELECT name, description, triage_severity, snomed_fsn, snomed_code, icd10_code, notes FROM diseases")
    db1_diseases = {row[0]: row[1:] for row in cur1.fetchall()}
    
    # Get all diseases from DB2
    cur2.execute("SELECT name, description, triage_severity, snomed_fsn, snomed_code, icd10_code, notes FROM diseases")
    db2_diseases = {row[0]: row[1:] for row in cur2.fetchall()}
    
    # Create name to ID mapping for merged DB
    name_to_id = {}
    
    # Insert diseases (DB1 first, then DB2 if not duplicate)
    for name, data in db1_diseases.items():
        cur_merged.execute(
            "INSERT OR IGNORE INTO diseases (name, description, triage_severity, snomed_fsn, snomed_code, icd10_code, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name,) + data
        )
        cur_merged.execute("SELECT id FROM diseases WHERE name=?", (name,))
        name_to_id[name] = cur_merged.fetchone()[0]
    
    for name, data in db2_diseases.items():
        if name not in db1_diseases:
            cur_merged.execute(
                "INSERT INTO diseases (name, description, triage_severity, snomed_fsn, snomed_code, icd10_code, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (name,) + data
            )
            cur_merged.execute("SELECT id FROM diseases WHERE name=?", (name,))
            name_to_id[name] = cur_merged.fetchone()[0]
    
    return name_to_id


def merge_phenotypes(db1_conn, db2_conn, merged_conn):
    """Merge phenotypes from both databases."""
    cur1 = db1_conn.cursor()
    cur2 = db2_conn.cursor()
    cur_merged = merged_conn.cursor()
    
    # Get all phenotypes from DB1
    cur1.execute("SELECT name, type, snomed_code, hpo_code, loinc_code FROM phenotypes")
    db1_phenotypes = {row[0]: row[1:] for row in cur1.fetchall()}
    
    # Get all phenotypes from DB2
    cur2.execute("SELECT name, type, snomed_code, hpo_code, loinc_code FROM phenotypes")
    db2_phenotypes = {row[0]: row[1:] for row in cur2.fetchall()}
    
    # Create name to ID mapping for merged DB
    name_to_id = {}
    
    # Insert phenotypes (DB1 first, then DB2 if not duplicate)
    for name, data in db1_phenotypes.items():
        cur_merged.execute(
            "INSERT OR IGNORE INTO phenotypes (name, type, snomed_code, hpo_code, loinc_code) VALUES (?, ?, ?, ?, ?)",
            (name,) + data
        )
        cur_merged.execute("SELECT id FROM phenotypes WHERE name=?", (name,))
        name_to_id[name] = cur_merged.fetchone()[0]
    
    for name, data in db2_phenotypes.items():
        if name not in db1_phenotypes:
            cur_merged.execute(
                "INSERT INTO phenotypes (name, type, snomed_code, hpo_code, loinc_code) VALUES (?, ?, ?, ?, ?)",
                (name,) + data
            )
            cur_merged.execute("SELECT id FROM phenotypes WHERE name=?", (name,))
            name_to_id[name] = cur_merged.fetchone()[0]
    
    return name_to_id


def merge_priors(db1_conn, db2_conn, merged_conn, disease_map1, disease_map2):
    """Merge priors from both databases."""
    cur1 = db1_conn.cursor()
    cur2 = db2_conn.cursor()
    cur_merged = merged_conn.cursor()
    
    # Get disease name mappings
    cur_merged.execute("SELECT id, name FROM diseases")
    merged_name_to_id = {name: did for did, name in cur_merged.fetchall()}
    
    # Merge priors from DB1
    cur1.execute("SELECT disease_id, age_min_months, age_max_months, region, prevalence, source, year FROM disease_priors")
    for row in cur1.fetchall():
        did1, age_min, age_max, region, prev, source, year = row
        # Get disease name from DB1
        cur1.execute("SELECT name FROM diseases WHERE id=?", (did1,))
        disease_name = cur1.fetchone()[0]
        merged_did = merged_name_to_id.get(disease_name)
        if merged_did:
            cur_merged.execute(
                "INSERT OR IGNORE INTO disease_priors (disease_id, age_min_months, age_max_months, region, prevalence, source, year) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (merged_did, age_min, age_max, region, prev, source, year)
            )
    
    # Merge priors from DB2
    cur2.execute("SELECT disease_id, age_min_months, age_max_months, region, prevalence, source, year FROM disease_priors")
    for row in cur2.fetchall():
        did2, age_min, age_max, region, prev, source, year = row
        # Get disease name from DB2
        cur2.execute("SELECT name FROM diseases WHERE id=?", (did2,))
        disease_name = cur2.fetchone()[0]
        merged_did = merged_name_to_id.get(disease_name)
        if merged_did:
            cur_merged.execute(
                "INSERT OR IGNORE INTO disease_priors (disease_id, age_min_months, age_max_months, region, prevalence, source, year) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (merged_did, age_min, age_max, region, prev, source, year)
            )


def merge_evidence(db1_conn, db2_conn, merged_conn, disease_map1, disease_map2, phenotype_map1, phenotype_map2):
    """Merge evidence from both databases, handling schema differences."""
    cur1 = db1_conn.cursor()
    cur2 = db2_conn.cursor()
    cur_merged = merged_conn.cursor()
    
    # Get column names for evidence table in all databases
    db1_cols = get_table_columns(db1_conn, "disease_phenotype_evidence")
    db2_cols = get_table_columns(db2_conn, "disease_phenotype_evidence")
    merged_cols = get_table_columns(merged_conn, "disease_phenotype_evidence")
    
    # Get disease and phenotype name mappings
    cur_merged.execute("SELECT id, name FROM diseases")
    merged_disease_map = {name: did for did, name in cur_merged.fetchall()}
    cur_merged.execute("SELECT id, name FROM phenotypes")
    merged_phenotype_map = {name: pid for pid, name in cur_merged.fetchall()}
    
    # Common columns (excluding id)
    common_cols = [c for c in merged_cols if c != 'id']
    
    # Merge evidence from DB1
    cur1.execute(f"SELECT * FROM disease_phenotype_evidence")
    for row in cur1.fetchall():
        row_dict = dict(zip(db1_cols, row))
        disease_id1 = row_dict['disease_id']
        phenotype_id1 = row_dict['phenotype_id']
        
        # Get disease and phenotype names
        cur1.execute("SELECT name FROM diseases WHERE id=?", (disease_id1,))
        disease_name = cur1.fetchone()[0]
        cur1.execute("SELECT name FROM phenotypes WHERE id=?", (phenotype_id1,))
        phenotype_name = cur1.fetchone()[0]
        
        merged_did = merged_disease_map.get(disease_name)
        merged_pid = merged_phenotype_map.get(phenotype_name)
        
        if merged_did and merged_pid:
            # Build INSERT statement with only columns that exist in merged schema
            values = []
            placeholders = []
            for col in common_cols:
                if col in db1_cols:
                    values.append(row_dict.get(col))
                else:
                    values.append(None)  # Fill with NULL for missing columns
                placeholders.append('?')
            
            # Update disease_id and phenotype_id
            values[common_cols.index('disease_id')] = merged_did
            values[common_cols.index('phenotype_id')] = merged_pid
            
            sql = f"INSERT OR IGNORE INTO disease_phenotype_evidence ({', '.join(common_cols)}) VALUES ({', '.join(placeholders)})"
            cur_merged.execute(sql, values)
    
    # Merge evidence from DB2
    cur2.execute(f"SELECT * FROM disease_phenotype_evidence")
    for row in cur2.fetchall():
        row_dict = dict(zip(db2_cols, row))
        disease_id2 = row_dict['disease_id']
        phenotype_id2 = row_dict['phenotype_id']
        
        # Get disease and phenotype names
        cur2.execute("SELECT name FROM diseases WHERE id=?", (disease_id2,))
        disease_name = cur2.fetchone()[0]
        cur2.execute("SELECT name FROM phenotypes WHERE id=?", (phenotype_id2,))
        phenotype_name = cur2.fetchone()[0]
        
        merged_did = merged_disease_map.get(disease_name)
        merged_pid = merged_phenotype_map.get(phenotype_name)
        
        if merged_did and merged_pid:
            # Build INSERT statement
            values = []
            placeholders = []
            for col in common_cols:
                if col in db2_cols:
                    values.append(row_dict.get(col))
                else:
                    values.append(None)
                placeholders.append('?')
            
            # Update disease_id and phenotype_id
            values[common_cols.index('disease_id')] = merged_did
            values[common_cols.index('phenotype_id')] = merged_pid
            
            sql = f"INSERT OR IGNORE INTO disease_phenotype_evidence ({', '.join(common_cols)}) VALUES ({', '.join(placeholders)})"
            cur_merged.execute(sql, values)


def main():
    if len(sys.argv) < 4:
        print("Usage: python merge_dbs.py db1.db db2.db merged.db")
        sys.exit(1)
    
    db1_path = sys.argv[1]
    db2_path = sys.argv[2]
    merged_path = sys.argv[3]
    
    print(f"Merging {db1_path} + {db2_path} → {merged_path}")
    
    # Remove merged DB if exists
    if Path(merged_path).exists():
        Path(merged_path).unlink()
    
    # Open connections
    db1_conn = sqlite3.connect(db1_path)
    db2_conn = sqlite3.connect(db2_path)
    merged_conn = sqlite3.connect(merged_path)
    merged_conn.execute("PRAGMA foreign_keys = ON")
    
    # Load schema
    print("Loading schema...")
    with open('schema_ontology.sql', 'r') as f:
        schema_sql = f.read()
        merged_conn.executescript(schema_sql)
    
    # Merge data
    print("Merging diseases...")
    disease_map = merge_diseases(db1_conn, db2_conn, merged_conn)
    merged_conn.commit()
    
    print("Merging phenotypes...")
    phenotype_map = merge_phenotypes(db1_conn, db2_conn, merged_conn)
    merged_conn.commit()
    
    print("Merging priors...")
    merge_priors(db1_conn, db2_conn, merged_conn, {}, {})
    merged_conn.commit()
    
    print("Merging evidence...")
    merge_evidence(db1_conn, db2_conn, merged_conn, {}, {}, {}, {})
    merged_conn.commit()
    
    # Summary
    cur = merged_conn.cursor()
    cur.execute("SELECT COUNT(*) FROM diseases")
    diseases = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM phenotypes")
    phenotypes = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM disease_priors")
    priors = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM disease_phenotype_evidence")
    evidence = cur.fetchone()[0]
    
    print(f"\n{'='*80}")
    print(f"Merge complete: {merged_path}")
    print(f"  Diseases: {diseases}")
    print(f"  Phenotypes: {phenotypes}")
    print(f"  Priors: {priors}")
    print(f"  Evidence entries: {evidence}")
    print(f"{'='*80}")
    
    db1_conn.close()
    db2_conn.close()
    merged_conn.close()


if __name__ == "__main__":
    main()

