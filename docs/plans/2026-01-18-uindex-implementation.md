# U-Index CLI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a CLI tool that calculates the U-index for a researcher using their PubMed author ID.

**Architecture:** CLI wraps a core engine that fetches publications from PubMed, filters to first/last-authored papers, retrieves citation counts from OpenAlex via DOI matching, and calculates the U-index. A SQLite cache layer with 7-day expiry reduces API calls.

**Tech Stack:** Python 3.14, httpx (HTTP client), click (CLI), sqlite3 (cache)

---

## Task 1: Project Setup

**Files:**
- Modify: `Pipfile`
- Create: `pyproject.toml`
- Create: `src/uindex/__init__.py`

**Step 1: Update Pipfile with dependencies**

Replace `Pipfile` contents:

```toml
[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[packages]
httpx = "*"
click = "*"

[dev-packages]
pytest = "*"
pytest-httpx = "*"

[requires]
python_version = "3.14"
```

**Step 2: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "uindex"
version = "0.1.0"
description = "Calculate the Umeton Index (U-index) for researchers"
requires-python = ">=3.14"
dependencies = [
    "httpx",
    "click",
]

[project.scripts]
uindex = "uindex.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

**Step 3: Create package init**

Create `src/uindex/__init__.py`:

```python
"""U-index: Calculate the Umeton Index for researchers."""

__version__ = "0.1.0"
```

**Step 4: Create directory structure and install**

Run:
```bash
mkdir -p src/uindex tests
pipenv install --dev
pipenv run pip install -e .
```

**Step 5: Verify installation**

Run: `pipenv run python -c "import uindex; print(uindex.__version__)"`
Expected: `0.1.0`

**Step 6: Commit**

```bash
git add Pipfile Pipfile.lock pyproject.toml src/
git commit -m "Set up project structure with dependencies"
```

---

## Task 2: Core U-Index Calculation

**Files:**
- Create: `tests/test_core.py`
- Create: `src/uindex/core.py`

**Step 1: Write failing test for U-index calculation**

Create `tests/test_core.py`:

```python
from uindex.core import calculate_u_index


def test_calculate_u_index_basic():
    """U=3 when 3 papers have >= 3 citations each."""
    papers = [
        {"citations": 10},
        {"citations": 5},
        {"citations": 3},
        {"citations": 1},
    ]
    assert calculate_u_index(papers) == 3


def test_calculate_u_index_empty():
    """U=0 when no papers."""
    assert calculate_u_index([]) == 0


def test_calculate_u_index_no_citations():
    """U=0 when all papers have 0 citations."""
    papers = [{"citations": 0}, {"citations": 0}]
    assert calculate_u_index(papers) == 0


def test_calculate_u_index_all_high():
    """U equals paper count when all have enough citations."""
    papers = [
        {"citations": 100},
        {"citations": 50},
        {"citations": 30},
    ]
    assert calculate_u_index(papers) == 3
```

**Step 2: Run test to verify it fails**

Run: `pipenv run pytest tests/test_core.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'uindex.core'`

**Step 3: Write minimal implementation**

Create `src/uindex/core.py`:

```python
"""Core U-index calculation logic."""

from typing import TypedDict


class Paper(TypedDict):
    citations: int


def calculate_u_index(papers: list[Paper]) -> int:
    """Calculate U-index from a list of papers with citation counts.

    U-index is the largest U where U papers have >= U citations each.
    """
    if not papers:
        return 0

    sorted_papers = sorted(papers, key=lambda p: p["citations"], reverse=True)

    u_index = 0
    for i, paper in enumerate(sorted_papers, start=1):
        if paper["citations"] >= i:
            u_index = i
        else:
            break

    return u_index
```

**Step 4: Run test to verify it passes**

Run: `pipenv run pytest tests/test_core.py -v`
Expected: 4 passed

**Step 5: Commit**

```bash
git add tests/test_core.py src/uindex/core.py
git commit -m "Add core U-index calculation"
```

---

## Task 3: Cache Layer

**Files:**
- Create: `tests/test_cache.py`
- Create: `src/uindex/cache.py`

**Step 1: Write failing test for cache**

Create `tests/test_cache.py`:

