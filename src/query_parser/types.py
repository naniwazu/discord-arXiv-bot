"""Type definitions for query parser."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Optional

import arxiv


class TokenType(Enum):
    """Token types for query parsing."""

    KEYWORD = auto()
    AUTHOR = auto()
    CATEGORY = auto()
    ALL_FIELDS = auto()
    ABSTRACT = auto()
    NUMBER = auto()
    SORT = auto()
    OR = auto()
    NOT = auto()
    LPAREN = auto()
    RPAREN = auto()
    PHRASE = auto()
    UNKNOWN = auto()


@dataclass
class Token:
    """Represents a single token in the query."""

    type: TokenType
    value: str
    position: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, '{self.value}', pos={self.position})"


@dataclass
class ParseResult:
    """Result of query parsing."""

    success: bool
    search: arxiv.Search | None = None
    error: str | None = None
    debug_info: dict[str, Any] | None = None

    @property
    def query_string(self) -> str | None:
        """Get the arxiv query string if successful."""
        return self.search.query if self.success and self.search else None


@dataclass
class ValidationResult:
    """Result of token validation."""

    is_valid: bool
    error: str | None = None
