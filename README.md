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
U-index: 12
h-index (estimated): 18

Qualifying papers (first/last author): 28
├── With citations: 25
└── Unmatched (no DOI or not in OpenAlex): 3

Top qualifying papers:
  1. Paper Title (2023) - 156 citations [first author]
  2. Another Paper (2021) - 89 citations [last author]
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
