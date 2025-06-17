"""Transformer for converting tokens to arXiv queries."""

from __future__ import annotations

import datetime

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
        self.timezone = datetime.timezone(datetime.timedelta(hours=timezone_offset))

    def transform(self, tokens: list[Token]) -> arxiv.Search:
        """Transform tokens into an arXiv Search object."""
        # Check if we have operators or parentheses (Phase 2/3)
        has_operators = any(token.type in (TokenType.OR, TokenType.NOT) for token in tokens)
        has_parentheses = any(
            token.type in (TokenType.LPAREN, TokenType.RPAREN) for token in tokens
        )

        if has_operators or has_parentheses:
            return self._transform_with_operators(tokens)
        return self._transform_simple(tokens)

    def _transform_simple(self, tokens: list[Token]) -> arxiv.Search:
        """Transform tokens without operators (Phase 1 behavior)."""
        # Extract components
        query_parts = []
        max_results = DEFAULT_RESULT_COUNT
        sort_criterion, sort_order = DEFAULT_SORT
        since_date = None
        until_date = None

        # Group tokens by type
        for token in tokens:
            if token.type == TokenType.NUMBER:
                max_results = int(token.value)
            elif token.type == TokenType.SORT:
                sort_criterion, sort_order = SORT_MAPPINGS[token.value]
            elif token.type == TokenType.DATE_GT:
                since_date = self._parse_date(token.value)
            elif token.type == TokenType.DATE_LT:
                until_date = self._parse_date(token.value)
                # For until dates, add one day if only date is specified (YYYYMMDD)
                if until_date and len(token.value) == 8:
                    until_date += datetime.timedelta(days=1)
            else:
                # Convert token to query part
                query_part = self._token_to_query_part(token)
                if query_part:
                    query_parts.append(query_part)

        # Add date range if specified
        if since_date or until_date:
            date_query = self._build_date_query(since_date, until_date)
            if date_query:
                query_parts.append(date_query)

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
            if ' ' in value or ('"' in value):
                # If value already has quotes, use as-is, otherwise add quotes
                if value.startswith('"') and value.endswith('"'):
                    return f"{field_prefix}:{value}"
                else:
                    return f'{field_prefix}:"{value}"'
            else:
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

    def _transform_with_operators(self, tokens: list[Token]) -> arxiv.Search:
        """Transform tokens with support for operators (Phase 2)."""
        # Extract control tokens first
        query_tokens = []
        max_results = DEFAULT_RESULT_COUNT
        sort_criterion, sort_order = DEFAULT_SORT
        since_date = None
        until_date = None

        # Separate query tokens from control tokens
        for token in tokens:
            if token.type == TokenType.NUMBER:
                max_results = int(token.value)
            elif token.type == TokenType.SORT:
                sort_criterion, sort_order = SORT_MAPPINGS[token.value]
            elif token.type == TokenType.DATE_GT:
                since_date = self._parse_date(token.value)
            elif token.type == TokenType.DATE_LT:
                until_date = self._parse_date(token.value)
                # For until dates, add one day if only date is specified (YYYYMMDD)
                if until_date and len(token.value) == 8:
                    until_date += datetime.timedelta(days=1)
            else:
                query_tokens.append(token)

        # Parse query with operators
        query = self._parse_query_expression(query_tokens)

        # Add date range if specified
        if since_date or until_date:
            date_query = self._build_date_query(since_date, until_date)
            if date_query:
                if query:
                    query = f"({query}) AND {date_query}"
                else:
                    query = date_query

        return arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_criterion,
            sort_order=sort_order,
        )

    def _parse_query_expression(self, tokens: list[Token]) -> str:
        """Parse query tokens with operator precedence and parentheses."""
        if not tokens:
            return ""

        # First handle parentheses (highest precedence)
        tokens = self._process_parentheses(tokens)

        # Split by OR operators (lowest precedence)
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
            if len(group_queries) > 1:
                return f"({' OR '.join(group_queries)})"
            return ""
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

    def _split_by_operator(
        self, tokens: list[Token], operator_type: TokenType,
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

    def _process_parentheses(self, tokens: list[Token]) -> list[Token]:
        """Process parentheses by replacing them with grouped tokens."""
        if not any(token.type in (TokenType.LPAREN, TokenType.RPAREN) for token in tokens):
            return tokens

        result = []
        i = 0

        while i < len(tokens):
            token = tokens[i]

            if token.type == TokenType.LPAREN:
                i = self._process_single_parenthesis_group(tokens, i, result)
            else:
                result.append(token)
                i += 1

        return result

    def _process_single_parenthesis_group(
        self, tokens: list[Token], start_idx: int, result: list[Token],
    ) -> int:
        """Process a single parenthesis group and return the next index."""
        # Check if previous token is a field prefix
        field_context = self._extract_field_context(tokens, start_idx, result)

        # Find matching closing parenthesis
        end_idx = self._find_matching_parenthesis(tokens, start_idx)

        if end_idx == -1:
            # Unmatched parentheses - treat as regular token
            result.append(tokens[start_idx])
            return start_idx + 1

        # Extract and process inner tokens
        inner_tokens = tokens[start_idx + 1 : end_idx]
        if inner_tokens:
            inner_query = self._parse_parentheses_group(inner_tokens)
            if inner_query:
                grouped_token = self._create_grouped_token(
                    field_context, inner_query, tokens[start_idx].position,
                )
                result.append(grouped_token)

        return end_idx + 1

    def _extract_field_context(
        self, tokens: list[Token], start_idx: int, result: list[Token],
    ) -> Token | None:
        """Extract field context from previous token if applicable."""
        if start_idx == 0:
            return None

        prev_token = tokens[start_idx - 1]
        field_types = (
            TokenType.AUTHOR,
            TokenType.CATEGORY,
            TokenType.ALL_FIELDS,
            TokenType.ABSTRACT,
            TokenType.ARXIV_FIELD,
        )

        if prev_token.type in field_types:
            # Remove the previous field token from result since we'll combine it
            result.pop()
            return prev_token

        return None

    def _find_matching_parenthesis(self, tokens: list[Token], start_idx: int) -> int:
        """Find the index of the matching closing parenthesis."""
        paren_count = 1
        j = start_idx + 1

        while j < len(tokens) and paren_count > 0:
            if tokens[j].type == TokenType.LPAREN:
                paren_count += 1
            elif tokens[j].type == TokenType.RPAREN:
                paren_count -= 1
            j += 1

        return j - 1 if paren_count == 0 else -1

    def _create_grouped_token(
        self, field_context: Token | None, inner_query: str, position: int,
    ) -> Token:
        """Create a grouped token with optional field context."""
        if field_context:
            if field_context.type == TokenType.ARXIV_FIELD:
                field_prefix = f"{field_context.value}:"
            else:
                field_prefix = self._get_field_prefix(field_context.type)
            return Token(TokenType.KEYWORD, f"{field_prefix}({inner_query})", position)

        return Token(TokenType.KEYWORD, f"({inner_query})", position)

    def _get_field_prefix(self, token_type: TokenType) -> str:
        """Get the field prefix for a token type."""
        if token_type == TokenType.AUTHOR:
            return "au:"
        if token_type == TokenType.CATEGORY:
            return "cat:"
        if token_type == TokenType.ALL_FIELDS:
            return "all:"
        if token_type == TokenType.ABSTRACT:
            return "abs:"
        return "ti:"  # Default to title

    def _parse_parentheses_group(self, tokens: list[Token]) -> str:
        """Parse tokens inside parentheses without infinite recursion."""
        if not tokens:
            return ""

        # Check for nested parentheses and process them first
        if any(token.type in (TokenType.LPAREN, TokenType.RPAREN) for token in tokens):
            tokens = self._process_parentheses(tokens)

        # Now process OR operators
        or_groups = self._split_by_operator(tokens, TokenType.OR)

        if len(or_groups) > 1:
            # Multiple OR groups - join with OR
            group_queries = []
            for group in or_groups:
                group_query = self._parse_and_expression(group)
                if group_query:
                    group_queries.append(group_query)

            return " OR ".join(group_queries) if group_queries else ""
        # No OR operators, process as AND expression
        return self._parse_and_expression(tokens)

    def _parse_date(self, date_str: str) -> datetime.datetime | None:
        """Parse date string in various formats."""
        try:
            if len(date_str) == 8:  # YYYYMMDD
                return datetime.datetime.strptime(date_str, "%Y%m%d").replace(tzinfo=self.timezone)
            elif len(date_str) == 12:  # YYYYMMDDHHMM
                return datetime.datetime.strptime(date_str, "%Y%m%d%H%M").replace(tzinfo=self.timezone)
            elif len(date_str) == 14:  # YYYYMMDDHHMMSS
                return datetime.datetime.strptime(date_str, "%Y%m%d%H%M%S").replace(tzinfo=self.timezone)
        except ValueError:
            pass
        return None

    def _build_date_query(self, since_date: datetime.datetime | None, until_date: datetime.datetime | None) -> str | None:
        """Build arXiv date range query."""
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
