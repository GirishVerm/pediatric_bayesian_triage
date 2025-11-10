# New Database Setup - Top 20 Diagnosable Diseases

## Overview
Created a new database (`pediatric_new.db`) with 20 carefully selected diagnosable diseases that require symptom-based diagnostic reasoning (excluding obvious physical conditions).

## Selected Diseases

### High Severity (triage_severity = 3.0)
1. **Kawasaki Disease** - Classic diagnostic challenge
2. **Concussion** - Requires symptom assessment
3. **Endocarditis** - Serious infection
4. **Myocarditis** - Heart inflammation
5. **Pericarditis** - Heart condition
6. **Pancreatitis** - Abdominal condition
7. **Sickle Cell Disease** - Genetic but diagnosable
8. **Cystic Fibrosis** - Genetic but has symptoms
9. **Viral Hepatitis** - Liver infection

### Medium Severity (triage_severity = 2.0)
10. **Diabetes** - Common, symptom-based
11. **Epilepsy** - Seizure disorders
12. **Gallstones** - Common GI condition
13. **Crohn's Disease** - Inflammatory bowel
14. **Ulcerative Colitis** - Inflammatory bowel
15. **Inflammatory Bowel Disease** - General category

### Low Severity (triage_severity = 1.0)
16. **Head Lice** - Common parasitic
17. **Pinworms** - Common parasitic
18. **Thrush** - Fungal infection
19. **Warts** - Viral infection
20. **Acne** - Common skin condition

## Files Created

1. **`diseases_top20.csv`** - Disease definitions with triage severity
2. **`priors_top20.csv`** - Disease priors (initial estimates - need validation)
3. **`evidence_top20.csv`** - Empty evidence template
4. **`diseases_top20.txt`** - Simple list of selected diseases
5. **`load_diseases.py`** - Script to load diseases from CSV
6. **`setup_new_db.py`** - Complete database setup script

## Database Status

✅ **Database created**: `pediatric_new.db`
✅ **Schema loaded**: All tables initialized
✅ **Diseases loaded**: 20 diseases added
⏳ **Priors**: Need to be validated and loaded
⏳ **Evidence**: Need to be gathered and loaded

## Next Steps

### 1. Validate and Load Priors
```bash
# Review priors_top20.csv and update with validated prevalence data
python load_priors.py priors_top20.csv pediatric_new.db
```

### 2. Gather Evidence
- Research published sources for each disease
- Extract sensitivity, specificity, LR+, LR- values
- Add to `evidence_top20.csv` following the template format
- Include detailed citations (PMID, DOI, page numbers, etc.)

### 3. Load Evidence
```bash
python load_evidence.py evidence_top20.csv pediatric_new.db
```

### 4. Test Inference
```bash
python inference.py --db pediatric_new.db
python autotest_diseases.py --db pediatric_new.db
```

## Selection Criteria

Diseases were selected based on:
- ✅ Require diagnostic reasoning (not obvious physical conditions)
- ✅ Symptom-based diagnosis possible
- ✅ Common or important pediatric conditions
- ✅ Have potential for evidence-based diagnosis
- ❌ Excluded: Obvious physical conditions (sunburn, frostbite, etc.)
- ❌ Excluded: Structural/anatomical issues requiring imaging
- ❌ Excluded: Rare/complex conditions without clear symptom patterns
- ❌ Excluded: Mental/behavioral conditions (different diagnostic approach)

## Notes

- The original well-performing database (`pediatric.db` with 26/27 convergence) is preserved
- This new database is for experimentation with different disease sets
- Priors are initial estimates and should be validated with published sources
- Evidence needs to be gathered from published medical literature

