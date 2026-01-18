# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

U-index is a bibliometric metric that modifies the h-index to count only publications where a researcher is **first or last author**. A researcher has U-index U if U of their first-or-last-authored papers have each been cited at least U times.

Key domain rules:
- Single-author papers count as first (and last) author
- Co-first/co-last authors all qualify
- Corresponding author does NOT qualify

## Development Commands

```bash
pipenv install --dev                           # Install all dependencies
pipenv run pip install -e .                    # Install package in editable mode
pipenv run pytest -v                           # Run all tests
pipenv run pytest tests/test_pubmed.py -v      # Run specific test file
pipenv run pytest tests/test_core.py::test_empty_list -v  # Run single test
pipenv run uindex "Author Name"                # Run CLI
```

## Architecture

**Data flow:** CLI (`cli.py`) orchestrates the pipeline:
1. `PubMedClient.fetch_author_papers()` - searches PubMed, parses XML, determines author position (first/middle/last)
2. Filter to only first/last author papers
3. `OpenAlexClient.get_citations_by_dois()` - batches DOIs (50 at a time), fetches citation counts
4. `calculate_u_index()` - pure function computing U-index on filtered papers
5. Results cached to SQLite with 7-day TTL

**Testing:** All HTTP calls are mocked using `pytest-httpx`. Tests provide XML fixtures for PubMed and JSON for OpenAlex. See `tests/test_pubmed.py` for XML response patterns.

## License

MIT License. See [LICENSE](LICENSE) for details.
