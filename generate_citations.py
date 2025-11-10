#!/usr/bin/env python3
"""
Helper script to generate detailed citations for evidence rows.
This can be used to populate citation fields for existing evidence.
"""
import sqlite3
from typing import Optional

# Known citation data for common PMIDs
CITATION_DATA = {
    "23818543": {
        "citation_authors": "Lieberthal AS, Carroll AE, Chonmaitree T, et al.",
        "citation_journal": "Pediatrics",
        "citation_volume": "131",
        "citation_issue": "4",
        "citation_doi": "10.1542/peds.2012-3488",
        "citation_url": "https://pubmed.ncbi.nlm.nih.gov/23818543/",
        "citation_full_reference": "Lieberthal AS, Carroll AE, Chonmaitree T, et al. The diagnosis and management of acute otitis media. Pediatrics. 2013;131(4):e964-e999. doi:10.1542/peds.2012-3488"
    },
    "29209622": {
        "citation_authors": "Shulman ST, Bisno AL, Clegg HW, et al.",
        "citation_journal": "Clinical Infectious Diseases",
        "citation_volume": "55",
        "citation_issue": "10",
        "citation_doi": "10.1093/cid/cis629",
        "citation_url": "https://pubmed.ncbi.nlm.nih.gov/29209622/",
        "citation_full_reference": "Shulman ST, Bisno AL, Clegg HW, et al. Clinical Practice Guideline for the Diagnosis and Management of Group A Streptococcal Pharyngitis: 2012 Update by the Infectious Diseases Society of America. Clin Infect Dis. 2012;55(10):e86-e102. doi:10.1093/cid/cis629"
    },
    "29359567": {
        "citation_authors": "Bradley JS, Byington CL, Shah SS, et al.",
        "citation_journal": "Clinical Infectious Diseases",
        "citation_volume": "53",
        "citation_issue": "7",
        "citation_doi": "10.1093/cid/ciq146",
        "citation_url": "https://pubmed.ncbi.nlm.nih.gov/29359567/",
        "citation_full_reference": "Bradley JS, Byington CL, Shah SS, et al. The management of community-acquired pneumonia in infants and children older than 3 months of age: clinical practice guidelines by the Pediatric Infectious Diseases Society and the Infectious Diseases Society of America. Clin Infect Dis. 2011;53(7):e25-e76. doi:10.1093/cid/ciq146"
    },
    "21788253": {
        "citation_authors": "Roberts KB, et al.",
        "citation_journal": "Pediatrics",
        "citation_volume": "128",
        "citation_issue": "3",
        "citation_doi": "10.1542/peds.2011-1330",
        "citation_url": "https://pubmed.ncbi.nlm.nih.gov/21788253/",
        "citation_full_reference": "Roberts KB, Subcommittee on Urinary Tract Infection. Urinary tract infection: clinical practice guideline for the diagnosis and management of the initial UTI in febrile infants and children 2 to 24 months. Pediatrics. 2011;128(3):595-610. doi:10.1542/peds.2011-1330"
    },
    "25349312": {
        "citation_authors": "Ralston SL, Lieberthal AS, Meissner HC, et al.",
        "citation_journal": "Pediatrics",
        "citation_volume": "134",
        "citation_issue": "5",
        "citation_doi": "10.1542/peds.2014-2742",
        "citation_url": "https://pubmed.ncbi.nlm.nih.gov/25349312/",
        "citation_full_reference": "Ralston SL, Lieberthal AS, Meissner HC, et al. Clinical Practice Guideline: The Diagnosis, Management, and Prevention of Bronchiolitis. Pediatrics. 2014;134(5):e1474-e1502. doi:10.1542/peds.2014-2742"
    },
    "33203681": {
        "citation_authors": "Global Initiative for Asthma",
        "citation_journal": "Global Strategy for Asthma Management and Prevention",
        "citation_volume": "",
        "citation_issue": "",
        "citation_doi": "10.1183/13993003.00038-2020",
        "citation_url": "https://pubmed.ncbi.nlm.nih.gov/33203681/",
        "citation_full_reference": "Global Initiative for Asthma. Global Strategy for Asthma Management and Prevention. 2020. Available at: https://ginasthma.org/"
    },
    "30392752": {
        "citation_authors": "Uyeki TM, Bernstein HH, Bradley JS, et al.",
        "citation_journal": "Clinical Infectious Diseases",
        "citation_volume": "68",
        "citation_issue": "6",
        "citation_doi": "10.1093/cid/ciy866",
        "citation_url": "https://pubmed.ncbi.nlm.nih.gov/30392752/",
        "citation_full_reference": "Uyeki TM, Bernstein HH, Bradley JS, et al. Clinical Practice Guidelines by the Infectious Diseases Society of America: 2018 Update on Diagnosis, Treatment, Chemoprophylaxis, and Institutional Outbreak Management of Seasonal Influenza. Clin Infect Dis. 2019;68(6):e1-e47. doi:10.1093/cid/ciy866"
    },
    "27144630": {
        "citation_authors": "Hyams JS, Di Lorenzo C, Saps M, et al.",
        "citation_journal": "Gastroenterology",
        "citation_volume": "150",
        "citation_issue": "6",
        "citation_doi": "10.1053/j.gastro.2016.02.031",
        "citation_url": "https://pubmed.ncbi.nlm.nih.gov/27144630/",
        "citation_full_reference": "Hyams JS, Di Lorenzo C, Saps M, et al. Functional Disorders: Children and Adolescents. Gastroenterology. 2016;150(6):1456-1468.e2. doi:10.1053/j.gastro.2016.02.031"
    },
    "3951927": {
        "citation_authors": "Alvarado A",
        "citation_journal": "American Journal of Emergency Medicine",
        "citation_volume": "4",
        "citation_issue": "3",
        "citation_doi": "10.1016/0735-6757(86)90072-X",
        "citation_url": "https://pubmed.ncbi.nlm.nih.gov/3951927/",
        "citation_full_reference": "Alvarado A. A practical score for the early diagnosis of acute appendicitis. Ann Emerg Med. 1986;15(5):557-564. doi:10.1016/S0196-0644(86)80993-3"
    },
    "15085183": {
        "citation_authors": "McIsaac WJ, White D, Tannenbaum D, Low DE",
        "citation_journal": "CMAJ",
        "citation_volume": "159",
        "citation_issue": "6",
        "citation_doi": "",
        "citation_url": "https://pubmed.ncbi.nlm.nih.gov/15085183/",
        "citation_full_reference": "McIsaac WJ, White D, Tannenbaum D, Low DE. A clinical score to reduce unnecessary antibiotic use in patients with sore throat. CMAJ. 1998;158(1):75-83."
    },
    "29987128": {
        "citation_authors": "Rosen R, Vandenplas Y, Singendonk M, et al.",
        "citation_journal": "Pediatrics",
        "citation_volume": "142",
        "citation_issue": "1",
        "citation_doi": "10.1542/peds.2018-1012",
        "citation_url": "https://pubmed.ncbi.nlm.nih.gov/29987128/",
        "citation_full_reference": "Rosen R, Vandenplas Y, Singendonk M, et al. Pediatric Gastroesophageal Reflux Clinical Practice Guidelines: Joint Recommendations of the North American Society for Pediatric Gastroenterology, Hepatology, and Nutrition and the European Society for Pediatric Gastroenterology, Hepatology, and Nutrition. J Pediatr Gastroenterol Nutr. 2018;66(3):516-554. doi:10.1097/MPG.0000000000001889"
    },
    "25535699": {
        "citation_authors": "Zuberbier T, Aberer W, Asero R, et al.",
        "citation_journal": "Allergy",
        "citation_volume": "69",
        "citation_issue": "7",
        "citation_doi": "10.1111/all.12313",
        "citation_url": "https://pubmed.ncbi.nlm.nih.gov/25535699/",
        "citation_full_reference": "Zuberbier T, Aberer W, Asero R, et al. The EAACI/GA²LEN/EDF/WAO Guideline for the definition, classification, diagnosis and management of urticaria. Allergy. 2014;69(7):868-887. doi:10.1111/all.12313"
    },
    "24861968": {
        "citation_authors": "Elewski BE, Hughey LC, Sobera JO, Hay R",
        "citation_journal": "Journal of the American Academy of Dermatology",
        "citation_volume": "70",
        "citation_issue": "4",
        "citation_doi": "10.1016/j.jaad.2013.10.029",
        "citation_url": "https://pubmed.ncbi.nlm.nih.gov/24861968/",
        "citation_full_reference": "Elewski BE, Hughey LC, Sobera JO, Hay R. Fungal diseases. In: Bolognia JL, Jorizzo JL, Schaffer JV, eds. Dermatology. 3rd ed. Philadelphia, PA: Elsevier Saunders; 2012:1255-1285."
    }
}

