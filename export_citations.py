#!/usr/bin/env python3
"""
Export detailed citations for academic papers.
Generates properly formatted citations for all evidence used in the model.
"""
import sqlite3
import sys
from collections import defaultdict

def export_citations(db_path="pediatric.db", output_format="bibtex"):
    """Export citations in various formats for academic papers."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Get all unique citations
    cur.execute("""
        SELECT DISTINCT
            source_pmid,
            citation_full_reference,
            citation_doi,
            citation_url,
            citation_authors,
            citation_journal,
            citation_volume,
            citation_issue,
            year,
            guideline_org,
            COUNT(*) as evidence_count
        FROM disease_phenotype_evidence
        WHERE source_pmid IS NOT NULL AND source_pmid != ''
        GROUP BY source_pmid
        ORDER BY source_pmid
    """)
    
    citations = cur.fetchall()
    
    if output_format == "bibtex":
        print("% BibTeX citations for IATRO Pediatric Diagnosis Assistant")
        print("% Generated from evidence database\n")
        
        for row in citations:
            pmid, full_ref, doi, url, authors, journal, volume, issue, year, org, count = row
            if not authors or not journal:
                continue
            
            # Create BibTeX key from first author and year
            first_author = authors.split(',')[0].split()[0].lower() if authors else "unknown"
            bibtex_key = f"{first_author}{year}"
            
            print(f"@article{{{bibtex_key},")
            print(f"  title = {{[Extracted from evidence database]}},")
            print(f"  author = {{{authors}}},")
            print(f"  journal = {{{journal}}},")
            if volume:
                print(f"  volume = {{{volume}}},")
            if issue:
                print(f"  number = {{{issue}}},")
            if year:
                print(f"  year = {{{year}}},")
            if doi:
                print(f"  doi = {{{doi}}},")
            print(f"  pmid = {{{pmid}}},")
            if url:
                print(f"  url = {{{url}}},")
            print(f"  note = {{Used in {count} evidence rows}},")
            print(f"  full_reference = {{{full_ref}}},")
            print("}\n")
    
    elif output_format == "apa":
        print("APA Style Citations\n" + "="*80 + "\n")
        for row in citations:
            pmid, full_ref, doi, url, authors, journal, volume, issue, year, org, count = row
            if full_ref:
                print(f"{full_ref}")
                print(f"  Used in {count} evidence rows")
                print(f"  PMID: {pmid}\n")
            elif authors and journal and year:
                # Construct APA citation
                print(f"{authors} ({year}). [Title]. {journal}")
                if volume:
                    print(f"  Volume {volume}")
                if issue:
                    print(f"  Issue {issue}")
                print(f"  PMID: {pmid}")
                if doi:
                    print(f"  DOI: {doi}")
                print(f"  Used in {count} evidence rows\n")
    
    elif output_format == "detailed":
        print("Detailed Evidence Citations\n" + "="*80 + "\n")
        for row in citations:
            pmid, full_ref, doi, url, authors, journal, volume, issue, year, org, count = row
            print(f"PMID: {pmid}")
            if full_ref:
                print(f"Full Reference: {full_ref}")
            if authors:
                print(f"Authors: {authors}")
            if journal:
                print(f"Journal: {journal}")
            if volume:
                print(f"Volume: {volume}")
            if issue:
                print(f"Issue: {issue}")
            if year:
                print(f"Year: {year}")
            if doi:
                print(f"DOI: {doi}")
            if url:
                print(f"URL: {url}")
            print(f"Evidence Rows: {count}")
            print("-" * 80 + "\n")
    
    elif output_format == "csv":
        print("source_pmid,citation_full_reference,citation_doi,citation_url,citation_authors,citation_journal,citation_volume,citation_issue,year,guideline_org,evidence_count")
        for row in citations:
            print(",".join([str(x) if x else "" for x in row]))
    
    conn.close()

def export_evidence_with_citations(db_path="pediatric.db", disease_name=None):
    """Export evidence rows with detailed citations for a specific disease or all diseases."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    query = """
        SELECT 
            d.name as disease,
            p.name as phenotype,
            dpe.sensitivity,
            dpe.specificity,
            dpe.lr_pos,
            dpe.lr_neg,
            dpe.source_pmid,
            dpe.citation_full_reference,
            dpe.citation_data_location,
            dpe.citation_page,
            dpe.citation_table,
            dpe.citation_doi
        FROM disease_phenotype_evidence dpe
        JOIN diseases d ON dpe.disease_id = d.id
        JOIN phenotypes p ON dpe.phenotype_id = p.id
    """
    
    if disease_name:
        query += " WHERE d.name = ?"
        cur.execute(query, (disease_name,))
    else:
        cur.execute(query)
    
    rows = cur.fetchall()
    
    print("Disease | Phenotype | LR+ | Citation | Data Location")
    print("-" * 100)
    for row in rows:
        disease, phenotype, sens, spec, lr_pos, lr_neg, pmid, full_ref, data_loc, page, table, doi = row
        citation = full_ref if full_ref else f"PMID {pmid}" if pmid else "No citation"
        location = data_loc if data_loc else (f"Page {page}" if page else (f"Table {table}" if table else ""))
        
        print(f"{disease} | {phenotype} | {lr_pos} | {citation[:60]}... | {location}")
    
    conn.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Export citations for academic papers")
    parser.add_argument("--format", choices=["bibtex", "apa", "detailed", "csv"], default="detailed",
                       help="Output format for citations")
    parser.add_argument("--disease", help="Export citations for specific disease only")
    parser.add_argument("--evidence", action="store_true", help="Export evidence rows with citations")
    args = parser.parse_args()
    
    if args.evidence:
        export_evidence_with_citations(disease_name=args.disease)
    else:
        export_citations(output_format=args.format)

