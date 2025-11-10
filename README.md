## Pediatric Diagnosis Assistant (IATRO)

A lightweight, ontology-backed pediatric disease diagnosis assistant. It ingests curated disease–phenotype evidence into a local SQLite database and runs an evidence-driven inference loop to suggest the most informative next symptoms and converge to a likely diagnosis.

### Highlights
- **Ontology-backed schema**: Uses HPO for phenotypes and can store SNOMED/LOINC codes.
- **Evidence-driven inference**: Posterior updates using positive likelihood ratios; dynamic selection of next questions.
- **Curated inputs**: Start with a small curated CSV dataset and expand with evidence rows.
- **Local-first**: Simple SQLite DB; easy to run and iterate.

## Repository Contents
- **`schema_ontology.sql`**: Creates tables `diseases`, `phenotypes`, `disease_phenotype_evidence`, and `disease_priors` with indexes and uniqueness constraints.
- **`fill_hpo_ids.py`**: Looks up HPO IDs for phenotype labels via the EBI OLS API and writes a normalized CSV.
- **`load_top20_into_db.py`**: Ensures the schema and loads curated disease–phenotype rows (with optional HPO codes) into the DB.
- **`load_evidence.py`**: Upserts detailed evidence rows (sens/spec/LR, source metadata) from `evidence_template.csv` into `disease_phenotype_evidence`.
- **`inference.py`**: Implements the interactive inference loop: computes posteriors, suggests next symptoms, explains terms in plain language, and applies coverage/scarcity/cluster boosts.
- **`autotest_diseases.py`**: Simulates runs to evaluate the convergence behavior across diseases.
- **`evidence_template.csv`**: Minimal template for ingesting evidence (headers only; add your rows here).
- **`top20_disease_phenotypes.csv`**: Curated starter dataset of disease–phenotype pairs (without HPO). Use `fill_hpo_ids.py` to create an HPO-enriched file.
- **`requirements.txt`**: External Python dependency pinning.

Note: The main database file (`pediatric.db`) is tracked in version control to preserve the well-performing model (86/87 convergence). Backup databases are excluded.

## Quick Start

### 1) Environment
- Requires **Python 3.10+**.
- Install dependencies:
```bash
pip install -r requirements.txt
```

### 2) Prepare Data
- Option A: Use curated dataset as-is (phenotypes without HPO). This works; HPO is optional.
- Option B: Enrich curated dataset with HPO IDs:
```bash
python fill_hpo_ids.py top20_disease_phenotypes.csv top20_disease_phenotypes_hpo.csv
```

### 3) Initialize the Database and Load Curated Rows
- If using the HPO-enriched file:
```bash
python load_top20_into_db.py top20_disease_phenotypes_hpo.csv pediatric.db
```
- If using the plain curated file:
```bash
python load_top20_into_db.py top20_disease_phenotypes.csv pediatric.db
```

### 4) Load Evidence Rows (optional but recommended)
- Add rows to `evidence_template.csv`, then run:
```bash
python load_evidence.py evidence_template.csv pediatric.db
```

### 5) Run Inference
- Preview recommended next symptoms (top-N):
```bash
python inference.py --preview 10
```
- Interactive CLI:
```bash
python inference.py
```

### 6) Auto-test (simulate convergence)
```bash
python autotest_diseases.py --max_steps 6 --min_evidence 2
```

## Current Status (November 2025)

### Performance Metrics
- **Total Diseases**: 87 (merged from original 67 + 20 new diagnosable diseases)
- **Convergence Rate**: 86/87 (98.9%) - 1 disease skipped due to insufficient evidence
- **Evidence Rows**: 760 (all validated from published sources with PMIDs and detailed citations)
- **Phenotypes**: 554 unique symptom terms
- **Published Sources**: Multiple guideline organizations (AAP, AHA, IDSA, ISPAD, ILAE, CDC, ECCO, CF Foundation, etc.)
- **Database**: `pediatric.db` - Best performing model preserved in version control

### Converging Diseases (86/87)

**Original 26 Diseases:**

