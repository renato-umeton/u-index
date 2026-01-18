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
