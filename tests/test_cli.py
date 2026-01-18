"""Tests for CLI interface."""

import pytest
from click.testing import CliRunner
from pytest_httpx import HTTPXMock
from uindex.cli import main


ESEARCH_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<eSearchResult><IdList><Id>12345678</Id></IdList></eSearchResult>"""

EFETCH_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<PubmedArticleSet>
    <PubmedArticle>
        <MedlineCitation>
            <PMID>12345678</PMID>
            <Article>
                <ArticleTitle>Important Research Paper</ArticleTitle>
                <AuthorList>
                    <Author><LastName>Test</LastName><ForeName>Author</ForeName></Author>
                    <Author><LastName>Other</LastName><ForeName>Person</ForeName></Author>
                </AuthorList>
                <ELocationID EIdType="doi">10.1000/test1</ELocationID>
            </Article>
            <DateCompleted><Year>2023</Year></DateCompleted>
        </MedlineCitation>
    </PubmedArticle>
</PubmedArticleSet>"""

OPENALEX_RESPONSE = {
    "results": [{"doi": "https://doi.org/10.1000/test1", "cited_by_count": 25}]
}


def test_cli_basic(httpx_mock: HTTPXMock, tmp_path):
    """CLI outputs U-index for an author."""
    httpx_mock.add_response(text=ESEARCH_RESPONSE)
    httpx_mock.add_response(text=EFETCH_RESPONSE)
    httpx_mock.add_response(json=OPENALEX_RESPONSE)

    runner = CliRunner()
    result = runner.invoke(main, ["Test Author", "--cache-dir", str(tmp_path)])

    assert result.exit_code == 0
    assert "U-index: 1" in result.output
    assert "Important Research Paper" in result.output


def test_cli_no_cache(httpx_mock: HTTPXMock, tmp_path):
    """CLI with --no-cache skips caching."""
    httpx_mock.add_response(text=ESEARCH_RESPONSE)
    httpx_mock.add_response(text=EFETCH_RESPONSE)
    httpx_mock.add_response(json=OPENALEX_RESPONSE)

    runner = CliRunner()
    result = runner.invoke(main, ["Test Author", "--no-cache", "--cache-dir", str(tmp_path)])

    assert result.exit_code == 0
    assert "U-index:" in result.output


# Fixtures for DOI case sensitivity test
CASE_TEST_ESEARCH = """<?xml version="1.0" encoding="UTF-8"?>
<eSearchResult><IdList>
    <Id>11111111</Id>
    <Id>22222222</Id>
    <Id>33333333</Id>
    <Id>44444444</Id>
    <Id>55555555</Id>
</IdList></eSearchResult>"""

