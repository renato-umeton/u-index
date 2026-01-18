# CLAUDE.md

This file provides guidance for AI assistants working with code in this repository.

## Project Overview

This repository implements the **Umeton Index (U-index)**, a bibliometric metric that modifies the h-index to count only publications where a researcher is first or last author. The metric is designed to measure research leadership impact by filtering out middle-author positions.

**Definition:** A researcher has Umeton index U if U of their first-or-last-authored papers have each been cited at least U times.

## Development Environment

Python 3.14 with pipenv:
```bash
pipenv install           # Install dependencies
pipenv shell             # Activate virtual environment
```

## Key Concepts (from manuscript)

- **Leadership subset L(R):** Papers where researcher R is first OR last author
- **Single-author papers:** Count as both first and last author
- **Co-first/co-last authors:** All marked authors qualify for that position
- **Corresponding author:** NOT used as a qualifying position

The metric is bounded by the standard h-index (U <= h) and is field-dependent - only meaningful in disciplines where author position conventions exist (biomedical, life sciences, experimental sciences).
