"""Transformer for converting tokens to arXiv queries."""

from __future__ import annotations

import datetime

import arxiv

from .constants import (
    CATEGORY_CORRECTIONS,
    CATEGORY_SHORTCUTS,
    DEFAULT_TIMEZONE_OFFSET,
)
from .control_data import ControlDataExtractor
from .parentheses_processor import ParenthesesProcessor
from .types import Token, TokenType


class QueryTransformer:
    """Transforms tokens into arXiv Search objects."""

    def __init__(self, timezone_offset: int = DEFAULT_TIMEZONE_OFFSET) -> None:
        self.timezone_offset = timezone_offset
        self.timezone = datetime.timezone(datetime.timedelta(hours=timezone_offset))
        self.control_extractor = ControlDataExtractor(timezone_offset)
        self.parentheses_processor = ParenthesesProcessor()

    def transform(self, tokens: list[Token]) -> arxiv.Search:
        """Transform tokens into an arXiv Search object."""
        # Extract control data (eliminates duplicate logic)
        control_data, content_tokens = self.control_extractor.extract(tokens)

        # Check if we have operators or parentheses (Phase 2/3)
        has_operators = any(token.type in (TokenType.OR, TokenType.NOT) for token in content_tokens)
        has_parentheses = any(
            token.type in (TokenType.LPAREN, TokenType.RPAREN) for token in content_tokens
        )

        if has_operators or has_parentheses:
            query = self._build_complex_query(content_tokens)
        else:
            query = self._build_simple_query(content_tokens)

        # Add date range if specified
        date_query = self.control_extractor.build_date_query(control_data)
        if date_query:
            query = f"({query}) AND {date_query}" if query else date_query

        return arxiv.Search(
            query=query,
            max_results=control_data.max_results,
            sort_by=control_data.sort_criterion,
            sort_order=control_data.sort_order,
        )

    def _build_simple_query(self, content_tokens: list[Token]) -> str:
        """Build simple AND-connected query from content tokens."""
        query_parts = []

        # Convert each content token to query part
        for token in content_tokens:
            query_part = self._token_to_query_part(token)
            if query_part:
                query_parts.append(query_part)

        # Join query parts with AND
        return " AND ".join(query_parts) if query_parts else ""

    def _token_to_query_part(self, token: Token) -> str | None:
        """Convert a single token to an arXiv query part."""
        if token.type == TokenType.KEYWORD:
            return self._handle_keyword_token(token)

        field_mapping = {
            TokenType.AUTHOR: "au",
            TokenType.CATEGORY: "cat",
            TokenType.ALL_FIELDS: "all",
            TokenType.ABSTRACT: "abs",
        }

        if token.type in field_mapping:
            field_prefix = field_mapping[token.type]
            if token.type == TokenType.CATEGORY:
                value = self._normalize_category(token.value)
            else:
                value = token.value

            # Add quotes if value contains spaces or if it came from a quoted field
            if " " in value or ('"' in value):
                # If value already has quotes, use as-is, otherwise add quotes
                if value.startswith('"') and value.endswith('"'):
                    return f"{field_prefix}:{value}"
                return f'{field_prefix}:"{value}"'
            return f"{field_prefix}:{value}"

        if token.type == TokenType.PHRASE:
            return f'ti:"{token.value}"'

        # Phase 1: Ignore operators and parentheses for now
        return None

    def _handle_keyword_token(self, token: Token) -> str:
        """Handle keyword token processing."""
        # Check if this is a grouped expression (from parentheses processing)
        if token.value.startswith("(") and token.value.endswith(")"):
            return token.value  # Already processed grouped expression
        # Default to title search
        return f"ti:{token.value}"

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

    def _build_complex_query(self, content_tokens: list[Token]) -> str:
        """Build complex query with operators and parentheses from content tokens."""
        return self._parse_query_expression(content_tokens)

    def _parse_query_expression(self, tokens: list[Token]) -> str:
        """Parse query tokens with operator precedence and parentheses.

        Now uses stack-based parentheses processing instead of recursion.
        """
        if not tokens:
            return ""

        # Use new stack-based parentheses processor (no recursion risk)
        processed_items = self.parentheses_processor.process(tokens)

        # Build query from processed items (mix of tokens and grouped expressions)
        return self.parentheses_processor.build_query_from_processed_items(processed_items)

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

    def _split_by_operator(
        self,
        tokens: list[Token],
        operator_type: TokenType,
    ) -> list[list[Token]]:
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
