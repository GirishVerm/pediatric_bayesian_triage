# Detailed Academic Citation Guide

This guide explains how to add detailed academic citations to evidence rows for precise referencing in academic papers.

## Citation Fields

The database now supports the following detailed citation fields:

### Basic Citation (Required)
- **`source_pmid`**: PubMed ID (e.g., "23818543")
- **`guideline_org`**: Organization name (e.g., "AAP", "IDSA")
- **`year`**: Publication year
- **`study_design`**: Type of study (e.g., "Guideline", "Systematic review", "Meta-analysis")

### Detailed Citation Fields (Optional but Recommended for Academic Papers)

1. **`citation_page`**: Page number(s) where the data appears (e.g., "e13-e14", "842-845")
2. **`citation_table`**: Table number/identifier (e.g., "Table 1", "Table 2")
3. **`citation_figure`**: Figure number/identifier (e.g., "Figure 1", "Figure 2, panel B")
4. **`citation_section`**: Section heading or number (e.g., "Section 2: Diagnosis", "Methods section")
5. **`citation_doi`**: Digital Object Identifier (e.g., "10.1542/peds.2012-3488")
6. **`citation_url`**: Direct URL to the source (e.g., "https://pubmed.ncbi.nlm.nih.gov/23818543/")
7. **`citation_authors`**: Author list (e.g., "Lieberthal AS et al.", "Shulman ST, Bisno AL, Clegg HW, et al.")
8. **`citation_journal`**: Journal name (e.g., "Pediatrics", "Clinical Infectious Diseases")
9. **`citation_volume`**: Journal volume number (e.g., "131", "55")
10. **`citation_issue`**: Journal issue number (e.g., "4", "10")
11. **`citation_full_reference`**: Complete formatted citation in standard academic format
12. **`citation_data_location`**: Specific location of the data within the source (e.g., "Table 1, row 3", "Figure 1, panel B", "Section 2.1, paragraph 2")

## Example: Complete Citation Entry

```csv
disease_name,phenotype_label,sensitivity,specificity,lr_pos,source_pmid,guideline_org,year,study_design,evidence_grade,extraction_date,notes,citation_page,citation_table,citation_section,citation_doi,citation_url,citation_authors,citation_journal,citation_volume,citation_issue,citation_full_reference,citation_data_location
Acute otitis media,Ear pain,0.85,0.75,3.4,23818543,AAP,2013,Guideline,A,2025-11-01,AAP Clinical Practice Guideline,e13-e14,Table 1,Section 2: Diagnosis,10.1542/peds.2012-3488,https://pubmed.ncbi.nlm.nih.gov/23818543/,Lieberthal AS et al.,Pediatrics,131,4,"Lieberthal AS, Carroll AE, Chonmaitree T, et al. The diagnosis and management of acute otitis media. Pediatrics. 2013;131(4):e964-e999. doi:10.1542/peds.2012-3488",Table 1: Diagnostic criteria for AOM
```

## Citation Format Standards

### Full Reference Format
Use standard academic citation format:
```
Author(s). Title. Journal. Year;Volume(Issue):Pages. doi:DOI
```

Example:
```
Lieberthal AS, Carroll AE, Chonmaitree T, et al. The diagnosis and management of acute otitis media. Pediatrics. 2013;131(4):e964-e999. doi:10.1542/peds.2012-3488
```

### Data Location Examples
- **Table**: "Table 1: Diagnostic criteria", "Table 2, row 3"
- **Figure**: "Figure 1", "Figure 2, panel B"
- **Section**: "Section 2: Diagnosis", "Section 2.1: Physical examination findings"
- **Page range**: "Pages 842-845"
- **Combined**: "Table 1, Section 2: Diagnosis, page e13"

## Querying Citations

### Get Full Citation for a Specific Evidence Row
```sql
SELECT 
    d.name as disease,
    p.name as phenotype,
    dpe.lr_pos,
    dpe.citation_full_reference,
    dpe.citation_data_location,
    dpe.citation_page,
    dpe.citation_table
FROM disease_phenotype_evidence dpe
JOIN diseases d ON dpe.disease_id = d.id
JOIN phenotypes p ON dpe.phenotype_id = p.id
WHERE d.name = 'Acute otitis media' AND p.name = 'Ear pain';
```

### Generate Academic Citation List
```sql
SELECT DISTINCT
    dpe.source_pmid,
    dpe.citation_full_reference,
    dpe.citation_doi,
    dpe.citation_url,
    COUNT(*) as evidence_count
FROM disease_phenotype_evidence dpe
WHERE dpe.citation_full_reference IS NOT NULL
GROUP BY dpe.source_pmid
ORDER BY dpe.source_pmid;
```

## Best Practices

1. **Always include `citation_full_reference`**: This provides the complete citation in standard format
2. **Use `citation_data_location`**: Specify exactly where in the source the data appears (table, figure, section)
3. **Include `citation_doi`**: Makes it easy to access the source
4. **Add `citation_page`**: Helps readers find the specific information quickly
5. **Use `citation_table` or `citation_figure`**: When data comes from a specific table or figure
6. **Be specific in `citation_data_location`**: Instead of just "Table 1", use "Table 1: Diagnostic criteria, row 2"

## Example: Updating Existing Evidence with Citations

To add detailed citations to existing evidence, create a CSV with the citation fields:

```csv
disease_name,phenotype_label,source_pmid,citation_full_reference,citation_data_location,citation_doi,citation_page
Acute otitis media,Ear pain,23818543,"Lieberthal AS, Carroll AE, Chonmaitree T, et al. The diagnosis and management of acute otitis media. Pediatrics. 2013;131(4):e964-e999. doi:10.1542/peds.2012-3488",Table 1: Diagnostic criteria for AOM,10.1542/peds.2012-3488,e13-e14
```

Then load it using `load_evidence.py` - it will update existing rows with the citation information.

