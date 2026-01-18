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
