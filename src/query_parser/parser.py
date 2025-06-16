"""Main query parser implementation."""

from __future__ import annotations

from typing import Any

import arxiv

from .tokenizer import Tokenizer
from .transformer import QueryTransformer
from .types import ParseResult, Token
from .validator import QueryValidator


class QueryParser:
    """Main parser that coordinates tokenization, validation, and transformation."""

    def __init__(self, timezone_offset: int = -9, *, debug: bool = False) -> None:
        """Initialize parser with components.
        
        Args:
            timezone_offset: Timezone offset in hours (default: -9 for JST)
            debug: Whether to include debug information in results

        """
        self.tokenizer = Tokenizer()
        self.transformer = QueryTransformer(timezone_offset)
        self.validator = QueryValidator()
        self.debug = debug

    def parse(self, query: str) -> ParseResult:
        """Parse a query string into an arXiv Search object.
        
        Args:
            query: The query string to parse
            
        Returns:
            ParseResult containing the search object or error information

        """
        try:
            # Tokenize
            tokens = self.tokenizer.tokenize(query)

            # Validate
            validation_result = self.validator.validate(tokens)
            if not validation_result.is_valid:
                return ParseResult(
                    success=False,
                    error=validation_result.error,
                    debug_info=self._get_debug_info(query, tokens) if self.debug else None,
                )

            # Transform
            search = self.transformer.transform(tokens)

            # Create result
            return ParseResult(
                success=True,
                search=search,
                debug_info=self._get_debug_info(query, tokens, search) if self.debug else None,
            )

        except Exception as e:
            return ParseResult(
                success=False,
                error=f"Parse error: {e!s}",
                debug_info={"exception": str(e), "query": query} if self.debug else None,
            )

    def _get_debug_info(
        self,
        query: str,
        tokens: list[Token],
        search: arxiv.Search | None = None,
    ) -> dict[str, Any]:
        """Generate debug information for the parse result."""
        debug_info = {
            "original_query": query,
            "tokens": [
                {
                    "type": token.type.name,
                    "value": token.value,
                    "position": token.position,
                }
                for token in tokens
            ],
        }

        if search:
            debug_info["arxiv_query"] = search.query
            debug_info["max_results"] = search.max_results
            debug_info["sort_by"] = search.sort_by.name
            debug_info["sort_order"] = search.sort_order.name

        return debug_info
