import os
import time
from datetime import datetime
import pandas as pd
from Bio import Entrez
from pathlib import Path

# --- Dynamic Path Configuration ---
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

# --- Configuration ---

# Fully populated list of companies and their search aliases.
COMPANY_SEARCH_TERMS = {
    # --- AI-Native Drug Discovery ---
    'Recursion': {"aliases": ["Recursion Pharmaceuticals", "Recursion"], "type": "affiliation"},
    'Relay Therapeutics': {"aliases": ["Relay Therapeutics"], "type": "affiliation"},
    'Schrodinger': {"aliases": ["Schrodinger Inc", "Schrodinger LLC"], "type": "affiliation"},
    'AbCellera': {"aliases": ["AbCellera Biologics", "AbCellera"], "type": "affiliation"},
    'Absci': {"aliases": ["Absci", "Absci Inc"], "type": "affiliation"},
    'Certara': {"aliases": ["Certara"], "type": "affiliation"},

    # --- AI-Native Diagnostics ---
    'Tempus': {"aliases": ["Tempus Labs", "Tempus AI"], "type": "affiliation"},
    'Guardant Health': {"aliases": ["Guardant Health"], "type": "affiliation"},
    'iRhythm': {"aliases": ["iRhythm Technologies", "iRhythm"], "type": "affiliation"},
    'Butterfly Network': {"aliases": ["Butterfly Network Inc", "BFLY"], "type": "affiliation"},
    'GeneDx': {"aliases": ["GeneDx", "Sema4"], "type": "affiliation"},
    'NeoGenomics': {"aliases": ["NeoGenomics Laboratories", "NeoGenomics"], "type": "affiliation"},
    'Lunit': {"aliases": ["Lunit Inc"], "type": "affiliation"},

    # --- Large Pharma/Biotech ---
    'Pfizer': {"aliases": ["Pfizer Inc", "Pfizer"], "type": "affiliation"},
    'Novartis': {"aliases": ["Novartis"], "type": "affiliation"},
    'Roche': {"aliases": ["Roche", "Genentech"], "type": "affiliation"},
    'Merck': {"aliases": ["Merck & Co", "Merck Sharp & Dohme", "MSD"], "type": "affiliation"},
    'AstraZeneca': {"aliases": ["AstraZeneca"], "type": "affiliation"},
    'GSK': {"aliases": ["GlaxoSmithKline", "GSK plc"], "type": "affiliation"},
    'Johnson & Johnson': {"aliases": ["Johnson & Johnson", "Janssen Pharmaceutica"], "type": "affiliation"},
    'Sanofi': {"aliases": ["Sanofi"], "type": "affiliation"},
    'Bayer': {"aliases": ["Bayer AG", "Bayer"], "type": "affiliation"},
    'Amgen': {"aliases": ["Amgen"], "type": "affiliation"},
    'Gilead': {"aliases": ["Gilead Sciences", "Kite Pharma"], "type": "affiliation"},

    # --- Tech Enablers ---
    'NVIDIA': {"aliases": ["NVIDIA", "Nvidia Corporation", "Nvidia Clara"], "type": "keyword"},
    'Google': {"aliases": ["Google", "Alphabet", "Verily", "DeepMind", "Google Health"], "type": "keyword"},
    'Microsoft': {"aliases": ["Microsoft", "Microsoft Research"], "type": "keyword"},
    'Amazon': {"aliases": ["Amazon", "AWS", "Amazon Web Services"], "type": "keyword"},
    'IBM': {"aliases": ["IBM", "IBM Research", "IBM Watson Health"], "type": "keyword"},
    'Intel': {"aliases": ["Intel Corp", "Intel"], "type": "keyword"}
}

# TODO: IMPORTANT! Provide your email to NCBI (required by their usage policy)
Entrez.email = "your.email@example.com"