CASE_TEST_EFETCH = """<?xml version="1.0" encoding="UTF-8"?>
<PubmedArticleSet>
    <PubmedArticle>
        <MedlineCitation>
            <PMID>11111111</PMID>
            <Article>
                <ArticleTitle>Paper One - Last Author.</ArticleTitle>
                <AuthorList>
                    <Author><LastName>Other</LastName><ForeName>First</ForeName></Author>
                    <Author><LastName>Sample</LastName><ForeName>Author</ForeName></Author>
                </AuthorList>
                <ELocationID EIdType="doi">10.1016/S2589-7500(24)00114-6</ELocationID>
            </Article>
            <DateCompleted><Year>2024</Year></DateCompleted>
        </MedlineCitation>
    </PubmedArticle>
    <PubmedArticle>
        <MedlineCitation>
            <PMID>22222222</PMID>
            <Article>
                <ArticleTitle>Paper Two - First Author.</ArticleTitle>
                <AuthorList>
                    <Author><LastName>Sample</LastName><ForeName>Author</ForeName></Author>
                    <Author><LastName>Other</LastName><ForeName>Last</ForeName></Author>
                </AuthorList>
                <ELocationID EIdType="doi">10.1038/s41598-022-11444-w</ELocationID>
            </Article>
            <DateCompleted><Year>2022</Year></DateCompleted>
        </MedlineCitation>
    </PubmedArticle>
    <PubmedArticle>
        <MedlineCitation>
            <PMID>33333333</PMID>
            <Article>
                <ArticleTitle>Paper Three - Last Author.</ArticleTitle>
                <AuthorList>
                    <Author><LastName>Other</LastName><ForeName>First</ForeName></Author>
                    <Author><LastName>Sample</LastName><ForeName>Author</ForeName></Author>
                </AuthorList>
                <ELocationID EIdType="doi">10.1016/j.artmed.2020.101822</ELocationID>
            </Article>
            <DateCompleted><Year>2021</Year></DateCompleted>
        </MedlineCitation>
    </PubmedArticle>
    <PubmedArticle>
        <MedlineCitation>
            <PMID>44444444</PMID>
            <Article>
                <ArticleTitle>Paper Four - First Author.</ArticleTitle>
                <AuthorList>
                    <Author><LastName>Sample</LastName><ForeName>Author</ForeName></Author>
                    <Author><LastName>Other</LastName><ForeName>Last</ForeName></Author>
                </AuthorList>
                <ELocationID EIdType="doi">10.1186/1471-2105-13-S4-S6</ELocationID>
            </Article>
            <DateCompleted><Year>2012</Year></DateCompleted>
        </MedlineCitation>
    </PubmedArticle>
    <PubmedArticle>
        <MedlineCitation>
            <PMID>55555555</PMID>
            <Article>
                <ArticleTitle>Paper Five - First Author.</ArticleTitle>
                <AuthorList>
                    <Author><LastName>Sample</LastName><ForeName>Author</ForeName></Author>
                    <Author><LastName>Other</LastName><ForeName>Last</ForeName></Author>
                </AuthorList>
                <ELocationID EIdType="doi">10.1007/978-1-4419-7210-1_26</ELocationID>
            </Article>
            <DateCompleted><Year>2013</Year></DateCompleted>
        </MedlineCitation>
    </PubmedArticle>
</PubmedArticleSet>"""

# OpenAlex returns DOIs in lowercase
CASE_TEST_OPENALEX = {
    "results": [
        {"doi": "https://doi.org/10.1016/j.artmed.2020.101822", "cited_by_count": 794},
        {"doi": "https://doi.org/10.1016/s2589-7500(24)00114-6", "cited_by_count": 28},
        {"doi": "https://doi.org/10.1038/s41598-022-11444-w", "cited_by_count": 10},
        {"doi": "https://doi.org/10.1186/1471-2105-13-s4-s6", "cited_by_count": 6},
        {"doi": "https://doi.org/10.1007/978-1-4419-7210-1_26", "cited_by_count": 5},
    ]
}


def test_doi_case_insensitive_matching(httpx_mock: HTTPXMock, tmp_path):
    """DOIs with different cases should match (PubMed uppercase, OpenAlex lowercase).

    PubMed returns DOIs like '10.1016/S2589-7500(24)00114-6' (uppercase S)
    OpenAlex normalizes to '10.1016/s2589-7500(24)00114-6' (lowercase s)
    Both should match correctly.
    """
    httpx_mock.add_response(text=CASE_TEST_ESEARCH)
    httpx_mock.add_response(text=CASE_TEST_EFETCH)
    httpx_mock.add_response(json=CASE_TEST_OPENALEX)

    runner = CliRunner()
    result = runner.invoke(main, ["Sample Author", "--no-cache", "--cache-dir", str(tmp_path)])

    assert result.exit_code == 0
    # All 5 qualifying papers should be matched (0 unmatched)
    assert "Papers with citation data: 5" in result.output
    assert "Unmatched (no DOI or not in OpenAlex): 0" in result.output
    # U-index should be 5 (all 5 papers have >= their rank in citations)
    assert "U-index: 5" in result.output
    # Verify links are present
    assert "https://pubmed.ncbi.nlm.nih.gov/" in result.output
    assert "https://openalex.org/works/" in result.output
