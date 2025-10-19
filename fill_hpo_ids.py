#!/usr/bin/env python3
import csv
import time
import sys
import requests

OLS_SEARCH_URL = "https://www.ebi.ac.uk/ols4/api/search"


def search_hpo(term: str):
    """Return best matching HPO id for a phenotype label using OLS."""
    params_exact = {
        "q": term,
        "ontology": "hp",
        "type": "class",
        "exact": "true",
        "rows": 20,
    }
    params_fuzzy = {
        "q": term,
        "ontology": "hp",
        "type": "class",
        "rows": 20,
    }

    for params in (params_exact, params_fuzzy):
        try:
            r = requests.get(OLS_SEARCH_URL, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()
        except Exception:
            continue
        docs = data.get("response", {}).get("docs", [])
        if not docs:
            continue
        # Prefer exact label match (case-insensitive)
        for d in docs:
            if d.get("label", "").lower() == term.lower():
                return d.get("obo_id") or d.get("short_form")
        # Otherwise take first result
        best = docs[0]
        return best.get("obo_id") or best.get("short_form")
    return None


def fill_hpo_ids(input_csv: str, output_csv: str):
    required = [
        "disease_name",
        "snomed_fsn",
        "snomed_id",
        "phenotype_label",
        "hpo_id",
        "age_min_months",
        "age_max_months",
        "setting",
        "notes",
    ]

    rows = []
    with open(input_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Validate header
        fieldnames = reader.fieldnames or []
        missing = [c for c in required if c not in fieldnames]
        if missing:
            print(f"Warning: input CSV missing columns: {missing}. Proceeding with normalization.")
        for raw in reader:
            if raw is None:
                continue
            # Remove unexpected key caused by extra columns
            if None in raw:
                raw.pop(None, None)
            # Normalize to required keys and strip whitespace
            normalized = {k: (raw.get(k) or "").strip() for k in required}
            # Skip empty rows (no disease and no phenotype)
            if not ((normalized["disease_name"]) or (normalized["phenotype_label"])):
                continue
            rows.append(normalized)

    for row in rows:
        label = row.get("phenotype_label")
        if not label or row.get("hpo_id"):
            continue
        hpo = search_hpo(label)
        row["hpo_id"] = hpo or ""
        time.sleep(0.2)

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=required)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    in_path = sys.argv[1] if len(sys.argv) > 1 else "top20_disease_phenotypes.csv"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "top20_disease_phenotypes_hpo.csv"
    fill_hpo_ids(in_path, out_path)
