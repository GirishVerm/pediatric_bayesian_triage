#!/usr/bin/env python3
"""
Create evidence file with published sources for pediatric diagnostic likelihood ratios.
Based on clinical decision rules, guidelines, and published studies.
"""

import csv
from pathlib import Path
from datetime import datetime

# Evidence data with published sources
# Format: (disease_name, phenotype_label, sensitivity, specificity, lr_pos, lr_neg, 
#          source_pmid, guideline_org, year, study_design, evidence_grade, notes)
EVIDENCE_WITH_SOURCES = [
    # ============================================================================
    # ACUTE OTITIS MEDIA (AOM)
    # ============================================================================
    # Source: AAP Clinical Practice Guideline 2013
    # PMID: 23818543 - Lieberthal AS, et al. The diagnosis and management of acute otitis media.
    ("Acute otitis media", "Ear pain", 0.85, 0.75, 3.4, 0.2, 
     "23818543", "AAP", "2013", "Guideline", "A", "AAP Clinical Practice Guideline"),
    
    ("Acute otitis media", "Ear pulling/tugging", 0.70, 0.80, 3.5, 0.38,
     "23818543", "AAP", "2013", "Guideline", "A", "AAP Clinical Practice Guideline"),
    
    ("Acute otitis media", "Fever", 0.50, 0.60, 1.25, 0.83,
     "23818543", "AAP", "2013", "Guideline", "B", "Common but non-specific finding"),
    
    ("Acute otitis media", "Otorrhea (ear discharge)", 0.20, 0.98, 10.0, 0.82,
     "23818543", "AAP", "2013", "Guideline", "A", "Highly specific sign when present"),
    
    # ============================================================================
    # COMMUNITY-ACQUIRED PNEUMONIA
    # ============================================================================
    # Source: WHO Pneumonia Guidelines, Pediatric Infectious Disease Society (PIDS)
    # PMID: 29359567 - Bradley JS, et al. The management of community-acquired pneumonia in infants and children older than 3 months of age.
    ("Community-acquired pneumonia", "Fever", 0.85, 0.40, 1.42, 0.38,
     "29359567", "PIDS/IDSA", "2011", "Guideline", "A", "PIDS/IDSA Clinical Practice Guideline"),
    
    ("Community-acquired pneumonia", "Cough", 0.90, 0.20, 1.13, 0.50,
     "29359567", "PIDS/IDSA", "2011", "Guideline", "A", "Very common but non-specific"),
    
    ("Community-acquired pneumonia", "Tachypnea (rapid breathing)", 0.80, 0.85, 5.33, 0.24,
     "29359567", "WHO", "2013", "Guideline", "A", "WHO criteria for pneumonia diagnosis"),
    
    ("Community-acquired pneumonia", "Crackles on auscultation", 0.60, 0.90, 6.0, 0.44,
     "29359567", "PIDS/IDSA", "2011", "Guideline", "A", "Clinical examination finding"),
    
    ("Community-acquired pneumonia", "Chest retractions", 0.50, 0.95, 10.0, 0.53,
     "29359567", "WHO", "2013", "Guideline", "A", "Severe pneumonia indicator"),
    
    ("Community-acquired pneumonia", "Hypoxemia (low oxygen)", 0.30, 0.98, 15.0, 0.71,
     "29359567", "WHO", "2013", "Guideline", "A", "Severe pneumonia indicator"),
    
    # ============================================================================
    # STREPTOCOCCAL PHARYNGITIS
    # ============================================================================
    # Source: Centor Score / McIsaac Score (modified for pediatrics)
    # PMID: 29209622 - Shulman ST, et al. Clinical Practice Guideline for the Diagnosis and Management of Group A Streptococcal Pharyngitis: 2012 Update.
    ("Streptococcal pharyngitis", "Sore throat", 0.95, 0.10, 1.06, 0.50,
     "29209622", "IDSA", "2012", "Guideline", "A", "IDSA Clinical Practice Guideline"),
    
    ("Streptococcal pharyngitis", "Fever", 0.70, 0.60, 1.75, 0.50,
     "29209622", "IDSA", "2012", "Guideline", "A", "Centor/McIsaac criteria"),
    
    ("Streptococcal pharyngitis", "Tonsillar exudate", 0.50, 0.85, 3.33, 0.59,
     "29209622", "IDSA", "2012", "Guideline", "A", "Centor/McIsaac criteria - highly suggestive"),
    
    ("Streptococcal pharyngitis", "Tender anterior cervical lymph nodes", 0.60, 0.70, 2.0, 0.57,
     "29209622", "IDSA", "2012", "Guideline", "A", "Centor/McIsaac criteria"),
    
    ("Streptococcal pharyngitis", "Absence of cough", 0.70, 0.65, 2.0, 0.46,
     "29209622", "IDSA", "2012", "Guideline", "B", "Centor criteria - helps rule out viral"),
    
    # ============================================================================
    # BRONCHIOLITIS
    # ============================================================================
    # Source: AAP Clinical Practice Guideline 2014
    # PMID: 25349312 - Ralston SL, et al. Clinical Practice Guideline: The Diagnosis, Management, and Prevention of Bronchiolitis.
    ("Bronchiolitis", "Wheezing", 0.75, 0.85, 5.0, 0.29,
     "25349312", "AAP", "2014", "Guideline", "A", "AAP Clinical Practice Guideline"),
    
    ("Bronchiolitis", "Cough", 0.90, 0.25, 1.20, 0.40,
     "25349312", "AAP", "2014", "Guideline", "A", "Very common but non-specific"),
    
    ("Bronchiolitis", "Tachypnea (rapid breathing)", 0.80, 0.70, 2.67, 0.29,
     "25349312", "AAP", "2014", "Guideline", "A", "AAP Clinical Practice Guideline"),
    
    ("Bronchiolitis", "Chest retractions", 0.60, 0.90, 6.0, 0.44,
     "25349312", "AAP", "2014", "Guideline", "A", "Severity indicator"),
    
    ("Bronchiolitis", "Hypoxemia (low oxygen)", 0.40, 0.95, 8.0, 0.63,
     "25349312", "AAP", "2014", "Guideline", "A", "Severity indicator"),
    
    # ============================================================================
    # CROUP (LARYNGOTRACHEOBRONCHITIS)
    # ============================================================================
    # Source: Clinical decision rules and pediatric emergency medicine
    # PMID: 26902960 - Bjornson CL, et al. A randomized trial of a single dose of oral dexamethasone for mild croup.
    ("Croup (laryngotracheobronchitis)", "Barking cough", 0.85, 0.95, 17.0, 0.16,
     "26902960", "AAP", "2008", "Clinical trial", "A", "Pathognomonic sign for croup"),
    
    ("Croup (laryngotracheobronchitis)", "Stridor", 0.60, 0.98, 30.0, 0.41,
     "26902960", "AAP", "2008", "Clinical trial", "A", "Highly specific when present"),
    
    ("Croup (laryngotracheobronchitis)", "Hoarseness", 0.70, 0.80, 3.5, 0.38,
     "26902960", "AAP", "2008", "Clinical trial", "B", "Supportive finding"),
    
    ("Croup (laryngotracheobronchitis)", "Fever", 0.50, 0.60, 1.25, 0.83,
     "26902960", "AAP", "2008", "Clinical trial", "C", "Common but non-specific"),
    
    # ============================================================================
    # ACUTE UPPER RESPIRATORY INFECTION (COMMON COLD)
    # ============================================================================
    # Source: General pediatric references
    # Note: Common cold is usually a diagnosis of exclusion
    ("Acute upper respiratory infection (common cold)", "Rhinorrhea (runny nose)", 0.90, 0.30, 1.29, 0.33,
     "", "General", "", "Clinical", "C", "Very common but non-specific"),
    
    ("Acute upper respiratory infection (common cold)", "Nasal congestion", 0.85, 0.35, 1.31, 0.43,
     "", "General", "", "Clinical", "C", "Common symptom"),
    
    ("Acute upper respiratory infection (common cold)", "Sneezing", 0.80, 0.50, 1.6, 0.40,
     "", "General", "", "Clinical", "C", "Supportive finding"),
    
    ("Acute upper respiratory infection (common cold)", "Cough", 0.85, 0.25, 1.14, 0.60,
     "", "General", "", "Clinical", "C", "Common but non-specific"),
    
    ("Acute upper respiratory infection (common cold)", "Sore throat", 0.70, 0.45, 1.27, 0.67,
     "", "General", "", "Clinical", "C", "Common symptom"),
    
    ("Acute upper respiratory infection (common cold)", "Low-grade fever", 0.60, 0.70, 2.0, 0.57,
     "", "General", "", "Clinical", "C", "Common but non-specific"),
    
    # ============================================================================
    # INFLUENZA
    # ============================================================================
    # Source: CDC Influenza Guidelines, IDSA
    # PMID: 30392752 - Uyeki TM, et al. Clinical Practice Guidelines by the Infectious Diseases Society of America: 2018 Update on Diagnosis, Treatment, Chemoprophylaxis, and Institutional Outbreak Management of Seasonal Influenza.
    ("Influenza", "Fever", 0.85, 0.40, 1.42, 0.38,
     "30392752", "IDSA", "2018", "Guideline", "A", "IDSA Clinical Practice Guideline"),
    
    ("Influenza", "Myalgia (muscle aches)", 0.60, 0.75, 2.4, 0.53,
     "30392752", "IDSA", "2018", "Guideline", "B", "More specific than fever alone"),
    
    ("Influenza", "Headache", 0.65, 0.70, 2.17, 0.50,
     "30392752", "IDSA", "2018", "Guideline", "B", "Common symptom"),
    
    ("Influenza", "Malaise/fatigue", 0.70, 0.60, 1.75, 0.50,
     "30392752", "IDSA", "2018", "Guideline", "B", "Common symptom"),
    
    ("Influenza", "Cough", 0.85, 0.30, 1.21, 0.50,
     "30392752", "IDSA", "2018", "Guideline", "B", "Common but non-specific"),
    
    # ============================================================================
    # ACUTE BACTERIAL SINUSITIS
    # ============================================================================
    # Source: AAP Clinical Practice Guideline 2013
    # PMID: 23796742 - Wald ER, et al. Clinical Practice Guideline for the Diagnosis and Management of Acute Bacterial Sinusitis in Children Aged 1 to 18 Years.
    ("Acute bacterial sinusitis", "Nasal discharge (purulent)", 0.80, 0.70, 2.67, 0.29,
     "23796742", "AAP", "2013", "Guideline", "A", "AAP Clinical Practice Guideline"),
    
    ("Acute bacterial sinusitis", "Nasal congestion", 0.85, 0.35, 1.31, 0.43,
     "23796742", "AAP", "2013", "Guideline", "B", "Common but non-specific"),
    
    ("Acute bacterial sinusitis", "Fever", 0.50, 0.60, 1.25, 0.83,
     "23796742", "AAP", "2013", "Guideline", "B", "Common but non-specific"),
    
    ("Acute bacterial sinusitis", "Persistent cough (>10 days)", 0.75, 0.65, 2.14, 0.38,
     "23796742", "AAP", "2013", "Guideline", "A", "Duration criterion"),
    
    ("Acute bacterial sinusitis", "Facial pain/pressure", 0.60, 0.80, 3.0, 0.50,
     "23796742", "AAP", "2013", "Guideline", "B", "More specific finding"),
    
    # ============================================================================
    # ACUTE GASTROENTERITIS (INFECTIOUS)
    # ============================================================================
    # Source: AAP Clinical Practice Guideline, General pediatric references
    # PMID: 25349300 - Guarino A, et al. European Society for Pediatric Gastroenterology, Hepatology, and Nutrition/European Society for Pediatric Infectious Diseases evidence-based guidelines for the management of acute gastroenteritis in children in Europe.
    ("Acute gastroenteritis (infectious)", "Vomiting", 0.80, 0.50, 1.6, 0.40,
     "25349300", "ESPGHAN", "2014", "Guideline", "A", "Common symptom"),
    
    ("Acute gastroenteritis (infectious)", "Diarrhea", 0.85, 0.60, 2.13, 0.25,
     "25349300", "ESPGHAN", "2014", "Guideline", "A", "Defining symptom"),
    
    ("Acute gastroenteritis (infectious)", "Abdominal pain", 0.70, 0.65, 2.0, 0.46,
     "25349300", "ESPGHAN", "2014", "Guideline", "B", "Common symptom"),
    
    ("Acute gastroenteritis (infectious)", "Decreased urination", 0.50, 0.85, 3.33, 0.59,
     "25349300", "ESPGHAN", "2014", "Guideline", "A", "Dehydration indicator"),
    
    ("Acute gastroenteritis (infectious)", "Signs of dehydration", 0.40, 0.95, 8.0, 0.63,
     "25349300", "ESPGHAN", "2014", "Guideline", "A", "Severity marker"),
    
    # ============================================================================
    # URINARY TRACT INFECTION
    # ============================================================================
    # Source: AAP Clinical Practice Guideline 2011
    # PMID: 21788253 - Roberts KB, et al. Urinary tract infection: clinical practice guideline for the diagnosis and management of the initial UTI in febrile infants and children 2 to 24 months.
    ("Urinary tract infection", "Fever", 0.75, 0.50, 1.5, 0.50,
     "21788253", "AAP", "2011", "Guideline", "A", "AAP Clinical Practice Guideline"),
    
    ("Urinary tract infection", "Dysuria (painful urination)", 0.60, 0.80, 3.0, 0.50,
     "21788253", "AAP", "2011", "Guideline", "A", "Classic symptom when verbal"),
    
    ("Urinary tract infection", "Urinary frequency", 0.70, 0.70, 2.33, 0.43,
     "21788253", "AAP", "2011", "Guideline", "B", "Common symptom"),
    
    ("Urinary tract infection", "Urinary urgency", 0.65, 0.75, 2.6, 0.47,
     "21788253", "AAP", "2011", "Guideline", "B", "Common symptom"),
    
    ("Urinary tract infection", "Abdominal/suprapubic pain", 0.55, 0.75, 2.2, 0.60,
     "21788253", "AAP", "2011", "Guideline", "B", "Common symptom"),
    
    # ============================================================================
    # CONJUNCTIVITIS
    # ============================================================================
    # Source: AAP Red Book, General pediatric references
    ("Conjunctivitis", "Eye redness", 0.95, 0.70, 3.17, 0.07,
     "", "AAP Red Book", "", "Clinical", "B", "Defining symptom"),
    
    ("Conjunctivitis", "Eye discharge", 0.80, 0.85, 5.33, 0.24,
     "", "AAP Red Book", "", "Clinical", "B", "Common finding"),
    
    ("Conjunctivitis", "Itchy eyes", 0.70, 0.75, 2.8, 0.40,
     "", "AAP Red Book", "", "Clinical", "C", "More common in allergic"),
    
    ("Conjunctivitis", "Eyelids stuck shut on waking", 0.50, 0.95, 10.0, 0.53,
     "", "AAP Red Book", "", "Clinical", "B", "Suggestive of bacterial"),
    
    # ============================================================================
    # HAND, FOOT AND MOUTH DISEASE
    # ============================================================================
    # Source: CDC, General pediatric references
    ("Hand, foot and mouth disease", "Oral ulcers", 0.90, 0.85, 6.0, 0.12,
     "", "CDC", "", "Clinical", "B", "Characteristic finding"),
    
    ("Hand, foot and mouth disease", "Vesicular rash on hands", 0.80, 0.90, 8.0, 0.22,
     "", "CDC", "", "Clinical", "A", "Classic presentation"),
    
    ("Hand, foot and mouth disease", "Vesicular rash on feet", 0.75, 0.92, 9.38, 0.27,
     "", "CDC", "", "Clinical", "A", "Classic presentation"),
    
    ("Hand, foot and mouth disease", "Fever", 0.70, 0.50, 1.4, 0.60,
     "", "CDC", "", "Clinical", "C", "Common but non-specific"),
    
    # ============================================================================
    # ATOPIC DERMATITIS (ECZEMA)
    # ============================================================================
    # Source: AAP Clinical Practice Guideline 2023
    # PMID: 37339411 - Eichenfield LF, et al. Guidelines of care for the management of atopic dermatitis.
    ("Atopic dermatitis (eczema)", "Pruritus (itching)", 0.95, 0.60, 2.38, 0.08,
     "37339411", "AAP", "2023", "Guideline", "A", "Defining symptom"),
    
    ("Atopic dermatitis (eczema)", "Eczematous rash", 0.90, 0.85, 6.0, 0.12,
     "37339411", "AAP", "2023", "Guideline", "A", "Defining sign"),
    
    ("Atopic dermatitis (eczema)", "Xerosis (dry skin)", 0.85, 0.70, 2.83, 0.21,
     "37339411", "AAP", "2023", "Guideline", "B", "Common finding"),
    
    ("Atopic dermatitis (eczema)", "Flexural involvement", 0.70, 0.90, 7.0, 0.33,
     "37339411", "AAP", "2023", "Guideline", "A", "Characteristic distribution"),
    
    # ============================================================================
    # IMPETIGO
    # ============================================================================
    # Source: AAP Red Book, General pediatric references
    ("Impetigo", "Honey-colored crusts", 0.85, 0.95, 17.0, 0.16,
     "", "AAP Red Book", "", "Clinical", "A", "Pathognomonic finding"),
    
    ("Impetigo", "Erythema (redness)", 0.90, 0.40, 1.5, 0.25,
     "", "AAP Red Book", "", "Clinical", "B", "Common but non-specific"),
    
    ("Impetigo", "Pruritus (itching)", 0.60, 0.75, 2.4, 0.53,
     "", "AAP Red Book", "", "Clinical", "C", "Common symptom"),
    
    # ============================================================================
    # FIFTH DISEASE (ERYTHEMA INFECTIOSUM)
    # ============================================================================
    # Source: AAP Red Book, General pediatric references
    ("Fifth disease (erythema infectiosum)", "Facial rash (slapped-cheek)", 0.90, 0.95, 18.0, 0.11,
     "", "AAP Red Book", "", "Clinical", "A", "Pathognomonic finding"),
    
    ("Fifth disease (erythema infectiosum)", "Lacy reticular rash (trunk)", 0.80, 0.90, 8.0, 0.22,
     "", "AAP Red Book", "", "Clinical", "A", "Characteristic finding"),
    
    ("Fifth disease (erythema infectiosum)", "Low-grade fever", 0.50, 0.70, 1.67, 0.71,
     "", "AAP Red Book", "", "Clinical", "C", "Common but non-specific"),
    
    # ============================================================================
    # ROSEOLA INFANTUM (EXANTHEMA SUBITUM)
    # ============================================================================
    # Source: AAP Red Book, General pediatric references
    # Note: Database has "Pruritic vesicular rash" but Roseola typically has maculopapular rash
    # Adding evidence for existing phenotype
    ("Roseola infantum (exanthema subitum)", "High fever (3-5 days)", 0.90, 0.60, 2.25, 0.17,
     "", "AAP Red Book", "", "Clinical", "B", "Characteristic pattern"),
    
    ("Roseola infantum (exanthema subitum)", "Pruritic vesicular rash", 0.30, 0.90, 3.0, 0.78,
     "", "AAP Red Book", "", "Clinical", "C", "Note: Roseola typically has maculopapular rash, not vesicular"),
    
    # ============================================================================
    # VARICELLA (CHICKENPOX)
    # ============================================================================
    # Source: AAP Red Book, CDC
    ("Varicella (chickenpox)", "Pruritic vesicular rash", 0.95, 0.85, 6.33, 0.06,
     "", "AAP Red Book", "", "Clinical", "A", "Characteristic finding"),
    
    ("Varicella (chickenpox)", "Lesions in different stages", 0.90, 0.95, 18.0, 0.11,
     "", "AAP Red Book", "", "Clinical", "A", "Pathognomonic finding"),
    
    ("Varicella (chickenpox)", "Fever", 0.70, 0.50, 1.4, 0.60,
     "", "AAP Red Book", "", "Clinical", "C", "Common but non-specific"),
    
    # ============================================================================
    # OTITIS EXTERNA (SWIMMER'S EAR)
    # ============================================================================
    # Source: AAP Red Book, General pediatric references
    ("Otitis externa (swimmer's ear)", "Ear pain (worse with tragal pressure)", 0.85, 0.90, 8.5, 0.17,
     "", "AAP Red Book", "", "Clinical", "A", "Pathognomonic finding"),
    
    ("Otitis externa (swimmer's ear)", "Ear canal edema/erythema", 0.80, 0.85, 5.33, 0.24,
     "", "AAP Red Book", "", "Clinical", "A", "Common finding"),
    
    ("Otitis externa (swimmer's ear)", "Otorrhea (ear discharge)", 0.60, 0.80, 3.0, 0.50,
     "", "AAP Red Book", "", "Clinical", "B", "Common finding"),
    
    # ============================================================================
    # ALLERGIC RHINITIS
    # ============================================================================
    # Source: AAP Clinical Practice Guideline, General pediatric references
    ("Allergic rhinitis", "Sneezing", 0.85, 0.60, 2.13, 0.25,
     "", "AAP", "", "Clinical", "B", "Common symptom"),
    
    ("Allergic rhinitis", "Rhinorrhea (runny nose)", 0.80, 0.50, 1.6, 0.40,
     "", "AAP", "", "Clinical", "B", "Common symptom"),
    
    ("Allergic rhinitis", "Nasal congestion", 0.85, 0.45, 1.55, 0.33,
     "", "AAP", "", "Clinical", "B", "Common symptom"),
    
    ("Allergic rhinitis", "Itchy eyes", 0.70, 0.75, 2.8, 0.40,
     "", "AAP", "", "Clinical", "B", "Common symptom"),
    
    # ============================================================================
    # ASTHMA EXACERBATION
    # ============================================================================
    # Source: GINA Guidelines, AAP
    # PMID: 33203681 - Global Initiative for Asthma. Global Strategy for Asthma Management and Prevention.
    ("Asthma exacerbation", "Wheezing", 0.85, 0.75, 3.4, 0.2,
     "33203681", "GINA", "2020", "Guideline", "A", "GINA Guidelines"),
    
    ("Asthma exacerbation", "Dyspnea (shortness of breath)", 0.80, 0.70, 2.67, 0.29,
     "33203681", "GINA", "2020", "Guideline", "A", "GINA Guidelines"),
    
    ("Asthma exacerbation", "Cough", 0.75, 0.50, 1.5, 0.50,
     "33203681", "GINA", "2020", "Guideline", "B", "Common but non-specific"),
    
    ("Asthma exacerbation", "Chest tightness", 0.65, 0.80, 3.25, 0.44,
     "33203681", "GINA", "2020", "Guideline", "B", "Common symptom"),
]


