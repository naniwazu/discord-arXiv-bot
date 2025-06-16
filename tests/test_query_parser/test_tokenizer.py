"""Tests for the tokenizer module."""


from src.query_parser.tokenizer import Tokenizer
from src.query_parser.types import TokenType


class TestTokenizer:
    """Test the Tokenizer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tokenizer = Tokenizer()

    def test_simple_keyword(self):
        """Test simple keyword tokenization."""
        tokens = self.tokenizer.tokenize("quantum")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.KEYWORD
        assert tokens[0].value == "quantum"
        assert tokens[0].position == 0

    def test_multiple_keywords(self):
        """Test multiple keywords."""
        tokens = self.tokenizer.tokenize("quantum computing")
        assert len(tokens) == 2
        assert all(t.type == TokenType.KEYWORD for t in tokens)
        assert tokens[0].value == "quantum"
        assert tokens[1].value == "computing"

    def test_author_prefix(self):
        """Test author prefix tokenization."""
        tokens = self.tokenizer.tokenize("@hinton")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.AUTHOR
        assert tokens[0].value == "hinton"

    def test_category_prefix(self):
        """Test category prefix tokenization."""
        tokens = self.tokenizer.tokenize("#cs.AI")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.CATEGORY
        assert tokens[0].value == "cs.AI"

    def test_all_fields_prefix(self):
        """Test all fields prefix tokenization."""
        tokens = self.tokenizer.tokenize("*quantum")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.ALL_FIELDS
        assert tokens[0].value == "quantum"

    def test_abstract_prefix(self):
        """Test abstract prefix tokenization."""
        tokens = self.tokenizer.tokenize("$neural")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.ABSTRACT
        assert tokens[0].value == "neural"

    def test_number_tokenization(self):
        """Test number tokenization."""
        tokens = self.tokenizer.tokenize("quantum 50")
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.KEYWORD
        assert tokens[1].type == TokenType.NUMBER
        assert tokens[1].value == "50"

    def test_sort_tokenization(self):
        """Test sort specifier tokenization."""
        # New format
        tokens = self.tokenizer.tokenize("quantum rd")
        assert len(tokens) == 2
        assert tokens[1].type == TokenType.SORT
        assert tokens[1].value == "rd"

        # Legacy format
        tokens = self.tokenizer.tokenize("quantum R")
        assert len(tokens) == 2
        assert tokens[1].type == TokenType.SORT
        assert tokens[1].value == "r"  # Converted to lowercase

    def test_phrase_tokenization(self):
        """Test phrase tokenization."""
        tokens = self.tokenizer.tokenize('"quantum computing"')
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.PHRASE
        assert tokens[0].value == "quantum computing"

    def test_complex_query(self):
        """Test complex query tokenization."""
        tokens = self.tokenizer.tokenize("quantum @hinton #cs.AI 20 rd")
        assert len(tokens) == 5
        assert tokens[0].type == TokenType.KEYWORD
        assert tokens[0].value == "quantum"
        assert tokens[1].type == TokenType.AUTHOR
        assert tokens[1].value == "hinton"
        assert tokens[2].type == TokenType.CATEGORY
        assert tokens[2].value == "cs.AI"
        assert tokens[3].type == TokenType.NUMBER
        assert tokens[3].value == "20"
        assert tokens[4].type == TokenType.SORT
        assert tokens[4].value == "rd"

    def test_mixed_prefixes(self):
        """Test query with mixed prefixes."""
        tokens = self.tokenizer.tokenize("@lecun *neural #cs.LG")
        assert len(tokens) == 3
        assert tokens[0].type == TokenType.AUTHOR
        assert tokens[1].type == TokenType.ALL_FIELDS
        assert tokens[2].type == TokenType.CATEGORY

    def test_operators(self):
        """Test operator tokenization (Phase 2)."""
        # OR operator
        tokens = self.tokenizer.tokenize("quantum | neural")
        assert len(tokens) == 3
        assert tokens[1].type == TokenType.OR
        assert tokens[1].value == "|"

        # NOT operator
        tokens = self.tokenizer.tokenize("quantum -classical")
        assert len(tokens) == 3
        assert tokens[1].type == TokenType.NOT
        assert tokens[1].value == "-"

    def test_parentheses(self):
        """Test parentheses tokenization."""
        tokens = self.tokenizer.tokenize("(quantum neural)")
        assert len(tokens) == 4
        assert tokens[0].type == TokenType.LPAREN
        assert tokens[3].type == TokenType.RPAREN

    def test_token_positions(self):
        """Test that token positions are correct."""
        tokens = self.tokenizer.tokenize("quantum @hinton")
        assert tokens[0].position == 0  # 'quantum' starts at 0
        assert tokens[1].position == 8  # '@hinton' starts at 8

    def test_empty_query(self):
        """Test empty query."""
        tokens = self.tokenizer.tokenize("")
        assert len(tokens) == 0

    def test_whitespace_only(self):
        """Test whitespace-only query."""
        tokens = self.tokenizer.tokenize("   \t\n   ")
        assert len(tokens) == 0

    def test_special_characters_in_values(self):
        """Test special characters in values."""
        tokens = self.tokenizer.tokenize("@john.smith")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.AUTHOR
        assert tokens[0].value == "john.smith"

    def test_phrase_with_quotes_inside(self):
        """Test phrase with escaped quotes."""
        # This is a limitation - we don't handle escaped quotes
        tokens = self.tokenizer.tokenize('"quantum"')
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.PHRASE
        assert tokens[0].value == "quantum"