```python
import time
from pathlib import Path
from uindex.cache import Cache


def test_cache_set_and_get(tmp_path):
    """Cache stores and retrieves values."""
    cache = Cache(tmp_path / "test.db")
    cache.set("key1", {"data": "value"})
    assert cache.get("key1") == {"data": "value"}


def test_cache_miss(tmp_path):
    """Cache returns None for missing keys."""
    cache = Cache(tmp_path / "test.db")
    assert cache.get("nonexistent") is None


def test_cache_expiry(tmp_path):
    """Cache returns None for expired entries."""
    cache = Cache(tmp_path / "test.db", ttl_seconds=1)
    cache.set("key1", {"data": "value"})
    time.sleep(1.1)
    assert cache.get("key1") is None


def test_cache_overwrite(tmp_path):
    """Cache overwrites existing values."""
    cache = Cache(tmp_path / "test.db")
    cache.set("key1", {"old": "data"})
    cache.set("key1", {"new": "data"})
    assert cache.get("key1") == {"new": "data"}
```

**Step 2: Run test to verify it fails**

Run: `pipenv run pytest tests/test_cache.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'uindex.cache'`

**Step 3: Write minimal implementation**

Create `src/uindex/cache.py`:

```python
"""SQLite-based cache with TTL support."""

import json
import sqlite3
import time
from pathlib import Path
from typing import Any


class Cache:
    """Simple key-value cache backed by SQLite."""

    DEFAULT_TTL = 7 * 24 * 60 * 60  # 7 days in seconds

    def __init__(self, db_path: Path, ttl_seconds: int | None = None):
        self.db_path = db_path
        self.ttl_seconds = ttl_seconds if ttl_seconds is not None else self.DEFAULT_TTL
        self._init_db()

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
            """)

    def get(self, key: str) -> Any | None:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT value, created_at FROM cache WHERE key = ?",
                (key,)
            ).fetchone()

        if row is None:
            return None

        value, created_at = row
        if time.time() - created_at > self.ttl_seconds:
            self.delete(key)
            return None

        return json.loads(value)

    def set(self, key: str, value: Any) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cache (key, value, created_at)
                VALUES (?, ?, ?)
                """,
                (key, json.dumps(value), time.time())
            )

    def delete(self, key: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache WHERE key = ?", (key,))
```

**Step 4: Run test to verify it passes**

Run: `pipenv run pytest tests/test_cache.py -v`
Expected: 4 passed

**Step 5: Commit**

```bash
git add tests/test_cache.py src/uindex/cache.py
git commit -m "Add SQLite cache layer with TTL"
```

---

## Task 4: PubMed API Client

**Files:**
- Create: `tests/test_pubmed.py`
- Create: `src/uindex/pubmed.py`

**Step 1: Write failing test for PubMed client**

Create `tests/test_pubmed.py`:

```python
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
        url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=Smith%20John%5BAuthor%5D&retmax=1000&retmode=xml",
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
```

**Step 2: Run test to verify it fails**

Run: `pipenv run pytest tests/test_pubmed.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'uindex.pubmed'`

**Step 3: Write minimal implementation**

Create `src/uindex/pubmed.py`:

```python
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
```

**Step 4: Run test to verify it passes**

Run: `pipenv run pytest tests/test_pubmed.py -v`
Expected: 3 passed

**Step 5: Commit**

```bash
git add tests/test_pubmed.py src/uindex/pubmed.py
git commit -m "Add PubMed API client"
```

---

## Task 5: OpenAlex API Client

**Files:**
- Create: `tests/test_openalex.py`
- Create: `src/uindex/openalex.py`

**Step 1: Write failing test for OpenAlex client**

Create `tests/test_openalex.py`:

```python
import pytest
from pytest_httpx import HTTPXMock
from uindex.openalex import OpenAlexClient


OPENALEX_RESPONSE = {
    "results": [
        {
            "doi": "https://doi.org/10.1000/test1",
            "cited_by_count": 42,
        },
        {
            "doi": "https://doi.org/10.1000/test2",
            "cited_by_count": 17,
        },
    ]
}


def test_get_citations_by_doi(httpx_mock: HTTPXMock):
    """Fetches citation counts for DOIs."""
    httpx_mock.add_response(json=OPENALEX_RESPONSE)

    client = OpenAlexClient()
    citations = client.get_citations_by_dois(["10.1000/test1", "10.1000/test2"])

    assert citations == {
        "10.1000/test1": 42,
        "10.1000/test2": 17,
    }


def test_get_citations_missing_doi(httpx_mock: HTTPXMock):
    """Returns 0 for DOIs not found in OpenAlex."""
    httpx_mock.add_response(json={"results": []})

    client = OpenAlexClient()
    citations = client.get_citations_by_dois(["10.1000/missing"])

    assert citations == {}


def test_get_citations_batching(httpx_mock: HTTPXMock):
    """Batches requests for more than 50 DOIs."""
    # First batch
    httpx_mock.add_response(json={
        "results": [{"doi": f"https://doi.org/10.1000/test{i}", "cited_by_count": i} for i in range(50)]
    })
    # Second batch
    httpx_mock.add_response(json={
        "results": [{"doi": "https://doi.org/10.1000/test50", "cited_by_count": 50}]
    })

    client = OpenAlexClient()
    dois = [f"10.1000/test{i}" for i in range(51)]
    citations = client.get_citations_by_dois(dois)

    assert len(citations) == 51
    assert citations["10.1000/test50"] == 50
```

