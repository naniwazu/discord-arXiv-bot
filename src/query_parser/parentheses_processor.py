"""Stack-based parentheses processor for query parser."""

from __future__ import annotations

from dataclasses import dataclass

from .token_converter import TokenToQueryConverter
from .types import Token, TokenType


@dataclass
class GroupedExpression:
    """Represents a grouped expression without mutating original tokens."""

    field_prefix: str | None
    content: str
    position: int

    def to_query_string(self) -> str:
        """Convert to query string format."""
        if self.field_prefix:
            return f"{self.field_prefix}({self.content})"
        return f"({self.content})"


class ParenthesesProcessor:
    """Non-recursive, stack-based parentheses processing."""

    def __init__(self) -> None:
        """Initialize field prefix mappings and token converter."""
        self.field_prefixes = {
            TokenType.AUTHOR: "au:",
            TokenType.CATEGORY: "cat:",
            TokenType.ALL_FIELDS: "all:",
            TokenType.ABSTRACT: "abs:",
        }
        self.token_converter = TokenToQueryConverter()

    def process(self, tokens: list[Token]) -> list[Token | GroupedExpression]:
        """Process parentheses safely without recursion.

        Returns a list of tokens and grouped expressions that can be
        processed by the query builder.
        """
        if not any(t.type in (TokenType.LPAREN, TokenType.RPAREN) for t in tokens):
            return tokens

        result = []
        stack = []  # Stack of (start_index, field_prefix)

        for token in tokens:
            if token.type == TokenType.LPAREN:
                # Check for field prefix before parenthesis
                field_prefix = None
                if (
                    result
                    and isinstance(result[-1], Token)
                    and result[-1].type in self.field_prefixes
                ):
                    field_token = result.pop()
                    field_prefix = self.field_prefixes[field_token.type]

                # Push opening parenthesis info to stack
                stack.append((len(result), field_prefix, token.position))

            elif token.type == TokenType.RPAREN:
                if not stack:
                    # Unmatched closing paren - treat as regular token
                    result.append(token)
                    continue

                # Pop from stack and create grouped expression
                start_index, field_prefix, paren_pos = stack.pop()

                # Extract tokens since opening parenthesis
                inner_tokens = result[start_index:]
                result = result[:start_index]

                # Build inner expression using the existing query building logic
                inner_content = self._build_inner_expression(inner_tokens)

                if inner_content:
                    grouped = GroupedExpression(field_prefix, inner_content, paren_pos)
                    result.append(grouped)

            else:
                # Regular token
                result.append(token)

        # Handle unmatched opening parentheses (treat as regular tokens)
        while stack:
            start_index, field_prefix, paren_pos = stack.pop()
            # Add opening paren as regular token
            lparen_token = Token(TokenType.LPAREN, "(", paren_pos)
            result.insert(start_index, lparen_token)

            # Re-add field prefix if it was consumed
            if field_prefix:
                # Find the corresponding field token type
                field_type = self._field_prefix_to_type(field_prefix)
                field_value = field_prefix[:-1]  # Remove the ':'
                field_token = Token(field_type, field_value, paren_pos - 1)
                result.insert(start_index, field_token)

        return result

    def build_query_from_processed_items(self, items: list[Token | GroupedExpression]) -> str:
        """Public method to build query from processed items."""
        return self._build_inner_expression(items)

    def _build_inner_expression(self, tokens: list[Token | GroupedExpression]) -> str:
        """Build expression from tokens inside parentheses."""
        if not tokens:
            return ""

        # Handle OR operators (lowest precedence)
        or_groups = self._split_by_or(tokens)

        if len(or_groups) > 1:
            # Multiple OR groups
            group_strs = []
            for group in or_groups:
                group_str = self._build_and_expression(group)
                if group_str:
                    group_strs.append(group_str)
            return " OR ".join(group_strs) if group_strs else ""
        # Single group - process as AND expression
        return self._build_and_expression(tokens)

    def _split_by_or(
        self,
        tokens: list[Token | GroupedExpression],
    ) -> list[list[Token | GroupedExpression]]:
        """Split tokens by OR operators."""
        groups = []
        current_group = []

        for token in tokens:
            if isinstance(token, Token) and token.type == TokenType.OR:
                if current_group:
                    groups.append(current_group)
                    current_group = []
            else:
                current_group.append(token)

        if current_group:
            groups.append(current_group)

        return groups if groups else [[]]

    def _build_and_expression(self, tokens: list[Token | GroupedExpression]) -> str:
        """Build AND expression from tokens, handling NOT operators."""
        if not tokens:
            return ""

        query_parts = []
        i = 0

        while i < len(tokens):
            token = tokens[i]

            if isinstance(token, Token) and token.type == TokenType.NOT:
                # NOT operator - negate the next token
                if i + 1 < len(tokens):
                    next_item = tokens[i + 1]
                    next_query = self._token_to_query_part(next_item)
                    if next_query:
                        query_parts.append(f"NOT {next_query}")
                    i += 2  # Skip both NOT and the next token
                else:
                    # NOT at end - ignore it
                    i += 1
            else:
                # Regular token or grouped expression
                query_part = self._token_to_query_part(token)
                if query_part:
                    query_parts.append(query_part)
                i += 1

        return " AND ".join(query_parts) if query_parts else ""

    def _token_to_query_part(self, item: Token | GroupedExpression) -> str | None:
        """Convert token or grouped expression to query part."""
        if isinstance(item, GroupedExpression):
            return item.to_query_string()
        if isinstance(item, Token):
            return self.token_converter.convert(item)
        return None

    def _field_prefix_to_type(self, prefix: str) -> TokenType:
        """Convert field prefix back to token type."""
        prefix_to_type = {
            "au:": TokenType.AUTHOR,
            "cat:": TokenType.CATEGORY,
            "all:": TokenType.ALL_FIELDS,
            "abs:": TokenType.ABSTRACT,
        }
        return prefix_to_type.get(prefix, TokenType.KEYWORD)
