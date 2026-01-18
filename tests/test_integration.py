"""Integration tests for the full U-index calculation flow."""

import pytest
from pytest_httpx import HTTPXMock
from uindex.cli import main
from click.testing import CliRunner


# Multi-paper scenario with mixed positions
ESEARCH_MULTI = """<?xml version="1.0" encoding="UTF-8"?>
<eSearchResult><IdList>
    <Id>1</Id><Id>2</Id><Id>3</Id><Id>4</Id><Id>5</Id>
</IdList></eSearchResult>"""

EFETCH_MULTI = """<?xml version="1.0" encoding="UTF-8"?>
<PubmedArticleSet>
    <PubmedArticle>
        <MedlineCitation><PMID>1</PMID>
            <Article>
                <ArticleTitle>Paper 1 - First Author</ArticleTitle>
                <AuthorList>
                    <Author><LastName>Target</LastName><ForeName>Author</ForeName></Author>
                    <Author><LastName>Other</LastName><ForeName>One</ForeName></Author>
                </AuthorList>
                <ELocationID EIdType="doi">10.1000/p1</ELocationID>
            </Article>
            <DateCompleted><Year>2023</Year></DateCompleted>
        </MedlineCitation>
    </PubmedArticle>
    <PubmedArticle>
        <MedlineCitation><PMID>2</PMID>
            <Article>
                <ArticleTitle>Paper 2 - Last Author</ArticleTitle>
                <AuthorList>
                    <Author><LastName>Student</LastName><ForeName>One</ForeName></Author>
                    <Author><LastName>Target</LastName><ForeName>Author</ForeName></Author>
                </AuthorList>
                <ELocationID EIdType="doi">10.1000/p2</ELocationID>
            </Article>
            <DateCompleted><Year>2022</Year></DateCompleted>
        </MedlineCitation>
    </PubmedArticle>
    <PubmedArticle>
        <MedlineCitation><PMID>3</PMID>
            <Article>
                <ArticleTitle>Paper 3 - Middle Author (excluded)</ArticleTitle>
                <AuthorList>
                    <Author><LastName>First</LastName><ForeName>One</ForeName></Author>
                    <Author><LastName>Target</LastName><ForeName>Author</ForeName></Author>
                    <Author><LastName>Last</LastName><ForeName>One</ForeName></Author>
                </AuthorList>
                <ELocationID EIdType="doi">10.1000/p3</ELocationID>
            </Article>
            <DateCompleted><Year>2021</Year></DateCompleted>
        </MedlineCitation>
    </PubmedArticle>
    <PubmedArticle>
        <MedlineCitation><PMID>4</PMID>
            <Article>
                <ArticleTitle>Paper 4 - First Author Low Cites</ArticleTitle>
                <AuthorList>
                    <Author><LastName>Target</LastName><ForeName>Author</ForeName></Author>
                    <Author><LastName>Other</LastName><ForeName>Two</ForeName></Author>
                </AuthorList>
                <ELocationID EIdType="doi">10.1000/p4</ELocationID>
            </Article>
            <DateCompleted><Year>2020</Year></DateCompleted>
        </MedlineCitation>
    </PubmedArticle>
    <PubmedArticle>
        <MedlineCitation><PMID>5</PMID>
            <Article>
                <ArticleTitle>Paper 5 - No DOI (unmatched)</ArticleTitle>
                <AuthorList>
                    <Author><LastName>Target</LastName><ForeName>Author</ForeName></Author>
                </AuthorList>
            </Article>
            <DateCompleted><Year>2019</Year></DateCompleted>
        </MedlineCitation>
    </PubmedArticle>
</PubmedArticleSet>"""

OPENALEX_MULTI = {
    "results": [
        {"doi": "https://doi.org/10.1000/p1", "cited_by_count": 50},
        {"doi": "https://doi.org/10.1000/p2", "cited_by_count": 30},
        {"doi": "https://doi.org/10.1000/p3", "cited_by_count": 100},  # Middle author, excluded
        {"doi": "https://doi.org/10.1000/p4", "cited_by_count": 2},
    ]
}


def test_full_uindex_calculation(httpx_mock: HTTPXMock, tmp_path):
    """
    Full integration test:
    - 5 papers total
    - 3 first/last authored (papers 1, 2, 4, 5)
    - 1 middle authored (paper 3, excluded)
    - 1 without DOI (paper 5, unmatched)
    - Citations: p1=50, p2=30, p4=2
    - U-index should be 2 (papers 1 and 2 have >= 2 citations)
    """
    httpx_mock.add_response(text=ESEARCH_MULTI)
    httpx_mock.add_response(text=EFETCH_MULTI)
    httpx_mock.add_response(json=OPENALEX_MULTI)

    runner = CliRunner()
    result = runner.invoke(main, ["Target Author", "--cache-dir", str(tmp_path)])

    assert result.exit_code == 0

    # U-index = 2 (two papers with >= 2 citations: 50 and 30)
    assert "U-index: 2" in result.output

    # Should show 4 qualifying papers (first/last), 1 unmatched
    assert "Qualifying papers (first/last author): 4" in result.output
    assert "Papers with citation data: 3" in result.output
    assert "Unmatched (no DOI or not in OpenAlex): 1" in result.output

    # Middle author paper should NOT appear in output
    assert "Paper 3 - Middle Author" not in result.output

    # First/last author papers should appear
    assert "Paper 1 - First Author" in result.output
    assert "Paper 2 - Last Author" in result.output

    # Unmatched paper should appear in unmatched section
    assert "UNMATCHED PAPERS" in result.output
    assert "Paper 5 - No DOI (unmatched)" in result.output

    # Links should be present
    assert "https://pubmed.ncbi.nlm.nih.gov/" in result.output
    assert "https://openalex.org/works/" in result.output
