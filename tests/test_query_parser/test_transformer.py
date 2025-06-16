"""Tests for the transformer module."""

import pytest

from src.query_parser.transformer import QueryTransformer
from src.query_parser.types import Token, TokenType


class TestQueryTransformer:
    """Test the QueryTransformer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = QueryTransformer()

    def test_simple_keyword_transform(self):
        """Test simple keyword transformation."""
        tokens = [Token(TokenType.KEYWORD, "quantum", 0)]
        search = self.transformer.transform(tokens)
        assert search.query == "ti:quantum"

    def test_multiple_keywords_transform(self):
        """Test multiple keywords are ANDed."""
        tokens = [
            Token(TokenType.KEYWORD, "quantum", 0),
            Token(TokenType.KEYWORD, "computing", 8),
        ]
        search = self.transformer.transform(tokens)
        assert search.query == "ti:quantum AND ti:computing"

    def test_author_transform(self):
        """Test author prefix transformation."""
        tokens = [Token(TokenType.AUTHOR, "hinton", 1)]
        search = self.transformer.transform(tokens)
        assert search.query == "au:hinton"

    def test_category_transform(self):
        """Test category transformation."""
        tokens = [Token(TokenType.CATEGORY, "cs.AI", 1)]
        search = self.transformer.transform(tokens)
        assert search.query == "cat:cs.AI"

    def test_category_shortcut_transform(self):
        """Test category shortcut expansion."""
        tokens = [Token(TokenType.CATEGORY, "cs", 1)]
        search = self.transformer.transform(tokens)
        assert search.query == "cat:cs.*"

    def test_category_case_correction(self):
        """Test category case correction."""
        tokens = [Token(TokenType.CATEGORY, "cs.ai", 1)]
        search = self.transformer.transform(tokens)
        assert search.query == "cat:cs.AI"

    def test_all_fields_transform(self):
        """Test all fields transformation."""
        tokens = [Token(TokenType.ALL_FIELDS, "quantum", 1)]
        search = self.transformer.transform(tokens)
        assert search.query == "all:quantum"

    def test_abstract_transform(self):
        """Test abstract transformation."""
        tokens = [Token(TokenType.ABSTRACT, "neural", 1)]
        search = self.transformer.transform(tokens)
        assert search.query == "abs:neural"

    def test_phrase_transform(self):
        """Test phrase transformation."""
        tokens = [Token(TokenType.PHRASE, "quantum computing", 1)]
        search = self.transformer.transform(tokens)
        assert search.query == 'ti:"quantum computing"'

    def test_number_transform(self):
        """Test number affects max_results."""
        tokens = [
            Token(TokenType.KEYWORD, "quantum", 0),
            Token(TokenType.NUMBER, "50", 8),
        ]
        search = self.transformer.transform(tokens)
        assert search.max_results == 50
        assert search.query == "ti:quantum"

    def test_sort_transform(self):
        """Test sort specification."""
        # New format - relevance descending
        tokens = [
            Token(TokenType.KEYWORD, "quantum", 0),
            Token(TokenType.SORT, "rd", 8),
        ]
        search = self.transformer.transform(tokens)
        assert search.sort_by.name == "Relevance"
        assert search.sort_order.name == "Descending"

        # Submitted date ascending
        tokens = [
            Token(TokenType.KEYWORD, "quantum", 0),
            Token(TokenType.SORT, "sa", 8),
        ]
        search = self.transformer.transform(tokens)
        assert search.sort_by.name == "SubmittedDate"
        assert search.sort_order.name == "Ascending"

    def test_default_values(self):
        """Test default values are applied."""
        tokens = [Token(TokenType.KEYWORD, "quantum", 0)]
        search = self.transformer.transform(tokens)
        assert search.max_results == 10  # Default
        assert search.sort_by.name == "SubmittedDate"  # Default
        assert search.sort_order.name == "Descending"  # Default

    def test_complex_transform(self):
        """Test complex query transformation."""
        tokens = [
            Token(TokenType.KEYWORD, "quantum", 0),
            Token(TokenType.AUTHOR, "hinton", 8),
            Token(TokenType.CATEGORY, "cs.AI", 16),
            Token(TokenType.NUMBER, "20", 23),
            Token(TokenType.SORT, "rd", 26),
        ]
        search = self.transformer.transform(tokens)
        assert "ti:quantum" in search.query
        assert "au:hinton" in search.query
        assert "cat:cs.AI" in search.query
        assert search.max_results == 20
        assert search.sort_by.name == "Relevance"

    def test_mixed_fields_transform(self):
        """Test mixed field types."""
        tokens = [
            Token(TokenType.AUTHOR, "lecun", 1),
            Token(TokenType.ALL_FIELDS, "neural", 8),
            Token(TokenType.CATEGORY, "cs.LG", 16),
        ]
        search = self.transformer.transform(tokens)
        assert search.query == "au:lecun AND all:neural AND cat:cs.LG"

    def test_empty_tokens(self):
        """Test empty token list."""
        tokens = []
        search = self.transformer.transform(tokens)
        assert search.query == ""
        assert search.max_results == 10

    def test_operators_ignored_phase1(self):
        """Test that operators are ignored in Phase 1."""
        tokens = [
            Token(TokenType.KEYWORD, "quantum", 0),
            Token(TokenType.OR, "|", 8),
            Token(TokenType.KEYWORD, "neural", 10),
        ]
        search = self.transformer.transform(tokens)
        # OR is ignored, keywords are ANDed
        assert search.query == "ti:quantum AND ti:neural"

    def test_parentheses_ignored_phase1(self):
        """Test that parentheses are ignored in Phase 1."""
        tokens = [
            Token(TokenType.LPAREN, "(", 0),
            Token(TokenType.KEYWORD, "quantum", 1),
            Token(TokenType.RPAREN, ")", 8),
        ]
        search = self.transformer.transform(tokens)
        assert search.query == "ti:quantum"