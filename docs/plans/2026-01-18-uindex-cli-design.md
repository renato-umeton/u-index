# U-Index CLI Design

## Overview

CLI tool to calculate the Umeton Index (U-index) for a researcher using their PubMed author ID. The U-index counts only first-or-last-authored papers: a researcher has U-index U if U of their first-or-last-authored papers have each been cited at least U times.

## Data Sources

- **PubMed (E-utilities)**: Author publications and author positions
- **OpenAlex**: Citation counts (matched via DOI)

## Architecture

```
CLI (uindex <pubmed_author_id>)
        │
        ▼
    Core Engine
    1. Fetch papers from PubMed
    2. Filter to first/last authored
    3. Get citations from OpenAlex
    4. Calculate U-index
        │
        ▼
    Cache Layer (SQLite, 7-day expiry)
        │
    ┌───┴───┐
    ▼       ▼
PubMed   OpenAlex
```

## Data Flow

### Step 1: Fetch from PubMed
- `esearch` to get PMIDs for author ID
- `efetch` to get full records with author lists and DOIs
- Extract author position (strict first = position 1, strict last = final position)

### Step 2: Filter qualifying papers
- Keep only papers where author is first OR last
- No special handling for equal contribution markers

### Step 3: Get citations from OpenAlex
- Batch query by DOI (up to 50 per request)
- Papers without DOI or not in OpenAlex: reported but excluded from calculation

### Step 4: Calculate U-index
- Sort qualifying papers by citation count descending
- Find largest U where paper #U has >= U citations

## Output Format

```
Author: [name]
U-index: 12
h-index (estimated): 18

Qualifying papers (first/last author): 28
├─ With citations: 25
└─ Unmatched (no DOI or not in OpenAlex): 3

Top qualifying papers:
  1. [Title] (2023) - 156 citations [first author]
  2. [Title] (2021) - 89 citations [last author]
  ...
```

## Project Structure

```
u-index/
├── src/
│   └── uindex/
│       ├── __init__.py
│       ├── cli.py          # CLI entry point
│       ├── core.py         # U-index calculation logic
│       ├── pubmed.py       # PubMed API client
│       ├── openalex.py     # OpenAlex API client
│       └── cache.py        # SQLite cache layer
├── tests/
│   ├── test_core.py
│   ├── test_pubmed.py
│   ├── test_openalex.py
│   └── test_cache.py
├── Pipfile
└── pyproject.toml
```

## Dependencies

- `httpx` - HTTP client
- `click` - CLI framework
- `sqlite3` - Cache (stdlib)

## CLI Interface

```bash
uindex 12345678              # basic usage
uindex 12345678 --no-cache   # skip cache
uindex 12345678 --refresh    # force refresh
```

## Cache

- Location: `~/.cache/uindex/cache.db`
- Default expiry: 7 days
- SQLite-based
