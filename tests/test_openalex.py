"""Tests for OpenAlex API client."""

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
    """Omits DOIs not found in OpenAlex from result."""
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
