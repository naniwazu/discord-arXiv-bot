"""Tests for parentheses and grouping functionality."""

from __future__ import annotations

from src.query_parser import QueryParser


class TestBasicParentheses:
    """Test basic parentheses functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = QueryParser()

    def test_simple_parentheses(self) -> None:
        """Test simple parentheses grouping."""
        result = self.parser.parse("(quantum neural)")

        assert result.success
        assert result.search is not None
        assert result.search.query == "(ti:quantum AND ti:neural)"

    def test_parentheses_with_single_term(self) -> None:
        """Test parentheses with single term."""
        result = self.parser.parse("(quantum)")

        assert result.success
        assert result.search is not None
        assert result.search.query == "(ti:quantum)"

    def test_parentheses_with_or_operator(self) -> None:
        """Test parentheses with OR operator."""
        result = self.parser.parse("(quantum | neural)")

        assert result.success
        assert result.search is not None
        assert result.search.query == "(ti:quantum OR ti:neural)"

    def test_parentheses_with_not_operator(self) -> None:
        """Test parentheses with NOT operator."""
        result = self.parser.parse("(quantum -neural)")

        assert result.success
        assert result.search is not None
        assert result.search.query == "(ti:quantum AND NOT ti:neural)"

    def test_multiple_parentheses_groups(self) -> None:
        """Test multiple parentheses groups."""
        result = self.parser.parse("(quantum physics) (neural networks)")

        assert result.success
        assert result.search is not None
        assert result.search.query == "(ti:quantum AND ti:physics) AND (ti:neural AND ti:networks)"


class TestNestedParentheses:
    """Test nested parentheses functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = QueryParser()

    def test_nested_parentheses(self) -> None:
        """Test nested parentheses."""
        result = self.parser.parse("((quantum))")

        assert result.success
        assert result.search is not None
        # Should handle nested grouping
        assert "quantum" in result.search.query

    def test_nested_with_operators(self) -> None:
        """Test nested parentheses with operators."""
        result = self.parser.parse("(quantum (neural | ai))")

        assert result.success
        assert result.search is not None
        # Should properly handle nested groups with operators
        assert "quantum" in result.search.query
        assert "neural" in result.search.query
        assert "ai" in result.search.query

    def test_complex_nested_structure(self) -> None:
        """Test complex nested parentheses structure."""
        result = self.parser.parse("((quantum | neural) (deep learning))")

        assert result.success
        assert result.search is not None
        # Should handle complex nested structures
        expected_terms = ["quantum", "neural", "deep", "learning"]
        for term in expected_terms:
            assert term in result.search.query


class TestParenthesesWithFieldPrefixes:
    """Test parentheses with field prefixes."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = QueryParser()

    def test_field_prefix_with_parentheses(self) -> None:
        """Test field prefix with parentheses should be rejected."""
        result = self.parser.parse("@(einstein bohr)")

        assert not result.success
        # Field prefix directly followed by parentheses should cause validation error
        assert "Unbalanced parentheses" in result.error

    def test_category_with_parentheses(self) -> None:
        """Test category prefix with parentheses should be rejected."""
        result = self.parser.parse("#(physics quantum)")

        assert not result.success
        # Category validation should reject malformed pattern
        assert "Invalid category format" in result.error

    def test_abstract_with_parentheses(self) -> None:
        """Test abstract prefix with parentheses should be rejected."""
        result = self.parser.parse("$(machine learning)")

        assert not result.success
        # Field prefix directly followed by parentheses should cause validation error
        assert "Unbalanced parentheses" in result.error

    def test_arxiv_field_with_parentheses(self) -> None:
        """Test arXiv field with parentheses."""
        result = self.parser.parse("ti:(quantum computing)")

        assert result.success
        assert result.search is not None
        # Current implementation treats "ti:" as keyword followed by parentheses group
        assert result.search.query == "ti:ti: AND (ti:quantum AND ti:computing)"

    def test_field_prefix_with_or_in_parentheses(self) -> None:
        """Test field prefix with OR operator in parentheses should be rejected."""
        result = self.parser.parse("@(einstein | bohr)")

        assert not result.success
        # Field prefix directly followed by parentheses should cause validation error
        assert "Unbalanced parentheses" in result.error


class TestParenthesesPrecedence:
    """Test operator precedence with parentheses."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = QueryParser()

    def test_parentheses_override_precedence(self) -> None:
        """Test that parentheses override operator precedence."""
        result = self.parser.parse("quantum (neural | ai) computing")

        assert result.success
        assert result.search is not None
        # Should group the OR operation first due to parentheses
        assert "quantum" in result.search.query
        assert "neural" in result.search.query
        assert "ai" in result.search.query
        assert "computing" in result.search.query

    def test_complex_precedence_with_not(self) -> None:
        """Test complex precedence with NOT operator."""
        result = self.parser.parse("quantum -(neural | classical)")

        assert result.success
        assert result.search is not None
        # NOT should apply to the parentheses group
        assert "quantum" in result.search.query
        assert "NOT" in result.search.query
        assert "neural" in result.search.query
        assert "classical" in result.search.query

    def test_multiple_precedence_levels(self) -> None:
        """Test multiple levels of operator precedence."""
        result = self.parser.parse("(quantum | neural) computing -classical")

        assert result.success
        assert result.search is not None
        # Should properly handle multiple precedence levels
        expected_terms = ["quantum", "neural", "computing", "NOT", "classical"]
        for term in expected_terms:
            assert term in result.search.query


