-- Ontology-backed schema for pediatric diagnosis

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS diseases (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  snomed_fsn TEXT,
  snomed_code TEXT,
  icd10_code TEXT,
  description TEXT,
  triage_severity REAL,
  notes TEXT,
  UNIQUE(name)
);

CREATE TABLE IF NOT EXISTS phenotypes (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  type TEXT, -- symptom, sign, lab, vital, imaging
  snomed_code TEXT,
  hpo_code TEXT,
  loinc_code TEXT,
  UNIQUE(hpo_code) -- prefer HPO as canonical for phenotypes
);

CREATE TABLE IF NOT EXISTS disease_phenotype_evidence (
  id INTEGER PRIMARY KEY,
  disease_id INTEGER NOT NULL REFERENCES diseases(id) ON DELETE CASCADE,
  phenotype_id INTEGER NOT NULL REFERENCES phenotypes(id) ON DELETE CASCADE,
  age_min_months INTEGER,
  age_max_months INTEGER,
  setting TEXT, -- ED, primary, inpatient
  region TEXT,
  source_pmid TEXT,
  guideline_org TEXT,
  year INTEGER,
  study_design TEXT,
  evidence_grade TEXT,
  sensitivity REAL,
  specificity REAL,
  lr_pos REAL,
  lr_neg REAL,
  prevalence REAL,
  extraction_date TEXT,
  notes TEXT,
  -- Detailed academic citation fields
  citation_page TEXT,
  citation_table TEXT,
  citation_figure TEXT,
  citation_section TEXT,
  citation_doi TEXT,
  citation_url TEXT,
  citation_authors TEXT,
  citation_journal TEXT,
  citation_volume TEXT,
  citation_issue TEXT,
  citation_full_reference TEXT,
  citation_data_location TEXT, -- e.g., "Table 2, row 3" or "Figure 1, panel B"
  UNIQUE(disease_id, phenotype_id, age_min_months, age_max_months, setting, region, source_pmid)
);

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
);

CREATE INDEX IF NOT EXISTS idx_evidence_disease ON disease_phenotype_evidence(disease_id);
CREATE INDEX IF NOT EXISTS idx_evidence_phenotype ON disease_phenotype_evidence(phenotype_id);