**Step 2: Run test to verify it fails**

Run: `pipenv run pytest tests/test_openalex.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'uindex.openalex'`

**Step 3: Write minimal implementation**

Create `src/uindex/openalex.py`:

```python
"""OpenAlex API client for citation data."""

import httpx


class OpenAlexClient:
    """Client for fetching citation counts from OpenAlex."""

    BASE_URL = "https://api.openalex.org"
    BATCH_SIZE = 50

    def __init__(self, timeout: float = 30.0):
        self.client = httpx.Client(timeout=timeout)

    def get_citations_by_dois(self, dois: list[str]) -> dict[str, int]:
        """Get citation counts for a list of DOIs.

        Returns a dict mapping DOI -> citation count.
        DOIs not found in OpenAlex are omitted from the result.
        """
        if not dois:
            return {}

        results = {}

        # Process in batches of 50
        for i in range(0, len(dois), self.BATCH_SIZE):
            batch = dois[i:i + self.BATCH_SIZE]
            batch_results = self._fetch_batch(batch)
            results.update(batch_results)

        return results

    def _fetch_batch(self, dois: list[str]) -> dict[str, int]:
        """Fetch citation counts for a batch of DOIs."""
        # OpenAlex filter format: doi:10.1000/x|10.1000/y
        doi_filter = "|".join(dois)
        url = f"{self.BASE_URL}/works?filter=doi:{doi_filter}&select=doi,cited_by_count"

        response = self.client.get(url)
        response.raise_for_status()

        data = response.json()
        results = {}

        for work in data.get("results", []):
            doi = work.get("doi", "")
            if doi:
                # OpenAlex returns full URL, normalize to just the DOI
                normalized_doi = doi.replace("https://doi.org/", "")
                results[normalized_doi] = work.get("cited_by_count", 0)

        return results

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()
```

**Step 4: Run test to verify it passes**

Run: `pipenv run pytest tests/test_openalex.py -v`
Expected: 3 passed

**Step 5: Commit**

```bash
git add tests/test_openalex.py src/uindex/openalex.py
git commit -m "Add OpenAlex API client"
```

---

## Task 6: CLI Interface

**Files:**
- Create: `tests/test_cli.py`
- Create: `src/uindex/cli.py`

**Step 1: Write failing test for CLI**

Create `tests/test_cli.py`:

```python
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
```

**Step 2: Run test to verify it fails**

Run: `pipenv run pytest tests/test_cli.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'uindex.cli'`

**Step 3: Write minimal implementation**

Create `src/uindex/cli.py`:

