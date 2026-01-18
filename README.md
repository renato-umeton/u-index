# U-Index

A CLI tool to calculate the Umeton Index (U-index) for researchers using PubMed and OpenAlex data.

## What is the U-index?

The U-index is a bibliometric metric that modifies the h-index to count only publications where a researcher is **first or last author**. This isolates research leadership contributions from collaborative middle-author positions.

**Definition:** A researcher has U-index U if U of their first-or-last-authored papers have each been cited at least U times.

For the full methodology, see the [preprint](docs/manuscript/umeton_index_preprint.md).

## Installation

Requires Python 3.14+.

```bash
git clone https://github.com/your-username/u-index.git
cd u-index
pipenv install
pipenv run pip install -e .
```

## Usage

```bash
# Calculate U-index for an author
pipenv run uindex "Umeton Renato"

# Skip cache (fetch fresh data)
pipenv run uindex "Umeton Renato" --no-cache

# Force refresh cached data
pipenv run uindex "Umeton Renato" --refresh
```

### Example Output

```
Author: Umeton Renato
Qualifying papers (first/last author): 5

U-index: 5

Papers with citation data: 5
Unmatched (no DOI or not in OpenAlex): 0

================================================================================
QUALIFYING PAPERS (sorted by citations)
================================================================================

1. Automated machine learning: Review of the state-of-the-art...
   Year: 2021 | Position: last author | Citations: 794
   PubMed:   https://pubmed.ncbi.nlm.nih.gov/32499001/
   OpenAlex: https://openalex.org/works/https://doi.org/10.1016/j.artmed.2020.101822
...
```

## Data Sources

- **PubMed** (via E-utilities): Author publications and author positions
- **OpenAlex**: Citation counts (matched via DOI)

## Development

```bash
pipenv install --dev     # Install all dependencies
pipenv run pytest -v     # Run tests
```

## License

MIT License. See [LICENSE](LICENSE) for details.

## Author

Renato Umeton - Office of Data Science, St. Jude Children's Research Hospital
