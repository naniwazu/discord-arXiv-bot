"""Simplified single-pass tokenizer for query parser."""

from __future__ import annotations

import re
from typing import ClassVar, NamedTuple

from .constants import SORT_MAPPINGS
from .types import Token, TokenType

# Maximum digits for result count numbers
MAX_RESULT_COUNT_DIGITS = 4


class TokenPattern(NamedTuple):
    """Defines a token pattern with its type."""

    regex: str
    token_type: TokenType
    capture_group: int = 1


class Tokenizer:
    """Simplified single-pass tokenizer with clear pattern priorities."""

    # Patterns defined in priority order (higher priority = earlier in list)
    PATTERNS: ClassVar[list[TokenPattern]] = [
        # Quoted field prefixes (highest priority)
        TokenPattern(r'@"([^"]+)"', TokenType.AUTHOR),
        TokenPattern(r'#"([^"]+)"', TokenType.CATEGORY),
        TokenPattern(r'\*"([^"]+)"', TokenType.ALL_FIELDS),
        TokenPattern(r'\$"([^"]+)"', TokenType.ABSTRACT),
        # Regular quotes (high priority)
        TokenPattern(r'"([^"]+)"', TokenType.PHRASE),
        # Date patterns (before other operators) - exact length only, strict boundaries
        TokenPattern(r">(\d{8}|\d{12}|\d{14})(?!\w)", TokenType.DATE_GT),  # Strict boundaries
        TokenPattern(r"<(\d{8}|\d{12}|\d{14})(?!\w)(?!\S)", TokenType.DATE_LT),  # Strict boundaries
        # Field prefixes (without quotes)
        TokenPattern(r"@(\S+)", TokenType.AUTHOR),
        TokenPattern(r"#(\S+)", TokenType.CATEGORY),
        TokenPattern(r"\*(\S+)", TokenType.ALL_FIELDS),
        TokenPattern(r"\$(\S+)", TokenType.ABSTRACT),
        # Operators and parentheses (must come before word patterns)
        TokenPattern(r"\|", TokenType.OR, 0),
        TokenPattern(r"-", TokenType.NOT, 0),
        TokenPattern(r"\(", TokenType.LPAREN, 0),
        TokenPattern(r"\)", TokenType.RPAREN, 0),
        # Words (lowest priority - catch all remaining non-operator characters)
        TokenPattern(r"[^\s\|\-\(\)]+", None, 1),  # Exclude operators from word pattern
    ]

    def __init__(self) -> None:
        """Compile regex patterns for efficiency."""
        self.compiled_patterns = [
            (re.compile(pattern.regex), pattern.token_type, pattern.capture_group)
            for pattern in self.PATTERNS
        ]

    def tokenize(self, query: str) -> list[Token]:
        """Tokenize query string in a single pass with clear priority."""
        tokens = []
        pos = 0

        while pos < len(query):
            # Skip whitespace
            if query[pos].isspace():
                pos += 1
                continue

            # Try each pattern in priority order
            matched = False
            for regex, pattern_token_type, capture_group in self.compiled_patterns:
                match = regex.match(query, pos)
                if match:
                    # Extract value from appropriate capture group
                    if capture_group == 0 or match.lastindex is None:
                        value = match.group(0)  # Entire match
                    else:
                        value = match.group(capture_group)  # Specific group

                    # Special handling for word classification
                    if pattern_token_type is None:
                        classified_type = self._classify_word(value)
                        # Convert sort tokens to lowercase for consistency
                        if classified_type == TokenType.SORT:
                            value = value.lower()
                        final_token_type = classified_type
                    else:
                        final_token_type = pattern_token_type

                    tokens.append(Token(final_token_type, value, pos))
                    pos = match.end()
                    matched = True
                    break

            if not matched:
                # Skip unexpected character and continue
                pos += 1

        return tokens

    def _classify_word(self, word: str) -> TokenType:
        """Classify a word as NUMBER, SORT, or KEYWORD."""
        # Check if it's a number (all digits are treated as potential result counts)
        if word.isdigit():
            return TokenType.NUMBER
        # Check if it's a sort specifier (case insensitive)
        if word.lower() in SORT_MAPPINGS:
            return TokenType.SORT
        # Otherwise it's a keyword
        return TokenType.KEYWORD
