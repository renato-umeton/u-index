"""PubMed E-utilities API client."""

import xml.etree.ElementTree as ET
from typing import Literal
from urllib.parse import quote

import httpx


Position = Literal["first", "last", "middle"] | None


class PubMedClient:
    """Client for fetching author publications from PubMed."""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self, timeout: float = 30.0):
        self.client = httpx.Client(timeout=timeout)

    def fetch_author_papers(self, author_name: str) -> list[dict]:
        """Fetch all papers for an author and determine their position on each."""
        pmids = self._search_author(author_name)
        if not pmids:
            return []

        return self._fetch_papers(pmids, author_name)

    def _search_author(self, author_name: str) -> list[str]:
        """Search PubMed for author's papers, return PMIDs."""
        query = quote(f"{author_name}[Author]")
        url = f"{self.BASE_URL}/esearch.fcgi?db=pubmed&term={query}&retmax=1000&retmode=xml"

        response = self.client.get(url)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        return [id_elem.text for id_elem in root.findall(".//Id") if id_elem.text]

    def _fetch_papers(self, pmids: list[str], author_name: str) -> list[dict]:
        """Fetch paper details for given PMIDs."""
        ids = ",".join(pmids)
        url = f"{self.BASE_URL}/efetch.fcgi?db=pubmed&id={ids}&retmode=xml"

        response = self.client.get(url)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        papers = []

        for article in root.findall(".//PubmedArticle"):
            paper = self._parse_article(article, author_name)
            papers.append(paper)

        return papers

    def _parse_article(self, article: ET.Element, author_name: str) -> dict:
        """Parse a PubMed article XML element."""
        citation = article.find(".//MedlineCitation")
        article_elem = citation.find(".//Article")

        pmid = citation.findtext(".//PMID", "")
        title = article_elem.findtext(".//ArticleTitle", "")

        # Get DOI
        doi = None
        for eloc in article_elem.findall(".//ELocationID"):
            if eloc.get("EIdType") == "doi":
                doi = eloc.text
                break

        # Get year
        year = citation.findtext(".//DateCompleted/Year", "")
        if not year:
            year = citation.findtext(".//PubDate/Year", "")

        # Get author position
        position = self._get_author_position(article_elem, author_name)

        return {
            "pmid": pmid,
            "title": title,
            "doi": doi,
            "year": year,
            "position": position,
        }

    def _get_author_position(self, article_elem: ET.Element, author_name: str) -> Position:
        """Determine author's position in the author list."""
        authors = article_elem.findall(".//Author")
        if not authors:
            return None

        name_parts = author_name.lower().split()

        for i, author in enumerate(authors):
            last_name = (author.findtext("LastName") or "").lower()
            fore_name = (author.findtext("ForeName") or "").lower()

            # Check if this author matches
            matches = all(part in f"{last_name} {fore_name}" for part in name_parts)

            if matches:
                if i == 0:
                    return "first"
                elif i == len(authors) - 1:
                    return "last"
                else:
                    return "middle"

        return None

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()
