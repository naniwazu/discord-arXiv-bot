"""Tokenizer for query parser."""

from __future__ import annotations

import re

from .constants import SORT_MAPPINGS
from .types import Token, TokenType


class Tokenizer:
    """Tokenizes query strings into structured tokens."""

    def tokenize(self, query: str) -> list[Token]:
        """Tokenize a query string into a list of tokens."""
        tokens = []
        consumed_positions: set[int] = set()

        # Pattern for matching tokens
        patterns = [
            # Phrases (highest priority)
            (r'"([^"]+)"', TokenType.PHRASE, 1, True),  # capture group 1, include quotes

            # Date patterns (high priority, before other < > patterns)
            (r">(\d{8,14})", TokenType.DATE_GT, 1, False),
            (r"<(\d{8,14})(?!\S)", TokenType.DATE_LT, 1, False),  # Don't match <@mentions

            # arXiv-style field specifications (ti:, au:, etc.) without parentheses
            (r"(ti|au|abs|cat|all|co|jr|rn|id):(?!\()", TokenType.ARXIV_FIELD, 1, False),

            # Prefixed tokens
            (r"@(\S+)", TokenType.AUTHOR, 1, False),
            (r"#(\S+)", TokenType.CATEGORY, 1, False),
            (r"\*(\S+)", TokenType.ALL_FIELDS, 1, False),
            (r"\$(\S+)", TokenType.ABSTRACT, 1, False),

            # Operators
            (r"\|", TokenType.OR, 0, False),
            (r"-(?=\S)", TokenType.NOT, 0, False),
            (r"\(", TokenType.LPAREN, 0, False),
            (r"\)", TokenType.RPAREN, 0, False),
        ]

        # First pass: Extract special tokens
        for pattern, token_type, capture_group, _include_match in patterns:
            for match in re.finditer(pattern, query):
                start = match.start()
                end = match.end()

                # Skip if this position is already consumed
                if any(pos in consumed_positions for pos in range(start, end)):
                    continue

                # Mark positions as consumed
                for pos in range(start, end):
                    consumed_positions.add(pos)

                # Extract value
                value = match.group(capture_group) if capture_group > 0 else match.group(0)

                # Add token
                tokens.append(Token(token_type, value, start))

        # Second pass: Extract remaining words (keywords, numbers, sort specs)
        remaining_text = []
        for i, char in enumerate(query):
            if i not in consumed_positions:
                remaining_text.append((char, i))

        # Group consecutive characters into words
        if remaining_text:
            current_word = []
            word_start = None

            for char, pos in remaining_text:
                if char.isspace():
                    if current_word:
                        word = "".join(current_word)
                        self._add_word_token(tokens, word, word_start)
                        current_word = []
                        word_start = None
                else:
                    if not current_word:
                        word_start = pos
                    current_word.append(char)

            # Don't forget the last word
            if current_word:
                word = "".join(current_word)
                self._add_word_token(tokens, word, word_start)

        # Sort tokens by position
        tokens.sort(key=lambda t: t.position)

        return tokens

    def _add_word_token(self, tokens: list[Token], word: str, position: int) -> None:
        """Add a token for a word (keyword, number, or sort spec)."""
        if not word:
            return

        # Check if it's a number
        if word.isdigit():
            tokens.append(Token(TokenType.NUMBER, word, position))
        # Check if it's a sort specifier
        elif word in SORT_MAPPINGS:
            tokens.append(Token(TokenType.SORT, word, position))
        # Otherwise it's a keyword
        else:
            tokens.append(Token(TokenType.KEYWORD, word, position))
