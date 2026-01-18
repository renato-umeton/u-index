"""Tests for core U-index calculation logic."""

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
