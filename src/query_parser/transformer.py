"""Transformer for converting tokens to arXiv queries."""

from __future__ import annotations

import datetime
from typing import List, Optional, Tuple

import arxiv

from .constants import (
    ARXIV_FIELDS,
    CATEGORY_CORRECTIONS,
    CATEGORY_SHORTCUTS,
    DEFAULT_RESULT_COUNT,
    DEFAULT_SORT,
    DEFAULT_TIMEZONE_OFFSET,
    SORT_MAPPINGS,
)
from .types import Token, TokenType


class QueryTransformer:
    """Transforms tokens into arXiv Search objects."""

    def __init__(self, timezone_offset: int = DEFAULT_TIMEZONE_OFFSET):
        self.timezone_offset = timezone_offset

    def transform(self, tokens: List[Token]) -> arxiv.Search:
        """Transform tokens into an arXiv Search object."""
        # Extract components
        query_parts = []
        max_results = DEFAULT_RESULT_COUNT
        sort_criterion, sort_order = DEFAULT_SORT

        # Group tokens by type
        for token in tokens:
            if token.type == TokenType.NUMBER:
                max_results = int(token.value)
            elif token.type == TokenType.SORT:
                sort_criterion, sort_order = SORT_MAPPINGS[token.value]
            else:
                # Convert token to query part
                query_part = self._token_to_query_part(token)
                if query_part:
                    query_parts.append(query_part)

        # Join query parts (simple AND for now, Phase 1)
        query = " AND ".join(query_parts) if query_parts else ""

        return arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_criterion,
            sort_order=sort_order,
        )

    def _token_to_query_part(self, token: Token) -> Optional[str]:
        """Convert a single token to an arXiv query part."""
        if token.type == TokenType.KEYWORD:
            # Default to title search
            return f"ti:{token.value}"

        if token.type == TokenType.AUTHOR:
            return f"au:{token.value}"

        if token.type == TokenType.CATEGORY:
            category = self._normalize_category(token.value)
            return f"cat:{category}"

        if token.type == TokenType.ALL_FIELDS:
            return f"all:{token.value}"

        if token.type == TokenType.ABSTRACT:
            return f"abs:{token.value}"

        if token.type == TokenType.PHRASE:
            # Default to title search for phrases
            return f'ti:"{token.value}"'

        # Phase 1: Ignore operators and parentheses for now
        return None

    def _normalize_category(self, category: str) -> str:
        """Normalize category name."""
        category_lower = category.lower()

        # Check for shortcuts first
        if category_lower in CATEGORY_SHORTCUTS:
            return CATEGORY_SHORTCUTS[category_lower]

        # Check for case corrections
        if category_lower in CATEGORY_CORRECTIONS:
            return CATEGORY_CORRECTIONS[category_lower]

        # Return as-is if no correction needed
        return category

    def transform_with_operators(self, tokens: List[Token]) -> arxiv.Search:
        """Transform tokens with support for operators (Phase 2)."""
        # This will be implemented in Phase 2
        # For now, fall back to simple transform
        return self.transform(tokens)
