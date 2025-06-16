"""Validator for query parser."""

from __future__ import annotations

from .constants import CATEGORY_CORRECTIONS, CATEGORY_SHORTCUTS, RESULT_COUNT_LIMIT
from .types import Token, TokenType, ValidationResult


class QueryValidator:
    """Validates tokens and provides error messages."""

    def validate(self, tokens: list[Token]) -> ValidationResult:
        """Validate a list of tokens."""
        # Check for empty query
        if not tokens:
            return ValidationResult(is_valid=False, error="Empty query")

        # Check numbers are within valid range
        for token in tokens:
            if token.type == TokenType.NUMBER:
                try:
                    num = int(token.value)
                    if num < 1 or num > RESULT_COUNT_LIMIT:
                        return ValidationResult(
                            is_valid=False,
                            error=f"Number of results must be between 1-{RESULT_COUNT_LIMIT}",
                        )
                except ValueError:
                    return ValidationResult(is_valid=False, error=f"Invalid number: {token.value}")

        # Note: We don't strictly validate categories anymore for legacy compatibility
        # Invalid categories will be passed through to arXiv API which will handle them

        # Check for balanced parentheses
        paren_count = 0
        for token in tokens:
            if token.type == TokenType.LPAREN:
                paren_count += 1
            elif token.type == TokenType.RPAREN:
                paren_count -= 1
                if paren_count < 0:
                    return ValidationResult(is_valid=False, error="Unbalanced parentheses")

        if paren_count != 0:
            return ValidationResult(is_valid=False, error="Unbalanced parentheses")

        # Note: OR/NOT operators are not implemented in Phase 1
        # They will be ignored in the transformer for now

        return ValidationResult(is_valid=True)

    def _is_valid_category_pattern(self, category: str) -> bool:
        """Check if a category follows valid arXiv category pattern."""
        import re
        pattern = r"^[a-z]+[-.]?[a-z]*$"
        return bool(re.match(pattern, category))
