"""Tests for Phase 2 features (operators)."""

import pytest

from src.query_parser import QueryParser


class TestPhase2Features:
    """Test Phase 2 features - operators and advanced sorting."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = QueryParser()

    @pytest.mark.skip(reason="Phase 2 not implemented yet")
    def test_or_operator(self):
        """Test OR operator functionality."""
        result = self.parser.parse("quantum | neural")
        assert result.success
        assert result.query_string == "(ti:quantum OR ti:neural)"

    @pytest.mark.skip(reason="Phase 2 not implemented yet")
    def test_not_operator(self):
        """Test NOT operator functionality."""
        result = self.parser.parse("quantum -classical")
        assert result.success
        assert result.query_string == "ti:quantum NOT ti:classical"

    @pytest.mark.skip(reason="Phase 2 not implemented yet")
    def test_not_with_prefix(self):
        """Test NOT operator with prefixed terms."""
        result = self.parser.parse("quantum -@smith")
        assert result.success
        assert result.query_string == "ti:quantum NOT au:smith"

    @pytest.mark.skip(reason="Phase 2 not implemented yet")
    def test_multiple_or(self):
        """Test multiple OR operators."""
        result = self.parser.parse("bert | gpt | t5")
        assert result.success
        assert result.query_string == "(ti:bert OR ti:gpt OR ti:t5)"

    @pytest.mark.skip(reason="Phase 2 not implemented yet")
    def test_mixed_operators(self):
        """Test mixed AND, OR, NOT operators."""
        result = self.parser.parse("quantum | neural -classical @hinton")
        assert result.success
        # Should be: (ti:quantum OR ti:neural) NOT ti:classical AND au:hinton
        assert "ti:quantum OR ti:neural" in result.query_string
        assert "NOT ti:classical" in result.query_string
        assert "au:hinton" in result.query_string

    @pytest.mark.skip(reason="Phase 2 not implemented yet")
    def test_or_with_different_fields(self):
        """Test OR between different field types."""
        result = self.parser.parse("@hinton | #cs.AI")
        assert result.success
        assert result.query_string == "(au:hinton OR cat:cs.AI)"

    @pytest.mark.skip(reason="Phase 2 not implemented yet")
    def test_ascending_sort(self):
        """Test ascending sort options."""
        # Submitted date ascending
        result = self.parser.parse("quantum sa")
        assert result.success
        assert result.search.sort_by.name == "SubmittedDate"
        assert result.search.sort_order.name == "Ascending"

        # Relevance ascending
        result = self.parser.parse("quantum ra")
        assert result.success
        assert result.search.sort_by.name == "Relevance"
        assert result.search.sort_order.name == "Ascending"

        # Last updated ascending
        result = self.parser.parse("quantum la")
        assert result.success
        assert result.search.sort_by.name == "LastUpdatedDate"
        assert result.search.sort_order.name == "Ascending"

    @pytest.mark.skip(reason="Phase 2 not implemented yet")
    def test_operator_precedence(self):
        """Test operator precedence (NOT > AND > OR)."""
        result = self.parser.parse("quantum | neural -classical deep")
        assert result.success
        # Should parse as: quantum OR (neural NOT classical AND deep)
        # Actual precedence rules TBD

    @pytest.mark.skip(reason="Phase 2 not implemented yet")
    def test_phrase_with_operators(self):
        """Test phrases work with operators."""
        result = self.parser.parse('"quantum computing" | "neural networks"')
        assert result.success
        assert result.query_string == '(ti:"quantum computing" OR ti:"neural networks")'

    @pytest.mark.skip(reason="Phase 2 not implemented yet")
    def test_not_at_start(self):
        """Test NOT operator at the start."""
        result = self.parser.parse("-classical quantum")
        assert result.success
        assert result.query_string == "NOT ti:classical AND ti:quantum"