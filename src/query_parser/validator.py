"""Validator for query parser."""

from __future__ import annotations

import datetime
import re

from .constants import RESULT_COUNT_LIMIT
from .control_data import (
    DATE_FORMAT_YYYYMMDD,
    DATE_FORMAT_YYYYMMDDHHMM,
    DATE_FORMAT_YYYYMMDDHHMMSS,
)
from .types import Token, TokenType, ValidationResult


class QueryValidator:
    """Validates tokens and provides error messages."""

    def validate(self, tokens: list[Token]) -> ValidationResult:  # noqa: C901, PLR0911, PLR0912
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
            elif token.type in (TokenType.DATE_GT, TokenType.DATE_LT):
                # Validate date format
                if not self._is_valid_date_format(token.value):
                    return ValidationResult(
                        is_valid=False,
                        error=(
                            f"Invalid date format: {token.value}. "
                            "Use YYYYMMDD, YYYYMMDDHHMM, or YYYYMMDDHHMMSS"
                        ),
                    )
            elif token.type == TokenType.CATEGORY:
                # Validate category format
                if not self._is_valid_category_pattern(token.value):
                    return ValidationResult(
                        is_valid=False,
                        error=(
                            f"Invalid category format: {token.value}. "
                            "Use format like 'cs.AI' or 'physics'"
                        ),
                    )
            elif token.type == TokenType.KEYWORD and self._is_malformed_date(token.value):
                return ValidationResult(
                    is_valid=False,
                    error=(
                        f"Invalid date format: {token.value}. "
                        "Use YYYYMMDD, YYYYMMDDHHMM, or YYYYMMDDHHMMSS"
                    ),
                )

        # Check for balanced parentheses and empty parentheses
        paren_count = 0
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.type == TokenType.LPAREN:
                paren_count += 1
                # Check for empty parentheses
                if i + 1 < len(tokens) and tokens[i + 1].type == TokenType.RPAREN:
                    return ValidationResult(is_valid=False, error="Empty parentheses")
            elif token.type == TokenType.RPAREN:
                paren_count -= 1
                if paren_count < 0:
                    return ValidationResult(is_valid=False, error="Unbalanced parentheses")
            i += 1

        if paren_count != 0:
            return ValidationResult(is_valid=False, error="Unbalanced parentheses")

        # Validate OR/NOT operators (Phase 2)
        for i, token in enumerate(tokens):
            if token.type == TokenType.OR:
                if i == 0 or i == len(tokens) - 1:
                    return ValidationResult(is_valid=False, error="Invalid OR operator placement")
                # Check that OR is between valid operands
                prev_token = tokens[i - 1]
                next_token = tokens[i + 1]
                valid_operand_types = {
                    TokenType.KEYWORD,
                    TokenType.AUTHOR,
                    TokenType.CATEGORY,
                    TokenType.ALL_FIELDS,
                    TokenType.ABSTRACT,
                    TokenType.PHRASE,
                    TokenType.RPAREN,
                }
                if prev_token.type not in valid_operand_types or (
                    next_token.type not in valid_operand_types
                    and next_token.type != TokenType.LPAREN
                ):
                    return ValidationResult(is_valid=False, error="Invalid OR operator usage")

            elif token.type == TokenType.NOT:
                # NOT must be followed by a valid operand
                if i == len(tokens) - 1:
                    return ValidationResult(
                        is_valid=False,
                        error="NOT operator must be followed by a term",
                    )
                next_token = tokens[i + 1]
                valid_operand_types = {
                    TokenType.KEYWORD,
                    TokenType.AUTHOR,
                    TokenType.CATEGORY,
                    TokenType.ALL_FIELDS,
                    TokenType.ABSTRACT,
                    TokenType.PHRASE,
                    TokenType.LPAREN,
                }
                if next_token.type not in valid_operand_types:
                    return ValidationResult(
                        is_valid=False,
                        error="NOT operator must be followed by a valid term",
                    )

        return ValidationResult(is_valid=True)

    def _is_valid_category_pattern(self, category: str) -> bool:
        """Check if a category follows valid arXiv category pattern."""
        # For quoted categories, be very permissive and let arXiv handle validation
        if " " in category or '"' in category:
            return True

        # Allow categories like 'cs', 'cs.AI', 'cond-mat.str-el', 'physics.*', etc.
        pattern = r"^[a-zA-Z]+([-.][a-zA-Z*]+)*$"
        return bool(re.match(pattern, category))

    def _is_valid_date_format(self, date_str: str) -> bool:  # noqa: PLR0911
        """Check if date string is in valid format."""
        # JST timezone (UTC+9)
        jst = datetime.timezone(datetime.timedelta(hours=9))

        if len(date_str) == DATE_FORMAT_YYYYMMDD:  # YYYYMMDD
            try:
                datetime.datetime.strptime(date_str, "%Y%m%d").replace(tzinfo=jst)
            except ValueError:
                return False
            else:
                return True
        elif len(date_str) == DATE_FORMAT_YYYYMMDDHHMM:  # YYYYMMDDHHMM
            try:
                datetime.datetime.strptime(date_str, "%Y%m%d%H%M").replace(tzinfo=jst)
            except ValueError:
                return False
            else:
                return True
        elif len(date_str) == DATE_FORMAT_YYYYMMDDHHMMSS:  # YYYYMMDDHHMMSS
            try:
                datetime.datetime.strptime(date_str, "%Y%m%d%H%M%S").replace(tzinfo=jst)
            except ValueError:
                return False
            else:
                return True

        return False

    def _is_malformed_date(self, keyword: str) -> bool:
        """Check if keyword looks like a malformed date operator."""
        # Check for date operator patterns that are malformed
        # e.g., >20240101xy, <20241301abc, >202401011430001, etc.
        date_pattern = r"^[><](\d+[a-zA-Z]+|\d{9,11}|\d{13}|\d{15,})$"
        return bool(re.match(date_pattern, keyword))
