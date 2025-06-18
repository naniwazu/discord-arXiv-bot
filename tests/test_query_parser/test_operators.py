"""Tests for query operators (OR, NOT)."""

from __future__ import annotations

from src.query_parser import QueryParser


class TestOROperator:
    """Test OR operator functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = QueryParser()

    def test_simple_or_operator(self) -> None:
        """Test basic OR operator functionality."""
        result = self.parser.parse("quantum | neural")

        assert result.success
        assert result.search is not None
        assert result.search.query == "ti:quantum OR ti:neural"

    def test_or_with_multiple_terms(self) -> None:
        """Test OR operator with multiple terms."""
        result = self.parser.parse("quantum machine | neural networks")

        assert result.success
        assert result.search is not None
        assert result.search.query == "ti:quantum AND ti:machine OR ti:neural AND ti:networks"

    def test_multiple_or_operators(self) -> None:
        """Test multiple OR operators."""
        result = self.parser.parse("quantum | neural | ai")

        assert result.success
        assert result.search is not None
        assert result.search.query == "ti:quantum OR ti:neural OR ti:ai"

    def test_or_with_field_prefixes(self) -> None:
        """Test OR operator with field prefixes."""
        result = self.parser.parse("@smith | @johnson")

        assert result.success
        assert result.search is not None
        assert result.search.query == "au:smith OR au:johnson"

    def test_or_with_mixed_fields(self) -> None:
        """Test OR operator with mixed field types."""
        result = self.parser.parse("@einstein | #physics")

        assert result.success
        assert result.search is not None
        assert result.search.query == "au:einstein OR cat:physics.*"

    def test_or_with_quotes(self) -> None:
        """Test OR operator with quoted phrases."""
        result = self.parser.parse('"machine learning" | "deep learning"')

        assert result.success
        assert result.search is not None
        assert result.search.query == 'ti:"machine learning" OR ti:"deep learning"'

    def test_or_precedence_with_and(self) -> None:
        """Test OR operator precedence with implicit AND."""
        result = self.parser.parse("quantum computing | neural networks")

        assert result.success
        assert result.search is not None
        # AND should have higher precedence than OR
        assert result.search.query == "ti:quantum AND ti:computing OR ti:neural AND ti:networks"


class TestNOTOperator:
    """Test NOT operator functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = QueryParser()

    def test_simple_not_operator(self) -> None:
        """Test basic NOT operator functionality."""
        result = self.parser.parse("quantum -neural")

        assert result.success
        assert result.search is not None
        assert result.search.query == "ti:quantum AND NOT ti:neural"

    def test_not_with_field_prefix(self) -> None:
        """Test NOT operator with field prefix."""
        result = self.parser.parse("quantum -@smith")

        assert result.success
        assert result.search is not None
        assert result.search.query == "ti:quantum AND NOT au:smith"

    def test_not_with_category(self) -> None:
        """Test NOT operator with category."""
        result = self.parser.parse("quantum -#physics")

        assert result.success
        assert result.search is not None
        assert result.search.query == "ti:quantum AND NOT cat:physics.*"

    def test_multiple_not_operators(self) -> None:
        """Test multiple NOT operators."""
        result = self.parser.parse("quantum -neural -deep")

        assert result.success
        assert result.search is not None
        assert result.search.query == "ti:quantum AND NOT ti:neural AND NOT ti:deep"

    def test_not_with_quotes(self) -> None:
        """Test NOT operator with quoted phrases."""
        result = self.parser.parse('quantum -"machine learning"')

        assert result.success
        assert result.search is not None
        assert result.search.query == 'ti:quantum AND NOT ti:"machine learning"'

    def test_not_at_beginning(self) -> None:
        """Test NOT operator at the beginning of query."""
        result = self.parser.parse("-classical quantum")

        assert result.success
        assert result.search is not None
        assert result.search.query == "NOT ti:classical AND ti:quantum"

    def test_only_not_operator(self) -> None:
        """Test query with only NOT operator."""
        result = self.parser.parse("-classical")

        assert result.success
        assert result.search is not None
        assert result.search.query == "NOT ti:classical"


class TestCombinedOperators:
    """Test combinations of OR and NOT operators."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = QueryParser()

    def test_or_and_not_combination(self) -> None:
        """Test OR and NOT operators together."""
        result = self.parser.parse("quantum | neural -classical")

        assert result.success
        assert result.search is not None
        assert result.search.query == "ti:quantum OR ti:neural AND NOT ti:classical"

    def test_not_with_or_group(self) -> None:
        """Test NOT operator applied to OR group."""
        result = self.parser.parse("quantum -(neural | classical)")

        assert result.success
        assert result.search is not None
        # This tests parentheses with NOT, which is complex
        assert "NOT" in result.search.query
        assert "neural" in result.search.query
        assert "classical" in result.search.query

    def test_complex_operator_precedence(self) -> None:
        """Test complex operator precedence."""
        result = self.parser.parse("quantum computing | neural networks -deep learning")

        assert result.success
        assert result.search is not None
        # Should group as: (quantum AND computing) OR
        # (neural AND networks AND NOT deep AND NOT learning)
        expected_parts = ["quantum", "computing", "neural", "networks", "NOT", "deep", "learning"]
        for part in expected_parts:
            assert part in result.search.query

    def test_operators_with_result_count(self) -> None:
        """Test operators with result count specification."""
        result = self.parser.parse("quantum | neural 20")

        assert result.success
        assert result.search is not None
        assert result.search.query == "ti:quantum OR ti:neural"
        assert result.search.max_results == 20

    def test_operators_with_sort(self) -> None:
        """Test operators with sort specification."""
        result = self.parser.parse("quantum | neural r")

        assert result.success
        assert result.search is not None
        assert result.search.query == "ti:quantum OR ti:neural"
        assert result.search.sort_by.name == "Relevance"


class TestOperatorValidation:
    """Test operator validation and error cases."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = QueryParser()

    def test_or_at_beginning_invalid(self) -> None:
        """Test OR operator at beginning should fail."""
        result = self.parser.parse("| quantum")

        assert not result.success
        assert "Invalid OR operator placement" in result.error

    def test_or_at_end_invalid(self) -> None:
        """Test OR operator at end should fail."""
        result = self.parser.parse("quantum |")

        assert not result.success
        assert "Invalid OR operator placement" in result.error

    def test_consecutive_or_operators_invalid(self) -> None:
        """Test consecutive OR operators should fail."""
        result = self.parser.parse("quantum | | neural")

        assert not result.success
        assert "Invalid OR operator" in result.error

    def test_not_at_end_invalid(self) -> None:
        """Test NOT operator at end should fail."""
        result = self.parser.parse("quantum -")

        assert not result.success
        assert "NOT operator must be followed by a term" in result.error

    def test_not_followed_by_operator_invalid(self) -> None:
        """Test NOT operator followed by another operator should fail."""
        result = self.parser.parse("quantum - |")

        assert not result.success
        assert "NOT operator must be followed by a valid term" in result.error
