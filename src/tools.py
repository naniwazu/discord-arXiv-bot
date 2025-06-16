from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from typing import NamedTuple

import arxiv

logger = logging.getLogger(__name__)

# Try to use new parser, fall back to legacy implementation
try:
    from query_parser import QueryParser
    USE_NEW_PARSER = True
except ImportError:
    USE_NEW_PARSER = False
    logger.warning("New query parser not available, using legacy implementation")

# Constants
DEFAULT_RESULT_COUNT: int = 10
RESULT_COUNT_LIMIT: int = 1000
JST_OFFSET_HOURS: int = -9
JST_TIMEZONE = datetime.timezone(datetime.timedelta(hours=JST_OFFSET_HOURS))

# Date format constants
DATE_FORMAT_YYYYMMDD = "%Y%m%d"
DATE_FORMAT_YYYYMMDDHHMM = "%Y%m%d%H%M"
DATE_FORMAT_YYYYMMDDHHMMSS = "%Y%m%d%H%M%S"

# Date string length constants
YYYYMMDD_LENGTH = 8
YYYYMMDDHHMM_LENGTH = 12
YYYYMMDDHHMMSS_LENGTH = 14

SORTBY_DICT: dict[str, arxiv.SortCriterion] = {
    "L": arxiv.SortCriterion.LastUpdatedDate,
    "l": arxiv.SortCriterion.LastUpdatedDate,
    "R": arxiv.SortCriterion.Relevance,
    "r": arxiv.SortCriterion.Relevance,
    "S": arxiv.SortCriterion.SubmittedDate,
    "s": arxiv.SortCriterion.SubmittedDate,
}

SEARCH_FIELDS: set[str] = {
    "ti",
    "au",
    "abs",
    "co",
    "jr",
    "cat",
    "rn",
    "id",
    "all",
}

DEFAULT_SINCE: datetime.datetime = datetime.datetime(
    1900, 1, 1, 0, 0, 0, tzinfo=JST_TIMEZONE,
)
DEFAULT_UNTIL: datetime.datetime = datetime.datetime(
    2100, 1, 1, 0, 0, 0, tzinfo=JST_TIMEZONE,
)


class DateParseResult(NamedTuple):
    """Result of date parsing operation."""

    success: bool
    datetime_obj: datetime.datetime | None = None
    error: str | None = None


@dataclass
class ParsedQuery:
    """Represents a parsed search query."""

    queries: list[str]
    max_results: int = DEFAULT_RESULT_COUNT
    since: datetime.datetime = DEFAULT_SINCE
    until: datetime.datetime = DEFAULT_UNTIL
    sort_by: arxiv.SortCriterion = arxiv.SortCriterion.SubmittedDate


def parse(search_query: str) -> arxiv.Search | None:
    """Parse a search query string into an arxiv.Search object.

    This function maintains backward compatibility while optionally using
    the new query parser when available.
    """
    # Use new parser if available
    if USE_NEW_PARSER:
        parser = QueryParser()
        result = parser.parse(search_query)
        if result.success:
            return result.search
        # Fall back to legacy parser on error
        logger.info("New parser failed: %s, falling back to legacy parser", result.error)
        return _parse_legacy(search_query)

    # Use legacy parser
    return _parse_legacy(search_query)


def _parse_legacy(search_query: str) -> arxiv.Search | None:
    """Legacy parse implementation for backward compatibility."""
    queries: list[str] = []
    max_results: int = DEFAULT_RESULT_COUNT
    since: datetime.datetime = DEFAULT_SINCE
    until: datetime.datetime = DEFAULT_UNTIL
    sort_by: arxiv.SortCriterion = arxiv.SortCriterion.SubmittedDate
    chunks: list[str] = list(search_query.split())

    for chunk in chunks:
        if chunk in SORTBY_DICT:
            sort_by = SORTBY_DICT[chunk]
        elif chunk[0] == "<":
            continue  # ignore mention chunk
        elif chunk.isdecimal():
            new_max_results = int(chunk)
            if 1 <= new_max_results <= RESULT_COUNT_LIMIT:
                max_results = new_max_results
        elif chunk.count(":") == 1:
            prefix, body = chunk.split(":")
            if prefix == "since":
                if len(body) == YYYYMMDD_LENGTH:
                    since = datetime.datetime.strptime(body, DATE_FORMAT_YYYYMMDD).replace(
                        tzinfo=JST_TIMEZONE,
                    )
                elif len(body) == YYYYMMDDHHMM_LENGTH:
                    since = datetime.datetime.strptime(body, DATE_FORMAT_YYYYMMDDHHMM).replace(
                        tzinfo=JST_TIMEZONE,
                    )
                elif len(body) == YYYYMMDDHHMMSS_LENGTH:
                    since = datetime.datetime.strptime(body, DATE_FORMAT_YYYYMMDDHHMMSS).replace(
                        tzinfo=JST_TIMEZONE,
                    )
                else:
                    return None
                continue
            if prefix == "until":
                if len(body) == YYYYMMDD_LENGTH:
                    # end of the day
                    until = (datetime.datetime.strptime(body, DATE_FORMAT_YYYYMMDD).replace(
                        tzinfo=JST_TIMEZONE,
                    ) + datetime.timedelta(days=1))
                elif len(body) == YYYYMMDDHHMM_LENGTH:
                    until = datetime.datetime.strptime(body, DATE_FORMAT_YYYYMMDDHHMM).replace(
                        tzinfo=JST_TIMEZONE,
                    )
                elif len(body) == YYYYMMDDHHMMSS_LENGTH:
                    until = datetime.datetime.strptime(body, DATE_FORMAT_YYYYMMDDHHMMSS).replace(
                        tzinfo=JST_TIMEZONE,
                    )
                else:
                    return None
                continue
            if prefix not in SEARCH_FIELDS:
                continue
            keywords = body.split(",")
            queries.extend([f"{prefix}:{keyword}" for keyword in keywords])
        else:
            return None

    if since != DEFAULT_SINCE or until != DEFAULT_UNTIL:
        since_str = datetime.datetime.strftime(since, DATE_FORMAT_YYYYMMDDHHMMSS)
        until_str = datetime.datetime.strftime(until, DATE_FORMAT_YYYYMMDDHHMMSS)
        queries.append(f"submittedDate:[{since_str} TO {until_str}]")

    query = " AND ".join(queries)
    return arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=sort_by,
        sort_order=arxiv.SortOrder.Descending,
    )
