"""Tests for the validator module."""


from src.query_parser.types import Token, TokenType
from src.query_parser.validator import QueryValidator


class TestQueryValidator:
    """Test the QueryValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = QueryValidator()

    def test_valid_simple_query(self):
        """Test validation of simple valid query."""
        tokens = [Token(TokenType.KEYWORD, "quantum", 0)]
        result = self.validator.validate(tokens)
        assert result.is_valid
        assert result.error is None

    def test_empty_query(self):
        """Test empty query is invalid."""
        tokens = []
        result = self.validator.validate(tokens)
        assert not result.is_valid
        assert result.error == "Empty query"

    def test_valid_number_range(self):
        """Test valid number range."""
        tokens = [
            Token(TokenType.KEYWORD, "quantum", 0),
            Token(TokenType.NUMBER, "50", 8),
        ]
        result = self.validator.validate(tokens)
        assert result.is_valid

    def test_number_too_small(self):
        """Test number below minimum."""
        tokens = [Token(TokenType.NUMBER, "0", 0)]
        result = self.validator.validate(tokens)
        assert not result.is_valid
        assert "must be between 1-1000" in result.error

    def test_number_too_large(self):
        """Test number above maximum."""
        tokens = [Token(TokenType.NUMBER, "5000", 0)]
        result = self.validator.validate(tokens)
        assert not result.is_valid
        assert "must be between 1-1000" in result.error

    def test_invalid_number_format(self):
        """Test non-numeric number token."""
        tokens = [Token(TokenType.NUMBER, "abc", 0)]
        result = self.validator.validate(tokens)
        assert not result.is_valid
        assert "Invalid number" in result.error

    def test_valid_category(self):
        """Test valid category."""
        tokens = [Token(TokenType.CATEGORY, "cs.AI", 0)]
        result = self.validator.validate(tokens)
        assert result.is_valid

    def test_valid_category_shortcut(self):
        """Test valid category shortcut."""
        tokens = [Token(TokenType.CATEGORY, "cs", 0)]
        result = self.validator.validate(tokens)
        assert result.is_valid

    def test_valid_category_lowercase(self):
        """Test valid category with lowercase."""
        tokens = [Token(TokenType.CATEGORY, "cs.ai", 0)]
        result = self.validator.validate(tokens)
        assert result.is_valid

    def test_invalid_category(self):
        """Test invalid category (now passes through to arXiv API)."""
        tokens = [Token(TokenType.CATEGORY, "invalid.xyz", 0)]
        result = self.validator.validate(tokens)
        assert result.is_valid  # Invalid categories now pass through

    def test_balanced_parentheses(self):
        """Test balanced parentheses."""
        tokens = [
            Token(TokenType.LPAREN, "(", 0),
            Token(TokenType.KEYWORD, "quantum", 1),
            Token(TokenType.RPAREN, ")", 8),
        ]
        result = self.validator.validate(tokens)
        assert result.is_valid

    def test_unbalanced_parentheses_missing_close(self):
        """Test unbalanced parentheses - missing close."""
        tokens = [
            Token(TokenType.LPAREN, "(", 0),
            Token(TokenType.KEYWORD, "quantum", 1),
        ]
        result = self.validator.validate(tokens)
        assert not result.is_valid
        assert "Unbalanced parentheses" in result.error

    def test_unbalanced_parentheses_missing_open(self):
        """Test unbalanced parentheses - missing open."""
        tokens = [
            Token(TokenType.KEYWORD, "quantum", 0),
            Token(TokenType.RPAREN, ")", 8),
        ]
        result = self.validator.validate(tokens)
        assert not result.is_valid
        assert "Unbalanced parentheses" in result.error

    def test_valid_or_operator(self):
        """Test valid OR operator usage."""
        tokens = [
            Token(TokenType.KEYWORD, "quantum", 0),
            Token(TokenType.OR, "|", 8),
            Token(TokenType.KEYWORD, "neural", 10),
        ]
        result = self.validator.validate(tokens)
        assert result.is_valid

    def test_or_operator_at_start(self):
        """Test OR operator at start (Phase 1: not validated)."""
        tokens = [
            Token(TokenType.OR, "|", 0),
            Token(TokenType.KEYWORD, "quantum", 2),
        ]
        result = self.validator.validate(tokens)
        assert result.is_valid  # OR validation removed in Phase 1

    def test_or_operator_at_end(self):
        """Test OR operator at end (Phase 1: not validated)."""
        tokens = [
            Token(TokenType.KEYWORD, "quantum", 0),
            Token(TokenType.OR, "|", 8),
        ]
        result = self.validator.validate(tokens)
        assert result.is_valid  # OR validation removed in Phase 1

    def test_or_between_valid_operands(self):
        """Test OR between various valid operands."""
        # Between author tokens
        tokens = [
            Token(TokenType.AUTHOR, "hinton", 0),
            Token(TokenType.OR, "|", 8),
            Token(TokenType.AUTHOR, "lecun", 10),
        ]
        result = self.validator.validate(tokens)
        assert result.is_valid

        # Between category and keyword
        tokens = [
            Token(TokenType.CATEGORY, "cs.AI", 0),
            Token(TokenType.OR, "|", 6),
            Token(TokenType.KEYWORD, "neural", 8),
        ]
        result = self.validator.validate(tokens)
        assert result.is_valid

    def test_or_with_parentheses(self):
        """Test OR with unbalanced parentheses."""
        tokens = [
            Token(TokenType.RPAREN, ")", 0),
            Token(TokenType.OR, "|", 2),
            Token(TokenType.LPAREN, "(", 4),
        ]
        result = self.validator.validate(tokens)
        assert not result.is_valid  # ) OR ( is unbalanced
        assert "Unbalanced parentheses" in result.error

    def test_complex_valid_query(self):
        """Test complex valid query."""
        tokens = [
            Token(TokenType.LPAREN, "(", 0),
            Token(TokenType.KEYWORD, "quantum", 1),
            Token(TokenType.OR, "|", 9),
            Token(TokenType.KEYWORD, "neural", 11),
            Token(TokenType.RPAREN, ")", 17),
            Token(TokenType.AUTHOR, "hinton", 19),
            Token(TokenType.CATEGORY, "cs.AI", 27),
            Token(TokenType.NUMBER, "50", 34),
            Token(TokenType.SORT, "rd", 37),
        ]
        result = self.validator.validate(tokens)
        assert result.is_valid

    def test_nested_parentheses(self):
        """Test nested parentheses."""
        tokens = [
            Token(TokenType.LPAREN, "(", 0),
            Token(TokenType.LPAREN, "(", 1),
            Token(TokenType.KEYWORD, "quantum", 2),
            Token(TokenType.RPAREN, ")", 9),
            Token(TokenType.RPAREN, ")", 10),
        ]
        result = self.validator.validate(tokens)
        assert result.is_valid

    def test_multiple_numbers(self):
        """Test multiple numbers - only last one should be used."""
        tokens = [
            Token(TokenType.NUMBER, "20", 0),
            Token(TokenType.NUMBER, "50", 3),
        ]
        result = self.validator.validate(tokens)
        assert result.is_valid  # Both numbers are valid individually
