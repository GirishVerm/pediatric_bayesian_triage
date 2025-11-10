-- Add detailed academic citation fields to disease_phenotype_evidence table
-- This allows precise citations for academic papers

ALTER TABLE disease_phenotype_evidence ADD COLUMN citation_page TEXT;
ALTER TABLE disease_phenotype_evidence ADD COLUMN citation_table TEXT;
ALTER TABLE disease_phenotype_evidence ADD COLUMN citation_figure TEXT;
ALTER TABLE disease_phenotype_evidence ADD COLUMN citation_section TEXT;
ALTER TABLE disease_phenotype_evidence ADD COLUMN citation_doi TEXT;
ALTER TABLE disease_phenotype_evidence ADD COLUMN citation_url TEXT;
ALTER TABLE disease_phenotype_evidence ADD COLUMN citation_authors TEXT;
ALTER TABLE disease_phenotype_evidence ADD COLUMN citation_journal TEXT;
ALTER TABLE disease_phenotype_evidence ADD COLUMN citation_volume TEXT;
ALTER TABLE disease_phenotype_evidence ADD COLUMN citation_issue TEXT;
ALTER TABLE disease_phenotype_evidence ADD COLUMN citation_full_reference TEXT;
ALTER TABLE disease_phenotype_evidence ADD COLUMN citation_data_location TEXT; -- e.g., "Table 2, row 3" or "Figure 1, panel B"

