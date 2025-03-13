import os
import httpx
import xml.etree.ElementTree as ET
import re
from typing import List, Dict, Any
from dotenv import load_dotenv

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
dotenv_path = os.path.join(root_dir, ".env")
load_dotenv(dotenv_path=dotenv_path)

API_KEY: str = os.getenv("API_KEY", "")
BASE_URL: str = os.getenv("API_URL", "")


async def search_pubmed(query: str, retmax: int = 100, retstart: int = 0, debug: bool = False) -> List[str]:

    endpoint: str = f"{BASE_URL}/esearch.fcgi"
    params: Dict[str, Any] = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": retmax,
        "retstart": retstart,
        "api_key": API_KEY,
    }

    if debug:
        params_without_api_key: Dict[str, Any] = {k: v for k, v in params.items() if k != "api_key"}
        print(f"Querying PubMed with: {params_without_api_key}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, params=params)
            response.raise_for_status()  # Raise exception for HTTP errors

        data: Dict[str, Any] = response.json()
        if debug:
            print(f"Response received: {data}")

        return data.get("esearchresult", {}).get("idlist", [])

    except httpx.HTTPStatusError as http_err:
        raise RuntimeError(f"HTTP error occurred: {http_err.response.status_code} - {http_err.response.text}")
    except httpx.RequestError as req_err:
        raise RuntimeError(f"Request error occurred: {req_err}")
    except ValueError as json_err:
        raise RuntimeError(f"Error decoding JSON response: {json_err}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")


async def fetch_pubmed_details(pmids: List[str], debug: bool = False) -> str:

    endpoint: str = f"{BASE_URL}/efetch.fcgi"
    params: Dict[str, Any] = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "api_key": API_KEY,
    }

    if debug:
        print(f"Fetching details for PMIDs: {pmids}")

    async with httpx.AsyncClient() as client:
        response = await client.get(endpoint, params=params)
        response.raise_for_status()

    return response.text


def parse_pubmed_details(xml_data: str) -> List[Dict[str, str]]:
    root: ET.Element = ET.fromstring(xml_data)
    articles: List[Dict[str, str]] = []

    for article in root.findall(".//PubmedArticle"):
        pubmed_id: str = article.findtext(".//PMID", "").strip()
        # Extract Title
        title: str = article.findtext(".//ArticleTitle", "").strip()

        # Skip articles without titles
        if not title:
            continue

        article_data: Dict[str, str] = {
            "PubmedID": pubmed_id,
            "Title": title,
        }

        # Extract publication date
        pub_date: ET.Element = article.find(".//PubDate") or ET.Element("PubDate")
        year: str = pub_date.findtext("Year", "")
        month: str = pub_date.findtext("Month", "")
        day: str = pub_date.findtext("Day", "")
        article_data["Publication Date"] = f"{year}-{month}-{day}".strip("-")

        # Extract authors and affiliations
        authors: List[ET.Element] = article.findall(".//Author")
        all_authors: List[str] = []
        company_affiliations: List[str] = []
        pharma_or_biotech_found: bool = False

        for author in authors:
            last_name: str = author.findtext("LastName", "")
            first_name: str = author.findtext("ForeName", "")
            full_name: str = f"{first_name} {last_name}".strip() if first_name and last_name else last_name
            if full_name:
                all_authors.append(full_name)

            affiliations: List[ET.Element] = author.findall(".//AffiliationInfo/Affiliation")
            for aff in affiliations:
                if aff.text:
                    aff_text_lower: str = aff.text.lower()
                    if (
                        "pharma" in aff_text_lower or "biotech" in aff_text_lower
                    ) and (
                        "company" in aff_text_lower or "corporation" in aff_text_lower or "ltd" in aff_text_lower
                    ) and not (
                        "university" in aff_text_lower or "institute" in aff_text_lower
                    ):
                        company_affiliations.append(aff.text)
                        pharma_or_biotech_found = True

        if pharma_or_biotech_found:
            article_data["Authors"] = ", ".join(set(all_authors))
            article_data["Company"] = ", ".join(set(company_affiliations))

            emails: List[str] = []
            for aff in article.findall(".//AffiliationInfo/Affiliation"):
                if aff.text:
                    extracted_emails: List[str] = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", aff.text)
                    emails.extend(extracted_emails)
            if emails:

                article_data["Corresponding Author Email"] = ", ".join(set(emails))
            else:
                article_data["Corresponding Author Email"]="No email"
            articles.append(article_data)

    return articles


async def fetch_filtered_articles(query: str, desired_count: int = 100, debug: bool = False) -> List[Dict[str, str]]:
    
    all_articles: List[Dict[str, str]] = []
    retstart: int = 0
    batch_size: int = 100

    while len(all_articles) < desired_count:
        pmids: List[str] = await search_pubmed(query, retmax=batch_size, retstart=retstart, debug=debug)
        if not pmids:
            break

        # Fetch details concurrently
        xml_data: str = await fetch_pubmed_details(pmids, debug=debug)
        articles: List[Dict[str, str]] = parse_pubmed_details(xml_data)
        all_articles.extend(articles)

        if debug:
            print(f"Total articles found: {len(all_articles)}")

        retstart += batch_size

    return all_articles[:desired_count]
