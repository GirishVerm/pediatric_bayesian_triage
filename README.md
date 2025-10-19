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

Note: The generated database file (`pediatric.db`) and large/raw CSV dumps are intentionally excluded from version control.

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

## Current Architecture
- **Data store**: `SQLite` file `pediatric.db` (excluded from git), schema in `schema_ontology.sql`.
  - `diseases(id, name, snomed_fsn, snomed_code, icd10_code, triage_severity, description, notes)`
  - `phenotypes(id, name, type, snomed_code, hpo_code, loinc_code)`
  - `disease_phenotype_evidence(...)`: age ranges, setting/region, source metadata, sens/spec, LR+, LR−, notes.
  - `disease_priors(...)`: optional per-disease priors by age/region.
- **Ingestion**:
  - `fill_hpo_ids.py`: HPO lookup via OLS; normalizes CSV headers; fills `hpo_id` when missing.
  - `load_top20_into_db.py`: Ensures schema; upserts diseases and phenotypes; links stub evidence rows.
  - `load_evidence.py`: Upserts detailed evidence rows; derives LR if only sens/spec provided.
- **Inference** (`inference.py`):
  - Loads diseases, priors, and evidence map; normalizes priors.
  - Picks next symptoms by expected positive information gain (`positive_score`).
  - Updates posteriors on positive findings with coverage penalty and dynamic boosts (cluster/scarcity/stage).
  - Stopping criteria based on confidence, evidence hits per top disease, and posterior gap.
  - Plain-language explanations for common symptoms.
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

## Data and Sources Used So Far
- **EBI Ontology Lookup Service (OLS)**: `https://www.ebi.ac.uk/ols4/api`
- **Human Phenotype Ontology (HPO)**: `https://hpo.jax.org/app/`
- **SNOMED CT** (for diseases/phenotypes coding): `https://www.snomed.org/snomed-ct`
- **LOINC** (for lab/imaging coding when applicable): `https://loinc.org/`
- **SQLite**: `https://sqlite.org/`
- **Python**: `https://www.python.org/`

Curated clinical evidence underlying the starter CSVs was compiled from general pediatric references; as we expand, each row should include specific provenance (`source_pmid`, `guideline_org`, `year`, `study_design`, `evidence_grade`).

## GitHub Preparation
- A `.gitignore` is included to exclude local DBs, caches, and large/raw CSVs. Only templates and curated CSV inputs are tracked.
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