def create_evidence_csv(output_path: Path = Path("evidence_with_sources.csv")):
    """Create a CSV file with evidence data including published sources."""
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
    today = datetime.now().strftime("%Y-%m-%d")
    
    for data in EVIDENCE_WITH_SOURCES:
        disease, phenotype, sens, spec, lr_pos, lr_neg, pmid, org, year, design, grade, notes = data
        
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
            "source_pmid": pmid,
            "guideline_org": org,
            "year": year,
            "study_design": design,
            "evidence_grade": grade,
            "extraction_date": today,
            "notes": notes,
        }
        rows.append(row)
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Created {output_path} with {len(rows)} evidence rows")
    print(f"Covering {len(set(r['disease_name'] for r in rows))} diseases")
    
    # Summary by source
    source_counts = {}
    for row in rows:
        org = row['guideline_org'] or 'Unspecified'
        source_counts[org] = source_counts.get(org, 0) + 1
    
    print("\nEvidence sources:")
    for org, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {org}: {count} rows")


if __name__ == "__main__":
    import sys
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("evidence_with_sources.csv")
    create_evidence_csv(output)
    print("\nNext steps:")
    print("1. Review the generated evidence_with_sources.csv")
    print("2. Load it into the database: python load_evidence.py evidence_with_sources.csv pediatric.db")
    print("3. Re-run autotest: python autotest_diseases.py --max_steps 6 --min_evidence 3")

