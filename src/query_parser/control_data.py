"""Control data extraction and management for query parser."""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import arxiv

from .constants import DEFAULT_RESULT_COUNT, DEFAULT_SORT, DEFAULT_TIMEZONE_OFFSET, SORT_MAPPINGS
from .types import Token, TokenType

# Date format constants
DATE_FORMAT_YYYYMMDD = 8
DATE_FORMAT_YYYYMMDDHHMM = 12
DATE_FORMAT_YYYYMMDDHHMMSS = 14


@dataclass
class ControlData:
    """Query control parameters separated from content tokens."""

    max_results: int = DEFAULT_RESULT_COUNT
    sort_criterion: arxiv.SortCriterion = DEFAULT_SORT[0]  # type: ignore[name-defined]
    sort_order: arxiv.SortOrder = DEFAULT_SORT[1]  # type: ignore[name-defined]
    since_date: datetime.datetime | None = None
    until_date: datetime.datetime | None = None


class ControlDataExtractor:
    """Single responsibility: Extract control tokens from any token list."""

    def __init__(self, timezone_offset: int = DEFAULT_TIMEZONE_OFFSET) -> None:
        """Initialize with timezone for date parsing."""
        self.timezone_offset = timezone_offset
        self.timezone = datetime.timezone(datetime.timedelta(hours=timezone_offset))

    def extract(self, tokens: list[Token]) -> tuple[ControlData, list[Token]]:
        """Extract control data and return remaining content tokens.

        This eliminates the duplicate logic that existed in both
        _transform_simple and _transform_with_operators methods.

        Args:
            tokens: List of tokens to process

        Returns:
            Tuple of (control_data, content_tokens)

        """
        control = ControlData()
        content_tokens = []

        for token in tokens:
            if token.type == TokenType.NUMBER:
                control.max_results = int(token.value)
            elif token.type == TokenType.SORT:
                control.sort_criterion, control.sort_order = SORT_MAPPINGS[token.value.lower()]
            elif token.type == TokenType.DATE_GT:
                control.since_date = self._parse_date(token.value)
            elif token.type == TokenType.DATE_LT:
                control.until_date = self._parse_date(token.value)
                # For until dates, add one day if only date is specified (YYYYMMDD)
                if control.until_date and len(token.value) == DATE_FORMAT_YYYYMMDD:
                    control.until_date += datetime.timedelta(days=1)
            else:
                # All other tokens are content tokens
                content_tokens.append(token)

        return control, content_tokens

    def _parse_date(self, date_str: str) -> datetime.datetime | None:
        """Parse date string in various formats."""
        try:
            if len(date_str) == DATE_FORMAT_YYYYMMDD:  # YYYYMMDD
                return datetime.datetime.strptime(date_str, "%Y%m%d").replace(tzinfo=self.timezone)
            if len(date_str) == DATE_FORMAT_YYYYMMDDHHMM:  # YYYYMMDDHHMM
                return datetime.datetime.strptime(date_str, "%Y%m%d%H%M").replace(
                    tzinfo=self.timezone,
                )
            if len(date_str) == DATE_FORMAT_YYYYMMDDHHMMSS:  # YYYYMMDDHHMMSS
                return datetime.datetime.strptime(date_str, "%Y%m%d%H%M%S").replace(
                    tzinfo=self.timezone,
                )
        except ValueError:
            pass
        return None

    def build_date_query(self, control_data: ControlData) -> str | None:
        """Build arXiv date range query from control data."""
        since_date = control_data.since_date
        until_date = control_data.until_date

        if not since_date and not until_date:
            return None

        # Default bounds if not specified
        if not since_date:
            since_date = datetime.datetime(1900, 1, 1, 0, 0, 0, tzinfo=self.timezone)
        if not until_date:
            until_date = datetime.datetime(2100, 1, 1, 0, 0, 0, tzinfo=self.timezone)

        since_str = since_date.strftime("%Y%m%d%H%M%S")
        until_str = until_date.strftime("%Y%m%d%H%M%S")

        return f"submittedDate:[{since_str} TO {until_str}]"
