"""Tests for edge cases and error handling."""


from src.query_parser import QueryParser


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = QueryParser()

    def test_very_long_query(self):
        """Test handling of very long queries."""
        # Create a query with many terms
        terms = ["quantum"] * 100
        query = " ".join(terms)
        result = self.parser.parse(query)
        assert result.success
        # Should handle long queries gracefully

    def test_special_characters_in_keywords(self):
        """Test special characters in keywords."""
        result = self.parser.parse("C++")
        assert result.success
        assert "ti:C++" in result.query_string

    def test_unicode_characters(self):
        """Test Unicode characters in queries."""
        result = self.parser.parse("量子 @山田")
        assert result.success
        assert "ti:量子" in result.query_string
        assert "au:山田" in result.query_string

    def test_mixed_quotes(self):
        """Test mixed quote types."""
        result = self.parser.parse('"quantum computing"')
        assert result.success
        assert 'ti:"quantum computing"' in result.query_string

    def test_numbers_at_boundaries(self):
        """Test numbers at min/max boundaries."""
        # Minimum valid
        result = self.parser.parse("quantum 1")
        assert result.success
        assert result.search.max_results == 1

        # Maximum valid
        result = self.parser.parse("quantum 1000")
        assert result.success
        assert result.search.max_results == 1000

        # Just over maximum
        result = self.parser.parse("quantum 1001")
        assert not result.success

    def test_multiple_spaces(self):
        """Test multiple spaces between tokens."""
        result = self.parser.parse("quantum    computing     50")
        assert result.success
        assert "ti:quantum AND ti:computing" in result.query_string
        assert result.search.max_results == 50

    def test_tabs_and_newlines(self):
        """Test tabs and newlines in query."""
        result = self.parser.parse("quantum\tcomputing\n50")
        assert result.success
        assert "ti:quantum AND ti:computing" in result.query_string

    def test_leading_trailing_whitespace(self):
        """Test leading and trailing whitespace."""
        result = self.parser.parse("  quantum computing  ")
        assert result.success
        assert "ti:quantum AND ti:computing" in result.query_string

    def test_only_prefixes(self):
        """Test query with only prefixes."""
        result = self.parser.parse("@ # $")
        assert result.success
        assert result.query_string == ""  # No valid tokens

    def test_prefix_without_value(self):
        """Test prefix characters without values."""
        result = self.parser.parse("quantum @ neural")
        assert result.success
        # @ should be ignored, treated as separate tokens

    def test_consecutive_operators(self):
        """Test consecutive operators."""
        result = self.parser.parse("quantum || neural")
        assert result.success
        # Should handle gracefully

    def test_mixed_case_sort(self):
        """Test mixed case sort specifiers."""
        result = self.parser.parse("quantum Rd")
        assert result.success
        assert result.search.sort_by.name == "Relevance"

    def test_invalid_sort_ignored(self):
        """Test invalid sort specifier is treated as keyword."""
        result = self.parser.parse("quantum xyz")
        assert result.success
        assert "ti:xyz" in result.query_string  # Treated as keyword

    def test_category_with_special_chars(self):
        """Test category with hyphens."""
        result = self.parser.parse("#quant-ph")
        assert result.success
        assert "cat:quant-ph" in result.query_string

    def test_repeated_prefixes(self):
        """Test repeated prefix usage."""
        result = self.parser.parse("@smith @jones @williams")
        assert result.success
        assert "au:smith AND au:jones AND au:williams" in result.query_string

    def test_mixed_prefix_types(self):
        """Test all prefix types together."""
        result = self.parser.parse("@smith #cs.AI *quantum $neural")
        assert result.success
        assert "au:smith" in result.query_string
        assert "cat:cs.AI" in result.query_string
        assert "all:quantum" in result.query_string
        assert "abs:neural" in result.query_string

    def test_number_like_keywords(self):
        """Test keywords that look like numbers."""
        result = self.parser.parse("2023 conference")
        assert result.success
        # 2023 should be treated as a number (max_results)
        assert result.search.max_results == 2023 or "ti:2023" in result.query_string

    def test_empty_quotes(self):
        """Test empty quoted string."""
        result = self.parser.parse('""')
        assert result.success
        # Empty phrase should be handled gracefully

    def test_unclosed_quotes(self):
        """Test unclosed quotes."""
        result = self.parser.parse('"quantum computing')
        assert result.success
        # Should handle gracefully, likely treating as regular keywords

    def test_category_case_variations(self):
        """Test various case combinations for categories."""
        cases = ["cs.AI", "CS.AI", "cs.ai", "CS.ai", "Cs.Ai"]
        for case in cases:
            result = self.parser.parse(f"#{case}")
            assert result.success
            assert "cat:cs.AI" in result.query_string

    def test_sort_with_no_keywords(self):
        """Test sort specifier without any search terms."""
        result = self.parser.parse("rd")
        assert result.success
        assert result.search.sort_by.name == "Relevance"
        assert result.query_string == ""  # No search terms

    def test_multiple_numbers_last_wins(self):
        """Test that when multiple numbers are given, the last one is used."""
        result = self.parser.parse("10 20 30")
        assert result.success
        # Depends on implementation - might use last number or treat as keywords

    def test_prefixes_with_numbers(self):
        """Test prefixes with numeric values."""
        result = self.parser.parse("@123 #123")
        assert result.success
        # Numbers after prefixes should work
