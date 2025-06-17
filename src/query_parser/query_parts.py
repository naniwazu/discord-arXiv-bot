"""Immutable query part structures for clean data flow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class QueryPart:
    """Represents an immutable part of the final query."""

    field: str | None  # Field prefix like "au", "cat", "ti", etc.
    content: str  # The actual search content
    is_negated: bool = False  # Whether this part should be negated with NOT

    def to_query_string(self) -> str:
        """Convert to arXiv query string format."""
        field_prefix = f"{self.field}:" if self.field else "ti:"
        query_str = f"{field_prefix}{self.content}"

        if self.is_negated:
            query_str = f"NOT {query_str}"

        return query_str


@dataclass(frozen=True)
class GroupedQuery:
    """Represents a grouped query expression (e.g., from parentheses)."""

    field: str | None  # Optional field prefix for the entire group
    parts: list[QueryPart]  # Parts within the group
    operator: Literal["AND", "OR"] = "AND"  # How parts are combined
    is_negated: bool = False  # Whether the entire group is negated

    def to_query_string(self) -> str:
        """Convert to arXiv query string format."""
        if not self.parts:
            return ""

        # Build inner query
        part_strings = [part.to_query_string() for part in self.parts]
        inner_query = f" {self.operator} ".join(part_strings)

        # Apply field prefix if specified
        query_str = f"{self.field}:({inner_query})" if self.field else f"({inner_query})"

        # Apply negation if needed
        if self.is_negated:
            query_str = f"NOT {query_str}"

        return query_str


class QueryPartBuilder:
    """Builder for creating QueryPart instances from tokens."""

    def __init__(self) -> None:
        """Initialize field mappings."""
        self.field_mappings = {
            "AUTHOR": "au",
            "CATEGORY": "cat",
            "ALL_FIELDS": "all",
            "ABSTRACT": "abs",
            "KEYWORD": "ti",  # Default to title search
            "PHRASE": "ti",  # Phrases also default to title
        }

    def from_token(self, token_type: str, value: str, *, is_negated: bool = False) -> QueryPart:
        """Create QueryPart from token information."""
        field = self.field_mappings.get(token_type)

        # Handle special formatting for phrases and quoted content
        if (" " in value or '"' in value) and not (value.startswith('"') and value.endswith('"')):
            value = f'"{value}"'

        return QueryPart(field=field, content=value, is_negated=is_negated)

    def from_field_and_content(
        self,
        field: str | None,
        content: str,
        *,
        is_negated: bool = False,
    ) -> QueryPart:
        """Create QueryPart with explicit field and content."""
        # Handle special formatting for quoted content
        needs_quotes = " " in content or '"' in content
        not_already_quoted = not (content.startswith('"') and content.endswith('"'))
        if needs_quotes and not_already_quoted:
            content = f'"{content}"'

        return QueryPart(field=field, content=content, is_negated=is_negated)


class QueryCombiner:
    """Combines QueryParts and GroupedQueries into final query strings."""

    def combine_with_and(self, items: list[QueryPart | GroupedQuery]) -> str:
        """Combine query items with AND operator."""
        if not items:
            return ""

        query_strings = [item.to_query_string() for item in items if item.to_query_string()]
        return " AND ".join(query_strings)

    def combine_with_or(self, items: list[QueryPart | GroupedQuery]) -> str:
        """Combine query items with OR operator."""
        if not items:
            return ""

        query_strings = [item.to_query_string() for item in items if item.to_query_string()]

        if len(query_strings) == 1:
            return query_strings[0]
        if len(query_strings) > 1:
            return f"({' OR '.join(query_strings)})"
        return ""

    def combine_mixed(self, or_groups: list[list[QueryPart | GroupedQuery]]) -> str:
        """Combine groups of items, where each group is AND-ed, and groups are OR-ed."""
        if not or_groups:
            return ""

        group_strings = []
        for group in or_groups:
            group_str = self.combine_with_and(group)
            if group_str:
                group_strings.append(group_str)

        return self.combine_with_or(
            [QueryPart(field=None, content=group_str) for group_str in group_strings],
        )
