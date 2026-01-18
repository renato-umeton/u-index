"""Core U-index calculation logic."""

from typing import TypedDict


class Paper(TypedDict):
    """A paper with citation count."""

    citations: int


def calculate_u_index(papers: list[Paper]) -> int:
    """Calculate U-index from a list of papers with citation counts.

    U-index is the largest U where U papers have >= U citations each.

    Args:
        papers: List of papers, each with a 'citations' key.

    Returns:
        The U-index value.
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