class TestParenthesesWithOtherFeatures:
    """Test parentheses with other query features."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = QueryParser()

    def test_parentheses_with_result_count(self) -> None:
        """Test parentheses with result count."""
        result = self.parser.parse("(quantum | neural) 50")

        assert result.success
        assert result.search is not None
        assert "quantum" in result.search.query
        assert "neural" in result.search.query
        assert result.search.max_results == 50

    def test_parentheses_with_sort(self) -> None:
        """Test parentheses with sort option."""
        result = self.parser.parse("(quantum computing) r")

        assert result.success
        assert result.search is not None
        assert "quantum" in result.search.query
        assert "computing" in result.search.query
        assert result.search.sort_by.name == "Relevance"

    def test_parentheses_with_dates(self) -> None:
        """Test parentheses with date constraints."""
        result = self.parser.parse("(quantum | neural) >20240101")

        assert result.success
        assert result.search is not None
        assert "quantum" in result.search.query
        assert "neural" in result.search.query
        assert "submittedDate:" in result.search.query

    def test_parentheses_with_quotes(self) -> None:
        """Test parentheses with quoted phrases."""
        result = self.parser.parse('(quantum "machine learning")')

        assert result.success
        assert result.search is not None
        assert "quantum" in result.search.query
        assert '"machine learning"' in result.search.query


class TestParenthesesValidation:
    """Test parentheses validation and error cases."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = QueryParser()

    def test_unbalanced_parentheses_left(self) -> None:
        """Test unbalanced parentheses (missing closing)."""
        result = self.parser.parse("(quantum neural")

        assert not result.success
        assert "Unbalanced parentheses" in result.error

    def test_unbalanced_parentheses_right(self) -> None:
        """Test unbalanced parentheses (missing opening)."""
        result = self.parser.parse("quantum neural)")

        assert not result.success
        assert "Unbalanced parentheses" in result.error

    def test_empty_parentheses(self) -> None:
        """Test empty parentheses should fail."""
        result = self.parser.parse("quantum ()")

        assert not result.success
        assert "Empty parentheses" in result.error

    def test_nested_empty_parentheses(self) -> None:
        """Test nested empty parentheses should fail."""
        result = self.parser.parse("quantum (())")

        assert not result.success
        assert "Empty parentheses" in result.error

    def test_multiple_unbalanced_parentheses(self) -> None:
        """Test multiple unbalanced parentheses."""
        result = self.parser.parse("((quantum) neural")

        assert not result.success
        assert "Unbalanced parentheses" in result.error

    def test_parentheses_with_only_operators(self) -> None:
        """Test parentheses containing only operators should fail."""
        result = self.parser.parse("quantum (|)")

        assert not result.success
        # Should fail due to invalid operator or empty content
        assert result.error is not None
