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

        # Check categories are valid
        for token in tokens:
            if token.type == TokenType.CATEGORY:
                category = token.value.lower()
                # Check if it's a shortcut or a valid category
                if (category not in CATEGORY_SHORTCUTS and
                    category not in CATEGORY_CORRECTIONS and
                    not self._is_valid_category_pattern(category)):
                    return ValidationResult(
                        is_valid=False,
                        error=f"Category not found: #{token.value}",
                    )

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

        # Check for valid operator usage
        for i, token in enumerate(tokens):
            if token.type == TokenType.OR:
                if i == 0 or i == len(tokens) - 1:
                    return ValidationResult(is_valid=False, error="Invalid OR operator placement")
                # Check that OR is between valid operands
                prev_token = tokens[i - 1]
                next_token = tokens[i + 1]
                valid_operand_types = {
                    TokenType.KEYWORD, TokenType.AUTHOR, TokenType.CATEGORY,
                    TokenType.ALL_FIELDS, TokenType.ABSTRACT, TokenType.PHRASE,
                    TokenType.RPAREN,
                }
                if (prev_token.type not in valid_operand_types or
                    (next_token.type not in valid_operand_types and
                     next_token.type != TokenType.LPAREN)):
                    return ValidationResult(is_valid=False, error="Invalid OR operator usage")

        return ValidationResult(is_valid=True)

    def _is_valid_category_pattern(self, category: str) -> bool:
        """Check if a category follows valid arXiv category pattern."""
        import re
        pattern = r"^[a-z]+[-.]?[a-z]*$"
        return bool(re.match(pattern, category))