1. Acute bacterial sinusitis
2. Acute gastroenteritis (infectious)
3. Acute otitis media
4. Acute upper respiratory infection (common cold)
5. Allergic rhinitis
6. Appendicitis
7. Asthma exacerbation
8. Atopic dermatitis (eczema)
9. Bronchiolitis
10. Community-acquired pneumonia
11. Conjunctivitis
12. Constipation
13. Croup (laryngotracheobronchitis)
14. Fifth disease (erythema infectiosum)
15. Hand-foot-and-mouth disease
16. Impetigo
17. Influenza
18. Miliaria (heat rash)
19. Otitis externa (swimmer's ear)
20. Roseola infantum (exanthema subitum)
21. Streptococcal pharyngitis
22. Tinea corporis (ringworm)
23. Urinary tract infection
24. Urticaria (hives)
25. Varicella (chickenpox)
26. Viral pharyngitis (non-strep)

**New 17 Diseases (from first merge):**
27. Kawasaki Disease
28. Diabetes
29. Epilepsy
30. Head Lice
31. Pinworms
32. Thrush
33. Acne
34. Endocarditis
35. Myocarditis
36. Pericarditis
37. Pancreatitis
38. Sickle Cell Disease
39. Cystic Fibrosis
40. Ulcerative Colitis
41. Inflammatory Bowel Disease
42. Viral Hepatitis
43. Gallstones

**New 20 Diseases (from second merge):**
44. Acute Lymphoblastic Leukemia
45. Acute Myeloid Leukemia
46. Anxiety
47. Aplastic Anemia
48. Arrhythmia
49. Attention Deficit Hyperactivity Disorder
50. Autism Spectrum Disorder (ASD)
51. Brain Tumors
52. Cardiomyopathy
53. Congenital Adrenal Hyperplasia
54. Depression
55. Heart Failure
56. Hemophilia
57. Hodgkin Lymphoma
58. Hydrocephalus
59. Intussusception
60. Neuroblastoma
61. Non-Hodgkin Lymphoma
62. Obsessive Compulsive Disorder
63. Retinoblastoma

### Remaining Challenges (1/87)

**1 disease skipped** due to insufficient evidence-backed symptoms (requires at least 2 evidence entries with LR+ values).

## Current Architecture
- **Data store**: `SQLite` file `pediatric.db` (tracked in git to preserve best model), schema in `schema_ontology.sql`. The merged database combines 67 original diseases with 20 new diagnosable diseases for a total of 87 diseases, schema in `schema_ontology.sql`.
  - `diseases(id, name, snomed_fsn, snomed_code, icd10_code, triage_severity, description, notes)`
  - `phenotypes(id, name, type, snomed_code, hpo_code, loinc_code)`
  - `disease_phenotype_evidence(...)`: age ranges, setting/region, source metadata, sens/spec, LR+, LR−, notes.
  - `disease_priors(...)`: optional per-disease priors by age/region.
- **Ingestion**:
  - `fill_hpo_ids.py`: HPO lookup via OLS; normalizes CSV headers; fills `hpo_id` when missing.
  - `load_top20_into_db.py`: Ensures schema; upserts diseases and phenotypes; links stub evidence rows.
  - `load_evidence.py`: Upserts detailed evidence rows; derives LR if only sens/spec provided.
  - `load_priors.py`: Loads disease prior probabilities from CSV.
- **Inference** (`inference.py`):
  - Loads diseases, priors, and evidence map; normalizes priors.
  - Picks next symptoms by expected positive information gain (`positive_score`).
  - Considers top 15 symptoms per iteration in interactive mode (top 30 in autotest with fallback search).
  - Uses improved symptom selection: lower LR+ threshold (1.0), selects highest LR+ for target disease, and searches all available symptoms if needed.
  - Updates posteriors on positive findings with coverage penalty and dynamic boosts (cluster/scarcity/stage).
  - Stopping criteria based on confidence, evidence hits per top disease, and posterior gap.
  - Plain-language explanations for common symptoms.
  - Skip functionality allows browsing symptom options without penalty.
- **Testing**: `autotest_diseases.py` simulates target disease runs and prints convergence stats.

## Goal Architecture (Roadmap)
- **Data ingestion pipeline**:
  - Automated extraction from guidelines, PubMed, and trusted clinical sources; standardized mapping to HPO/SNOMED/LOINC.
  - Evidence quality grading and versioned provenance.
- **Knowledge base**:
  - Move from SQLite to `PostgreSQL` with migrations; add audit trails and richer constraints.
  - Expand `disease_priors` with age stratification, regional prevalence, and context-aware priors.
- **Inference service**:
  - Package inference as a stateless API (REST/GraphQL) with documented endpoints.
  - Extend to handle negative findings and multi-signal modalities (labs, vitals, imaging).
  - Introduce information-theoretic question selection and multi-armed strategies.
- **User interfaces**:
  - Clinician-facing web app for triage with clear explanations and guardrails.
  - Family-facing "plain language" symptom helper and guidance.
- **Ops & Governance**:
  - Observability (logs/metrics), evaluation harness, and continuous curation.
  - Privacy, safety, and ethical review; domain expert validation workflows.

## Data and Sources Used

### Evidence Sources
All evidence rows are validated from published sources with specific PMIDs:
- **American Academy of Pediatrics (AAP)**: Clinical Practice Guidelines (2011-2023)
  - Acute otitis media (PMID 23818543)
  - Urinary tract infection (PMID 21788253)
  - Acute bacterial sinusitis (PMID 23796742)
  - Bronchiolitis (PMID 25349312)
  - Gastroesophageal reflux (PMID 29987128)
- **Infectious Diseases Society of America (IDSA)**: Guidelines for pharyngitis, influenza, pneumonia
  - Streptococcal pharyngitis (PMID 29209622)
  - Influenza (PMID 30392752)
- **World Health Organization (WHO)**: Pneumonia diagnostic criteria (PMID 29359567)
- **European Society for Pediatric Gastroenterology (ESPGHAN)**: Gastroenteritis guidelines (PMID 25349300)
- **Global Initiative for Asthma (GINA)**: Asthma diagnostic criteria (PMID 33203681)
- **Annals of Family Medicine**: Sinusitis systematic review (2005)
- **Rome IV Criteria**: Constipation diagnostic criteria (PMID 27144630)
- **International Headache Society (IHS)**: Headache diagnostic criteria (PMID 29368949)
- **Alvarado Score**: Appendicitis clinical decision rule (PMID 3951927)
- **Centor/McIsaac Criteria**: Pharyngitis clinical decision rule (PMID 15085183)
- **EAACI/AAAAI**: Urticaria guidelines (PMID 25535699)
- **AAD**: Dermatology guidelines (PMID 24861968)
- **AAP Red Book**: Clinical references for viral exanthems and common conditions

### Technical Resources
- **EBI Ontology Lookup Service (OLS)**: `https://www.ebi.ac.uk/ols4/api`
- **Human Phenotype Ontology (HPO)**: `https://hpo.jax.org/app/`
- **SNOMED CT** (for diseases/phenotypes coding): `https://www.snomed.org/snomed-ct`
- **LOINC** (for lab/imaging coding when applicable): `https://loinc.org/`
- **SQLite**: `https://sqlite.org/`
- **Python**: `https://www.python.org/`

All evidence rows include specific provenance: `source_pmid`, `guideline_org`, `year`, `study_design`, `evidence_grade`.

## How Model Parameters Are Determined

### Disease Priors
Disease priors (pre-test probabilities) are determined from:
- **Clinical estimates** based on pediatric practice prevalence
- **Age-stratified priors** where applicable (e.g., bronchiolitis more common in 0-12 months)
- **Setting-specific priors** (e.g., asthma exacerbation higher in ED vs. primary care)
- **Balanced distribution** to prevent any single disease from dominating initial probabilities
- Priors are stored in `disease_priors.csv` and loaded via `load_priors.py`

### Triage Severity
Triage severity values (1.0-5.0 scale) are assigned based on:
- **Clinical urgency**: Life-threatening conditions (e.g., appendicitis, pneumonia) have higher severity
- **Potential for complications**: Conditions requiring prompt treatment get higher values
- **Standard pediatric triage protocols**: Aligned with emergency department triage systems
- Stored in the `diseases` table as `triage_severity` field

### Sensitivity and Specificity
Sensitivity and specificity values are extracted from:
- **Published clinical guidelines**: AAP, IDSA, WHO guidelines provide validated sens/spec values
- **Systematic reviews and meta-analyses**: Pooled data from multiple studies
- **Clinical decision rules**: Validated tools like Alvarado score, Centor criteria, Rome IV
- **Primary research studies**: When available, values from peer-reviewed publications
- All values are documented with source PMIDs and evidence grades (A/B/C)

### Likelihood Ratios (LR+)
Positive likelihood ratios (LR+) are determined by:
- **Direct extraction**: When LR+ values are explicitly reported in guidelines or studies
- **Calculation from sens/spec**: LR+ = sensitivity / (1 - specificity) when only sens/spec available
- **Validation**: All calculated LR+ values are cross-checked against published ranges when available
- **Quality grading**: 
  - **Grade A**: From high-quality guidelines or systematic reviews
  - **Grade B**: From clinical guidelines or well-established findings
  - **Grade C**: From general clinical references or common knowledge
- LR+ values range from ~1.0 (non-specific) to 45+ (pathognomonic findings)

### Evidence Quality Assurance
- All evidence rows require either a **PMID** (PubMed ID) or reference to a recognized **guideline organization**
- Evidence extraction date is tracked for version control
- Notes field documents the specific source and context
- Low-quality or estimated values are excluded in favor of published, validated data

## GitHub Preparation
- A `.gitignore` is included to exclude backup DBs, caches, and large/raw CSVs. The main `pediatric.db` is tracked to preserve the well-performing model (86/87 convergence).
- Suggested initial commit workflow:
```bash
git init
git add -A
git commit -m "Initial cleaned repo: ontology schema, loaders, inference"
# Optional: set main branch and push to your remote
git branch -M main
git remote add origin <your_repo_url>
git push -u origin main
```

## Notes
- This repository is for research/prototyping only and is **not** a clinical decision aid.
- Please review and validate evidence and outputs with qualified domain experts before any real-world use.

