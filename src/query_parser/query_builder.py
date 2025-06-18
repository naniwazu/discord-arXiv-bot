"""Query string builder with single responsibility."""

from __future__ import annotations


class QueryStringBuilder:
    """Builds arXiv query strings from components.
    
    Single responsibility: Query string construction only.
    Handles AND/OR precedence and grouping logic.
    """

    def build_and_expression(self, parts: list[str]) -> str:
        """Build AND expression from query parts."""
        if not parts:
            return ""
        return " AND ".join(parts)

    def build_or_expression(self, groups: list[str]) -> str:
        """Build OR expression from query groups."""
        if not groups:
            return ""
        return " OR ".join(groups)

    def build_grouped_expression(self, content: str, field_prefix: str | None = None) -> str:
        """Build grouped expression with optional field prefix."""
        if not content:
            return ""
        
        if field_prefix:
            return f"{field_prefix}({content})"
        return f"({content})"

    def build_negated_expression(self, content: str) -> str:
        """Build NOT expression."""
        if not content:
            return ""
        return f"NOT {content}"

    def split_by_or(self, items: list) -> list[list]:
        """Split items by OR tokens, returning groups."""
        # Import here to avoid circular imports
        from .types import Token, TokenType
        
        groups = []
        current_group = []

        for item in items:
            if isinstance(item, Token) and item.type == TokenType.OR:
                if current_group:
                    groups.append(current_group)
                    current_group = []
            else:
                current_group.append(item)

        if current_group:
            groups.append(current_group)

        return groups if groups else [[]]