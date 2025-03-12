from dotenv import load_dotenv
import os
import requests


dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path=dotenv_path)


API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("API_URL")

print(f"API_KEY: {API_KEY}")
print(f"BASE_URL: {BASE_URL}")

def search_pubmed(query, retmax=10, debug=False):
    
    endpoint = f"{BASE_URL}/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": retmax,
        "api_key":API_KEY
    }

    if debug:
        print(f"Querying PubMed with: {params}")

    response = requests.get(endpoint, params=params)
    response.raise_for_status()

    data = response.json()
    return data.get("esearchresult", {}).get("idlist", [])

def fetch_pubmed_details(pmids, debug=False):
    
    endpoint = f"{BASE_URL}/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "api_key":API_KEY
    }

    if debug:
        print(f"Fetching details for PMIDs: {pmids}")

    response = requests.get(endpoint, params=params)
    response.raise_for_status()

    return response.text
