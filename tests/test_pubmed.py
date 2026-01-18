"""Tests for PubMed API client."""

import pytest
from pytest_httpx import HTTPXMock
from uindex.pubmed import PubMedClient


ESEARCH_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<eSearchResult>
    <IdList>
        <Id>12345678</Id>
        <Id>87654321</Id>
    </IdList>
</eSearchResult>"""

EFETCH_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<PubmedArticleSet>
    <PubmedArticle>
        <MedlineCitation>
            <PMID>12345678</PMID>
            <Article>
                <ArticleTitle>Test Paper One</ArticleTitle>
                <AuthorList>
                    <Author><LastName>Smith</LastName><ForeName>John</ForeName></Author>
                    <Author><LastName>Jones</LastName><ForeName>Jane</ForeName></Author>
                    <Author><LastName>Doe</LastName><ForeName>Bob</ForeName></Author>
                </AuthorList>
                <ELocationID EIdType="doi">10.1000/test1</ELocationID>
            </Article>
            <DateCompleted><Year>2023</Year></DateCompleted>
        </MedlineCitation>
    </PubmedArticle>
    <PubmedArticle>
        <MedlineCitation>
            <PMID>87654321</PMID>
            <Article>
                <ArticleTitle>Test Paper Two</ArticleTitle>
                <AuthorList>
                    <Author><LastName>Doe</LastName><ForeName>Bob</ForeName></Author>
                    <Author><LastName>Smith</LastName><ForeName>John</ForeName></Author>
                </AuthorList>
                <ELocationID EIdType="doi">10.1000/test2</ELocationID>
            </Article>
            <DateCompleted><Year>2022</Year></DateCompleted>
        </MedlineCitation>
    </PubmedArticle>
</PubmedArticleSet>"""


def test_fetch_author_papers(httpx_mock: HTTPXMock):
    """Fetches papers and identifies author position."""
    httpx_mock.add_response(
        url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=Smith%20John%5Bfull%5D&retmax=1000&retmode=xml",
        text=ESEARCH_RESPONSE,
    )
    httpx_mock.add_response(
        url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=12345678,87654321&retmode=xml",
        text=EFETCH_RESPONSE,
    )

    client = PubMedClient()
    papers = client.fetch_author_papers("Smith John")

    assert len(papers) == 2

    # First paper: Smith is first author
    assert papers[0]["pmid"] == "12345678"
    assert papers[0]["title"] == "Test Paper One"
    assert papers[0]["doi"] == "10.1000/test1"
    assert papers[0]["position"] == "first"
    assert papers[0]["year"] == "2023"

    # Second paper: Smith is last author
    assert papers[1]["pmid"] == "87654321"
    assert papers[1]["position"] == "last"


def test_fetch_author_papers_middle_author(httpx_mock: HTTPXMock):
    """Middle author position is identified."""
    httpx_mock.add_response(text=ESEARCH_RESPONSE)
    httpx_mock.add_response(text=EFETCH_RESPONSE)

    client = PubMedClient()
    papers = client.fetch_author_papers("Jones Jane")

    # Jones is middle author on paper 1, not on paper 2
    assert len(papers) == 2
    assert papers[0]["position"] == "middle"
    assert papers[1]["position"] is None  # Not an author


def test_single_author_paper(httpx_mock: HTTPXMock):
    """Single author is both first and last."""
    single_author_response = """<?xml version="1.0" encoding="UTF-8"?>
<PubmedArticleSet>
    <PubmedArticle>
        <MedlineCitation>
            <PMID>11111111</PMID>
            <Article>
                <ArticleTitle>Solo Paper</ArticleTitle>
                <AuthorList>
                    <Author><LastName>Solo</LastName><ForeName>Han</ForeName></Author>
                </AuthorList>
            </Article>
        </MedlineCitation>
    </PubmedArticle>
</PubmedArticleSet>"""

    httpx_mock.add_response(text='<eSearchResult><IdList><Id>11111111</Id></IdList></eSearchResult>')
    httpx_mock.add_response(text=single_author_response)

    client = PubMedClient()
    papers = client.fetch_author_papers("Solo Han")

    assert papers[0]["position"] == "first"  # Single author counts as first
