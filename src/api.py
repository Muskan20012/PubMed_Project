from dotenv import load_dotenv
import os
import requests
import xml.etree.ElementTree as ET


dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path=dotenv_path)


API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("API_URL")


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

def parse_pubmed_details(xml_data):
    """
    Parse the XML data from PubMed to extract desired fields.
    """
    root = ET.fromstring(xml_data)
    articles = []

    for article in root.findall(".//PubmedArticle"):
        article_data = {}
        # Extract PubMed ID
        article_data["PubmedID"] = article.findtext(".//PMID")
        # Extract Title
        article_data["Title"] = article.findtext(".//ArticleTitle")
        # Extract Publication Date
        pub_date = article.find(".//PubDate")
        if pub_date is not None:
            year = pub_date.findtext("Year", "")
            month = pub_date.findtext("Month", "")
            day = pub_date.findtext("Day", "")
            article_data["Publication Date"] = f"{year}-{month}-{day}".strip("-")

        # Extract Authors
        authors = article.findall(".//Author")
        non_academic_authors = []
        company_affiliations = []
        for author in authors:
            affiliations = author.findall(".//AffiliationInfo/Affiliation")
            for aff in affiliations:
                if "pharma" in aff.text.lower() or "biotech" in aff.text.lower():
                    company_affiliations.append(aff.text)
                elif not ("university" in aff.text.lower() or "college" in aff.text.lower()):
                    non_academic_authors.append(author.findtext("LastName"))

        article_data["Non-academic Author(s)"] = ", ".join(set(non_academic_authors))
        article_data["Company Affiliation(s)"] = ", ".join(set(company_affiliations))

        # Extract Corresponding Author Email
        emails = [
            aff.text for aff in article.findall(".//AffiliationInfo/Affiliation")
            if "@" in aff.text
        ]
        article_data["Corresponding Author Email"] = ", ".join(emails)

        articles.append(article_data)

    return articles

