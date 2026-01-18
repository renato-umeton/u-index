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
            "qualifying_count": len(qualifying),
            "qualifying_papers": [],
            "unmatched_count": 0,
            "unmatched_papers": [],
        }

        for paper in qualifying:
            doi = paper.get("doi")
            # Normalize DOI to lowercase for matching (OpenAlex returns lowercase)
            doi_key = doi.lower() if doi else None
            if doi_key and doi_key in citations:
                results["qualifying_papers"].append({
                    "title": paper["title"],
                    "year": paper["year"],
                    "position": paper["position"],
                    "citations": citations[doi_key],
                    "doi": doi,
                    "pmid": paper.get("pmid"),
                })
            else:
                results["unmatched_count"] += 1
                results["unmatched_papers"].append({
                    "title": paper["title"],
                    "year": paper["year"],
                    "position": paper["position"],
                    "pmid": paper.get("pmid"),
                    "doi": doi,
                })

        # Sort by citations descending
        results["qualifying_papers"].sort(key=lambda p: p["citations"], reverse=True)

        # Calculate U-index
        results["u_index"] = calculate_u_index(results["qualifying_papers"])

        # Cache results
        if cache:
            cache.set(cache_key, results)

        _print_results(results)

    finally:
        pubmed.close()
        openalex.close()


def _print_results(results: dict) -> None:
    """Print formatted results."""
    # Summary upfront
    click.echo(f"Author: {results['author']}")
    qualifying_total = results.get('qualifying_count', len(results['qualifying_papers']) + results['unmatched_count'])
    click.echo(f"Qualifying papers (first/last author): {qualifying_total}")
    click.echo()

    # Main result
    click.echo(f"U-index: {results['u_index']}")
    click.echo()

    matched_count = len(results['qualifying_papers'])
    click.echo(f"Papers with citation data: {matched_count}")
    click.echo(f"Unmatched (no DOI or not in OpenAlex): {results['unmatched_count']}")
    click.echo()

    # Full list of qualifying papers with links
    if results['qualifying_papers']:
        click.echo("=" * 80)
        click.echo("QUALIFYING PAPERS (sorted by citations)")
        click.echo("=" * 80)
        for i, paper in enumerate(results['qualifying_papers'], 1):
            click.echo()
            click.echo(f"{i}. {paper['title']}")
            click.echo(f"   Year: {paper['year']} | Position: {paper['position']} author | Citations: {paper['citations']}")
            if paper.get('pmid'):
                click.echo(f"   PubMed:   https://pubmed.ncbi.nlm.nih.gov/{paper['pmid']}/")
            if paper.get('doi'):
                click.echo(f"   OpenAlex: https://openalex.org/works/https://doi.org/{paper['doi']}")

    # Unmatched papers
    unmatched = results.get('unmatched_papers', [])
    if unmatched:
        click.echo()
        click.echo("=" * 80)
        click.echo("UNMATCHED PAPERS (no citation data)")
        click.echo("=" * 80)
        for i, paper in enumerate(unmatched, 1):
            click.echo()
            click.echo(f"{i}. {paper['title']}")
            click.echo(f"   Year: {paper['year']} | Position: {paper['position']} author")
            if paper.get('pmid'):
                click.echo(f"   PubMed: https://pubmed.ncbi.nlm.nih.gov/{paper['pmid']}/")
            if paper.get('doi'):
                click.echo(f"   DOI: {paper['doi']} (not found in OpenAlex)")


if __name__ == "__main__":
    main()
