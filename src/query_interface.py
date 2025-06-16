"""Query interface for parsing search queries."""

from __future__ import annotations

from typing import TYPE_CHECKING

from query_parser import QueryParser

if TYPE_CHECKING:
    import arxiv


def parse(search_query: str) -> arxiv.Search | None:
    """Parse a search query string into an arxiv.Search object.

    Args:
        search_query: The query string to parse

    Returns:
        arxiv.Search object if parsing succeeds, None otherwise

    """
    parser = QueryParser()
    result = parser.parse(search_query)

    if result.success:
        return result.search

    # If parsing fails, return None
    return None