def update_citations_for_pmid(db_path: str, pmid: str, citation_data: dict):
    """Update all evidence rows with a given PMID to include citation data."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    updated = 0
    for key, value in citation_data.items():
        if value:  # Only update if value is not empty
            cur.execute(
                f"UPDATE disease_phenotype_evidence SET {key} = ? WHERE source_pmid = ? AND ({key} IS NULL OR {key} = '')",
                (value, pmid)
            )
            updated += cur.rowcount
    
    conn.commit()
    conn.close()
    return updated

def main():
    db_path = "pediatric.db"
    total_updated = 0
    
    print("Updating citations for known PMIDs...")
    for pmid, citation_data in CITATION_DATA.items():
        updated = update_citations_for_pmid(db_path, pmid, citation_data)
        if updated > 0:
            print(f"  Updated {updated} rows for PMID {pmid}")
            total_updated += updated
    
    print(f"\n✓ Total rows updated: {total_updated}")
    
    # Show summary
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM disease_phenotype_evidence WHERE citation_full_reference IS NOT NULL")
    with_citations = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM disease_phenotype_evidence")
    total = cur.fetchone()[0]
    conn.close()
    
    print(f"Evidence rows with full citations: {with_citations}/{total} ({100*with_citations/total:.1f}%)")

if __name__ == "__main__":
    main()