# Keywords for the main AI theme
AI_KEYWORDS = "(\"artificial intelligence\"[MeSH Terms] OR \"artificial intelligence\"[Title/Abstract] OR \"machine learning\"[MeSH Terms] OR \"machine learning\"[Title/Abstract] OR \"deep learning\"[Title/Abstract] OR \"computational model\"[Title/Abstract])"

# Define output paths
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "pubmed_data"
OUTPUT_FILE = OUTPUT_DIR / "pubmed_ai_papers.csv"

# --- Main Functions ---

def search_pubmed(query, max_results=100):
    """Generic function to search PubMed and fetch publication details."""
    try:
        time.sleep(0.5)
        print(f"  Searching PubMed with query: {query[:120]}...")
        handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
        record = Entrez.read(handle)
        handle.close()
        pmid_list = record["IdList"]

        if not pmid_list:
            print("  -> No results found.")
            return []

        print(f"  -> Found {len(pmid_list)} IDs. Fetching details...")
        time.sleep(0.5)
        handle = Entrez.efetch(db="pubmed", id=pmid_list, rettype="medline", retmode="xml")
        records = Entrez.read(handle)
        handle.close()
        return records.get('PubmedArticle', [])

    except Exception as e:
        print(f"  -> An API error occurred: {e}")
        return []

def process_records(records, company_name, search_type):
    """Processes the raw records from PubMed into a clean list of dictionaries."""
    processed_data = []
    for i, record in enumerate(records):
        try:
            medline_citation = record.get('MedlineCitation', {})
            article = medline_citation.get('Article', {})
            journal = article.get('Journal', {})
            journal_title = journal.get('Title', 'No Journal Title')
            title = article.get('ArticleTitle', 'No Title')
            abstract_list = article.get('Abstract', {}).get('AbstractText', [])
            abstract = ' '.join(abstract_list) if abstract_list else 'No Abstract'
            pub_date = journal.get('JournalIssue', {}).get('PubDate', {})
            year = pub_date.get('Year', str(pub_date.get('MedlineDate', 'N/A')).split(' ')[0])
            pmid = medline_citation.get('PMID', f'NO_PMID_{i}')

            processed_data.append({
                'company_scraped': company_name,
                'search_type': search_type,
                'pmid': str(pmid),
                'publish_year': year,
                'journal_title': journal_title,
                'title': title,
                'abstract': abstract
            })
        except Exception:
            continue
    return processed_data

def build_query_from_aliases(aliases, search_field):
    """Builds an OR-separated query string for a list of aliases."""
    formatted_aliases = [f'"{alias}"[{search_field}]' for alias in aliases]
    return f"({(' OR ').join(formatted_aliases)})"

# --- Main Execution ---
if __name__ == "__main__":
    print("--- Starting PubMed Data Acquisition ---", flush=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    all_publications = []

    for company, search_info in COMPANY_SEARCH_TERMS.items():
        aliases = search_info['aliases']
        search_type = search_info['type']
        
        print(f"\n--- Processing Company: {company} ---")

        if search_type == 'affiliation':
            query_part = build_query_from_aliases(aliases, "Affiliation")
        else: # keyword search
            query_part = build_query_from_aliases(aliases, "Title/Abstract")
        
        # Broader query: searches for Company + AI
        full_query = f"{query_part} AND {AI_KEYWORDS}"

        records = search_pubmed(full_query)
        processed = process_records(records, company, search_type)
        all_publications.extend(processed)

    if all_publications:
        df = pd.DataFrame(all_publications)
        initial_count = len(df)
        df.drop_duplicates(subset='pmid', keep='first', inplace=True)
        final_count = len(df)
        print(f"\nRemoved {initial_count - final_count} duplicate records.")

        df.to_csv(OUTPUT_FILE, index=False)
        print(f"\nSuccessfully saved {len(df)} unique records to {OUTPUT_FILE}")
    else:
        print("\nNo publications found or processed to save.")

    print("--- Script Finished ---", flush=True)