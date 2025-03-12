from src.api import search_pubmed,fetch_pubmed_details

def query_pubmed(query, debug=False):
    
    pmids = search_pubmed(query, debug=debug)
    if not pmids:
        return {"error": "No results found."}
    
    details = fetch_pubmed_details(pmids, debug=debug)
    return {"pmids": pmids, "details": details}
