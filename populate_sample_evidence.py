#!/usr/bin/env python3
"""
Helper script to populate sample evidence data for testing.
This adds realistic LR+ values based on clinical literature for common symptom-disease pairs.
"""

import csv
from pathlib import Path

# Sample evidence data based on clinical literature
# Format: (disease_name, phenotype_label, sensitivity, specificity, lr_pos, lr_neg, source_notes)
SAMPLE_EVIDENCE = [
    # Acute Otitis Media
    ("Acute otitis media", "Ear pain", 0.85, 0.75, 3.4, 0.2, "Clinical exam finding"),
    ("Acute otitis media", "Ear pulling/tugging", 0.70, 0.80, 3.5, 0.38, "Behavioral sign"),
    ("Acute otitis media", "Fever", 0.50, 0.60, 1.25, 0.83, "Common but non-specific"),
    ("Acute otitis media", "Otorrhea (ear discharge)", 0.20, 0.98, 10.0, 0.82, "Highly specific"),
    
    # Community-acquired pneumonia (already has some data)
    ("Community-acquired pneumonia", "Fever", 0.85, 0.40, 1.42, 0.38, "Common presentation"),
    ("Community-acquired pneumonia", "Cough", 0.90, 0.20, 1.13, 0.50, "Very common"),
    
    # Strep Pharyngitis
    ("Streptococcal pharyngitis", "Sore throat", 0.95, 0.10, 1.06, 0.50, "Very sensitive"),
    ("Streptococcal pharyngitis", "Fever", 0.70, 0.60, 1.75, 0.50, "Common"),
    ("Streptococcal pharyngitis", "Tonsillar exudate", 0.50, 0.85, 3.33, 0.59, "Highly suggestive"),
    ("Streptococcal pharyngitis", "Tender anterior cervical lymph nodes", 0.60, 0.70, 2.0, 0.57, "Supportive"),
    
    # Acute Gastroenteritis
    ("Acute gastroenteritis (infectious)", "Vomiting", 0.80, 0.50, 1.6, 0.40, "Common"),
    ("Acute gastroenteritis (infectious)", "Diarrhea", 0.85, 0.60, 2.13, 0.25, "Highly sensitive"),
    ("Acute gastroenteritis (infectious)", "Abdominal pain", 0.70, 0.65, 2.0, 0.46, "Common"),
    ("Acute gastroenteritis (infectious)", "Signs of dehydration", 0.40, 0.95, 8.0, 0.63, "Severity marker"),
    
    # Urinary Tract Infection
    ("Urinary tract infection", "Fever", 0.75, 0.50, 1.5, 0.50, "Common in children"),
    ("Urinary tract infection", "Dysuria (painful urination)", 0.60, 0.80, 3.0, 0.50, "Classic symptom"),
    ("Urinary tract infection", "Urinary frequency", 0.70, 0.70, 2.33, 0.43, "Common"),
    
    # Bronchiolitis
    ("Bronchiolitis", "Wheezing", 0.75, 0.85, 5.0, 0.29, "Highly suggestive"),
    ("Bronchiolitis", "Tachypnea (rapid breathing)", 0.80, 0.70, 2.67, 0.29, "Common"),
    ("Bronchiolitis", "Chest retractions", 0.60, 0.90, 6.0, 0.44, "Severity marker"),
    
    # Croup
    ("Croup (laryngotracheobronchitis)", "Barking cough", 0.85, 0.95, 17.0, 0.16, "Pathognomonic"),
    ("Croup (laryngotracheobronchitis)", "Stridor", 0.60, 0.98, 30.0, 0.41, "Highly specific"),
    
    # Common Cold
    ("Acute upper respiratory infection (common cold)", "Rhinorrhea (runny nose)", 0.90, 0.30, 1.29, 0.33, "Very common"),
    ("Acute upper respiratory infection (common cold)", "Nasal congestion", 0.85, 0.35, 1.31, 0.43, "Common"),
    ("Acute upper respiratory infection (common cold)", "Sneezing", 0.80, 0.50, 1.6, 0.40, "Common"),
    
    # Influenza
    ("Influenza", "Fever", 0.85, 0.40, 1.42, 0.38, "Common"),
    ("Influenza", "Myalgia (muscle aches)", 0.60, 0.75, 2.4, 0.53, "Suggestive"),
    ("Influenza", "Malaise/fatigue", 0.70, 0.60, 1.75, 0.50, "Common"),
    
    # Conjunctivitis
    ("Conjunctivitis", "Eye redness", 0.95, 0.70, 3.17, 0.07, "Highly sensitive"),
    ("Conjunctivitis", "Eye discharge", 0.80, 0.85, 5.33, 0.24, "Common"),
    
    # Hand, Foot, Mouth Disease
    ("Hand, foot and mouth disease", "Oral ulcers", 0.90, 0.85, 6.0, 0.12, "Characteristic"),
    ("Hand, foot and mouth disease", "Vesicular rash on hands", 0.80, 0.90, 8.0, 0.22, "Classic"),
    ("Hand, foot and mouth disease", "Fever", 0.70, 0.50, 1.4, 0.60, "Common"),
]


def create_evidence_csv(output_path: Path = Path("evidence_template.csv")):
    """Create a CSV file with sample evidence data."""
    fieldnames = [
        "disease_name",
        "phenotype_label",
        "age_min_months",
        "age_max_months",
        "setting",
        "region",
        "sensitivity",
        "specificity",
        "lr_pos",
        "lr_neg",
        "source_pmid",
        "guideline_org",
        "year",
        "study_design",
        "evidence_grade",
        "extraction_date",
        "notes",
    ]
    
    rows = []
    for disease, phenotype, sens, spec, lr_pos, lr_neg, notes in SAMPLE_EVIDENCE:
        row = {
            "disease_name": disease,
            "phenotype_label": phenotype,
            "age_min_months": "",
            "age_max_months": "",
            "setting": "",
            "region": "",
            "sensitivity": str(sens),
            "specificity": str(spec),
            "lr_pos": str(lr_pos),
            "lr_neg": str(lr_neg),
            "source_pmid": "",
            "guideline_org": "",
            "year": "",
            "study_design": "",
            "evidence_grade": "",
            "extraction_date": "",
            "notes": notes,
        }
        rows.append(row)
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Created {output_path} with {len(rows)} evidence rows")
    print(f"Covering {len(set(r['disease_name'] for r in rows))} diseases")


if __name__ == "__main__":
    import sys
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("evidence_template.csv")
    create_evidence_csv(output)
    print("\nNext steps:")
    print("1. Review the generated evidence_template.csv")
    print("2. Load it into the database: python load_evidence.py evidence_template.csv")
    print("3. Re-run autotest: python autotest_diseases.py --max_steps 6 --min_evidence 2")

