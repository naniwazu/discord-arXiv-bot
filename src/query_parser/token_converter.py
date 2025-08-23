"""Token to query string converter with single responsibility."""

from __future__ import annotations

from .constants import CATEGORY_CORRECTIONS, CATEGORY_SHORTCUTS
from .types import Token, TokenType


class TokenToQueryConverter:
    """Converts tokens to arXiv query string parts.

    Single responsibility: Token → Query string conversion only.
    Eliminates duplication between transformer.py and parentheses_processor.py.
    """

    def __init__(self) -> None:
        """Initialize field mappings."""
        self.field_mapping = {
            TokenType.AUTHOR: "au",
            TokenType.CATEGORY: "cat",
            TokenType.ALL_FIELDS: "all",
            TokenType.ABSTRACT: "abs",
        }

    def convert(self, token: Token) -> str | None:
        """Convert a single token to an arXiv query part."""
        if token.type == TokenType.KEYWORD:
            return self._handle_keyword_token(token)

        if token.type == TokenType.PHRASE:
            return self._handle_phrase_token(token)

        if token.type in self.field_mapping:
            return self._handle_field_token(token)

        # Operators and parentheses are not handled here
        return None

    def _handle_keyword_token(self, token: Token) -> str:
        """Handle keyword token processing."""
        # Check if this is a grouped expression (from parentheses processing)
        if token.value.startswith("(") and token.value.endswith(")"):
            return token.value  # Already processed grouped expression
        # Default to title search
        return f"ti:{token.value}"

    def _handle_phrase_token(self, token: Token) -> str:
        """Handle phrase token (quoted strings)."""
        return f'ti:"{token.value}"'

    def _handle_field_token(self, token: Token) -> str:
        """Handle field prefix tokens (author, category, etc.)."""
        field_prefix = self.field_mapping[token.type]
        value = token.value

        # Special handling for category field
        if token.type == TokenType.CATEGORY:
            value = self._normalize_category(value)

        # Special handling for quoted values
        if " " in value or ('"' in value):
            # If value already has quotes, use as-is, otherwise add quotes
            if value.startswith('"') and value.endswith('"'):
                return f"{field_prefix}:{value}"
            return f'{field_prefix}:"{value}"'

        return f"{field_prefix}:{value}"

    def _normalize_category(self, category: str) -> str:
        """Normalize category name with shortcuts and corrections."""
        category_lower = category.lower()

        # Check for shortcuts first
        if category_lower in CATEGORY_SHORTCUTS:
            return CATEGORY_SHORTCUTS[category_lower]

        # Check for corrections
        if category_lower in CATEGORY_CORRECTIONS:
            return CATEGORY_CORRECTIONS[category_lower]

        return category