```python
"""Command-line interface for U-index calculation."""

from pathlib import Path

import click

from uindex.cache import Cache
from uindex.core import calculate_u_index
from uindex.openalex import OpenAlexClient
from uindex.pubmed import PubMedClient


DEFAULT_CACHE_DIR = Path.home() / ".cache" / "uindex"


@click.command()
@click.argument("author_name")
@click.option("--no-cache", is_flag=True, help="Skip cache, fetch fresh data")
@click.option("--refresh", is_flag=True, help="Force refresh cached data")
@click.option("--cache-dir", type=click.Path(path_type=Path), default=DEFAULT_CACHE_DIR,
              help="Cache directory path")
def main(author_name: str, no_cache: bool, refresh: bool, cache_dir: Path) -> None:
    """Calculate U-index for AUTHOR_NAME using PubMed data."""
    cache = None if no_cache else Cache(cache_dir / "cache.db")
    cache_key = f"author:{author_name}"

    # Check cache
    if cache and not refresh:
        cached = cache.get(cache_key)
        if cached:
            _print_results(cached)
            return

    # Fetch data
    pubmed = PubMedClient()
    openalex = OpenAlexClient()

    try:
        papers = pubmed.fetch_author_papers(author_name)

        # Filter to first/last authored
        qualifying = [p for p in papers if p["position"] in ("first", "last")]

        # Get DOIs for citation lookup
        dois = [p["doi"] for p in qualifying if p["doi"]]
        citations = openalex.get_citations_by_dois(dois)

        # Build results
        results = {
            "author": author_name,
            "total_papers": len(papers),
            "qualifying_papers": [],
            "unmatched_count": 0,
        }

        for paper in qualifying:
            doi = paper.get("doi")
            if doi and doi in citations:
                results["qualifying_papers"].append({
                    "title": paper["title"],
                    "year": paper["year"],
                    "position": paper["position"],
                    "citations": citations[doi],
                    "doi": doi,
                })
            else:
                results["unmatched_count"] += 1

        # Sort by citations descending
        results["qualifying_papers"].sort(key=lambda p: p["citations"], reverse=True)

        # Calculate indices
        results["u_index"] = calculate_u_index(results["qualifying_papers"])
        results["h_index"] = _estimate_h_index(papers, citations)

        # Cache results
        if cache:
            cache.set(cache_key, results)

        _print_results(results)

    finally:
        pubmed.close()
        openalex.close()


def _estimate_h_index(papers: list[dict], citations: dict[str, int]) -> int:
    """Estimate h-index from all papers."""
    all_papers = []
    for paper in papers:
        doi = paper.get("doi")
        if doi and doi in citations:
            all_papers.append({"citations": citations[doi]})
    return calculate_u_index(all_papers)


def _print_results(results: dict) -> None:
    """Print formatted results."""
    click.echo(f"Author: {results['author']}")
    click.echo(f"U-index: {results['u_index']}")
    click.echo(f"h-index (estimated): {results['h_index']}")
    click.echo()

    qualifying_count = len(results['qualifying_papers'])
    click.echo(f"Qualifying papers (first/last author): {qualifying_count + results['unmatched_count']}")
    click.echo(f"├─ With citations: {qualifying_count}")
    click.echo(f"└─ Unmatched (no DOI or not in OpenAlex): {results['unmatched_count']}")
    click.echo()

    if results['qualifying_papers']:
        click.echo("Top qualifying papers:")
        for i, paper in enumerate(results['qualifying_papers'][:10], 1):
            click.echo(f"  {i}. {paper['title']} ({paper['year']}) - {paper['citations']} citations [{paper['position']} author]")


if __name__ == "__main__":
    main()
```

**Step 4: Run test to verify it passes**

Run: `pipenv run pytest tests/test_cli.py -v`
Expected: 2 passed

**Step 5: Commit**

```bash
git add tests/test_cli.py src/uindex/cli.py
git commit -m "Add CLI interface"
```

---

## Task 7: Integration Test and Final Verification

**Files:**
- Create: `tests/test_integration.py`

**Step 1: Write integration test**

Create `tests/test_integration.py`:

```python
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
    assert "With citations: 3" in result.output
    assert "Unmatched (no DOI or not in OpenAlex): 1" in result.output

    # Middle author paper should NOT appear in output
    assert "Paper 3 - Middle Author" not in result.output

    # First/last author papers should appear
    assert "Paper 1 - First Author" in result.output
    assert "Paper 2 - Last Author" in result.output
```

**Step 2: Run integration test**

Run: `pipenv run pytest tests/test_integration.py -v`
Expected: 1 passed

**Step 3: Run all tests**

Run: `pipenv run pytest -v`
Expected: All tests pass

**Step 4: Commit**

```bash
git add tests/test_integration.py
git commit -m "Add integration test"
```

---

## Task 8: Final Cleanup and Documentation

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Update CLAUDE.md with development commands**

Add to `CLAUDE.md`:

```markdown

## Development Commands

```bash
pipenv install --dev     # Install all dependencies
pipenv shell             # Activate virtual environment
pipenv run pytest -v     # Run all tests
pipenv run pytest tests/test_core.py -v  # Run specific test file
pipenv run uindex "Author Name"  # Run CLI
```

## Architecture

```
src/uindex/
├── cli.py      - Click CLI entry point
├── core.py     - U-index calculation (pure function)
├── pubmed.py   - PubMed E-utilities client
├── openalex.py - OpenAlex API client
└── cache.py    - SQLite cache with TTL
```

Data flow: CLI → PubMed (papers + positions) → filter first/last → OpenAlex (citations) → calculate U-index
```

**Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "Update documentation with dev commands and architecture"
```

**Step 3: Verify CLI works end-to-end**

Run: `pipenv run uindex --help`
Expected: Help output showing usage

---

## Summary

After completing all tasks:
- 8 commits on `feature/pubmed-implementation` branch
- Full test coverage with unit and integration tests
- Working CLI: `uindex "Author Name"`
