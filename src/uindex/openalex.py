"""OpenAlex API client for citation data."""

import httpx


class OpenAlexClient:
    """Client for fetching citation counts from OpenAlex."""

    BASE_URL = "https://api.openalex.org"
    BATCH_SIZE = 50

    def __init__(self, timeout: float = 30.0):
        self.client = httpx.Client(timeout=timeout)

    def get_citations_by_dois(self, dois: list[str]) -> dict[str, int]:
        """Get citation counts for a list of DOIs.

        Returns a dict mapping DOI -> citation count.
        DOIs not found in OpenAlex are omitted from the result.
        """
        if not dois:
            return {}

        results = {}

        # Process in batches of 50
        for i in range(0, len(dois), self.BATCH_SIZE):
            batch = dois[i:i + self.BATCH_SIZE]
            batch_results = self._fetch_batch(batch)
            results.update(batch_results)

        return results

    def _fetch_batch(self, dois: list[str]) -> dict[str, int]:
        """Fetch citation counts for a batch of DOIs."""
        # OpenAlex filter format: doi:10.1000/x|10.1000/y
        doi_filter = "|".join(dois)
        url = f"{self.BASE_URL}/works?filter=doi:{doi_filter}&select=doi,cited_by_count"

        response = self.client.get(url)
        response.raise_for_status()

        data = response.json()
        results = {}

        for work in data.get("results", []):
            doi = work.get("doi", "")
            if doi:
                # OpenAlex returns full URL, normalize to just the DOI
                normalized_doi = doi.replace("https://doi.org/", "")
                results[normalized_doi] = work.get("cited_by_count", 0)

        return results

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()
