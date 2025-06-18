"""Transformer for converting tokens to arXiv queries."""

from __future__ import annotations

import datetime

import arxiv

from .constants import DEFAULT_TIMEZONE_OFFSET
from .control_data import ControlDataExtractor
from .parentheses_processor import ParenthesesProcessor
from .query_builder import QueryStringBuilder
from .token_converter import TokenToQueryConverter
from .types import Token, TokenType


class QueryTransformer:
    """Transforms tokens into arXiv Search objects."""

    def __init__(self, timezone_offset: int = DEFAULT_TIMEZONE_OFFSET) -> None:
        self.timezone_offset = timezone_offset
        self.timezone = datetime.timezone(datetime.timedelta(hours=timezone_offset))
        self.control_extractor = ControlDataExtractor(timezone_offset)
        self.parentheses_processor = ParenthesesProcessor()
        self.token_converter = TokenToQueryConverter()
        self.query_builder = QueryStringBuilder()

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

        # Convert each content token to query part using dedicated converter
        for token in content_tokens:
            query_part = self.token_converter.convert(token)
            if query_part:
                query_parts.append(query_part)

        # Build AND expression using dedicated builder
        return self.query_builder.build_and_expression(query_parts)


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

