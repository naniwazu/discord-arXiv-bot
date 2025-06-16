"""Transformer for converting tokens to arXiv queries."""

from __future__ import annotations

import arxiv

from .constants import (
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

    def __init__(self, timezone_offset: int = DEFAULT_TIMEZONE_OFFSET) -> None:
        self.timezone_offset = timezone_offset

    def transform(self, tokens: list[Token]) -> arxiv.Search:
        """Transform tokens into an arXiv Search object."""
        # Check if we have operators (Phase 2)
        has_operators = any(token.type in (TokenType.OR, TokenType.NOT) for token in tokens)
        
        if has_operators:
            return self._transform_with_operators(tokens)
        else:
            return self._transform_simple(tokens)

    def _transform_simple(self, tokens: list[Token]) -> arxiv.Search:
        """Transform tokens without operators (Phase 1 behavior)."""
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

        # Join query parts with AND
        query = " AND ".join(query_parts) if query_parts else ""

        return arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_criterion,
            sort_order=sort_order,
        )

    def _token_to_query_part(self, token: Token) -> str | None:
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

    def _transform_with_operators(self, tokens: list[Token]) -> arxiv.Search:
        """Transform tokens with support for operators (Phase 2)."""
        # Extract control tokens first
        query_tokens = []
        max_results = DEFAULT_RESULT_COUNT
        sort_criterion, sort_order = DEFAULT_SORT

        # Separate query tokens from control tokens
        for token in tokens:
            if token.type == TokenType.NUMBER:
                max_results = int(token.value)
            elif token.type == TokenType.SORT:
                sort_criterion, sort_order = SORT_MAPPINGS[token.value]
            else:
                query_tokens.append(token)

        # Parse query with operators
        query = self._parse_query_expression(query_tokens)

        return arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_criterion,
            sort_order=sort_order,
        )

    def _parse_query_expression(self, tokens: list[Token]) -> str:
        """Parse query tokens with operator precedence."""
        if not tokens:
            return ""

        # Split by OR operators first (lowest precedence)
        or_groups = self._split_by_operator(tokens, TokenType.OR)
        
        if len(or_groups) > 1:
            # Multiple OR groups - join with OR
            group_queries = []
            for group in or_groups:
                group_query = self._parse_and_expression(group)
                if group_query:
                    group_queries.append(group_query)
            
            if len(group_queries) == 1:
                return group_queries[0]
            elif len(group_queries) > 1:
                return f"({' OR '.join(group_queries)})"
            else:
                return ""
        else:
            # No OR operators, process as AND expression
            return self._parse_and_expression(tokens)

    def _parse_and_expression(self, tokens: list[Token]) -> str:
        """Parse AND expression with NOT operators."""
        if not tokens:
            return ""

        # Process NOT operators
        query_parts = []
        i = 0
        
        while i < len(tokens):
            token = tokens[i]
            
            if token.type == TokenType.NOT:
                # NOT operator - negate the next token
                if i + 1 < len(tokens):
                    next_token = tokens[i + 1]
                    next_query = self._token_to_query_part(next_token)
                    if next_query:
                        query_parts.append(f"NOT {next_query}")
                    i += 2  # Skip both NOT and the next token
                else:
                    # NOT at end - ignore it
                    i += 1
            else:
                # Regular token
                query_part = self._token_to_query_part(token)
                if query_part:
                    query_parts.append(query_part)
                i += 1

        return " AND ".join(query_parts) if query_parts else ""

    def _split_by_operator(self, tokens: list[Token], operator_type: TokenType) -> list[list[Token]]:
        """Split tokens by the specified operator."""
        groups = []
        current_group = []
        
        for token in tokens:
            if token.type == operator_type:
                if current_group:
                    groups.append(current_group)
                    current_group = []
            else:
                current_group.append(token)
        
        if current_group:
            groups.append(current_group)
        
        return groups if groups else [[]]
