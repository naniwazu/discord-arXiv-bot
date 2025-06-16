"""Integration tests for the complete query parser system."""


from src.query_parser import QueryParser
from src.query_interface import parse as interface_parse


class TestIntegration:
    """Test integration between components and with query interface."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = QueryParser()

    def test_parser_with_debug_mode(self):
        """Test parser in debug mode provides detailed information."""
        parser = QueryParser(debug=True)
        result = parser.parse("quantum @hinton #cs.AI 20 rd")

        assert result.success
        assert result.debug_info is not None
        assert "original_query" in result.debug_info
        assert "tokens" in result.debug_info
        assert "arxiv_query" in result.debug_info
        assert "max_results" in result.debug_info
        assert "sort_by" in result.debug_info

        # Check token details
        tokens = result.debug_info["tokens"]
        assert len(tokens) == 5
        assert any(t["type"] == "KEYWORD" for t in tokens)
        assert any(t["type"] == "AUTHOR" for t in tokens)

    def test_interface_compatibility_simple(self):
        """Test compatibility with query interface for simple queries."""
        # Compare results with query interface
        interface_result = interface_parse("ti:quantum au:hinton")

        if interface_result:
            # Our parser treats this differently - uses modern syntax
            new_result = self.parser.parse("quantum @hinton")
            assert new_result.success
            # Both should search for quantum in title and hinton as author

    def test_interface_compatibility_categories(self):
        """Test category handling compatibility."""
        interface_result = interface_parse("cat:cs.AI")

        if interface_result:
            new_result = self.parser.parse("#cs.AI")
            assert new_result.success
            assert new_result.query_string == "cat:cs.AI"

    def test_timezone_offset(self):
        """Test timezone offset configuration."""
        # Default JST (-9)
        parser_jst = QueryParser(timezone_offset=-9)
        assert parser_jst.transformer.timezone_offset == -9

        # UTC (0)
        parser_utc = QueryParser(timezone_offset=0)
        assert parser_utc.transformer.timezone_offset == 0

        # EST (-5)
        parser_est = QueryParser(timezone_offset=-5)
        assert parser_est.transformer.timezone_offset == -5

    def test_error_recovery(self):
        """Test error recovery and messages."""
        # Invalid category (now passes through to arXiv API)
        result = self.parser.parse("#invalid.xyz")
        assert result.success
        assert "cat:invalid.xyz" in result.query_string

        # Invalid number
        result = self.parser.parse("quantum 5000")
        assert not result.success
        assert "1-1000" in result.error

        # Empty query
        result = self.parser.parse("")
        assert not result.success
        assert "Empty query" in result.error

    def test_query_interface_integration(self):
        """Test integration through query_interface.py."""
        # query_interface.py should use new parser when available
        result = interface_parse("quantum @hinton #cs.AI 20")

        if result:
            # Should successfully parse with new syntax
            assert result.max_results == 20

    def test_real_world_queries(self):
        """Test real-world query examples."""
        queries = [
            # Simple searches
            "transformer",
            "attention mechanism",
            "bert 50",

            # Author searches
            "@bengio",
            "@yann.lecun",

            # Category searches
            "#cs.LG",
            "#stat.ML",
            "#cs",

            # Combined searches
            "transformer @vaswani #cs.CL",
            "neural @hinton 100 rd",
            '"vision transformer" #cs.CV 50',

            # Multiple authors/categories
            "@hinton @bengio #cs.AI #cs.LG",
        ]

        for query in queries:
            result = self.parser.parse(query)
            assert result.success, f"Failed to parse: {query}"
            assert result.search is not None
            assert result.query_string is not None

    def test_query_string_validation(self):
        """Test that generated query strings are valid."""
        test_cases = [
            ("quantum", "ti:quantum"),
            ("@smith", "au:smith"),
            ("#cs.AI", "cat:cs.AI"),
            ("#cs", "cat:cs.*"),
            ("*neural", "all:neural"),
            ("$abstract", "abs:abstract"),
            ('"exact phrase"', 'ti:"exact phrase"'),
        ]

        for input_query, expected_part in test_cases:
            result = self.parser.parse(input_query)
            assert result.success
            assert expected_part in result.query_string

    def test_combined_features(self):
        """Test combining multiple features."""
        result = self.parser.parse('@hinton "deep learning" #cs.LG 100 rd')

        assert result.success
        assert "au:hinton" in result.query_string
        assert 'ti:"deep learning"' in result.query_string
        assert "cat:cs.LG" in result.query_string
        assert result.search.max_results == 100
        assert result.search.sort_by.name == "Relevance"

    def test_performance_large_query(self):
        """Test performance with large queries."""
        # Create a query with many terms
        terms = []
        for i in range(50):
            terms.append(f"term{i}")
            if i % 5 == 0:
                terms.append(f"@author{i}")
            if i % 7 == 0:
                terms.append("#cs.AI")

        large_query = " ".join(terms)
        result = self.parser.parse(large_query)

        assert result.success
        # Should handle large queries without issues

    def test_unicode_handling(self):
        """Test Unicode character handling throughout the system."""
        queries = [
            "機械学習 @田中",
            "résumé @françois",
            "αβγ @Δημήτρης",
            "🤖 #cs.RO",  # Emoji
        ]

        for query in queries:
            result = self.parser.parse(query)
            assert result.success
            # Should handle Unicode properly

    def test_query_modification_workflow(self):
        """Test modifying queries (simulating user refinement)."""
        # User starts with simple query
        result1 = self.parser.parse("neural networks")
        assert result1.success

        # Adds author
        result2 = self.parser.parse("neural networks @hinton")
        assert result2.success
        assert "au:hinton" in result2.query_string

        # Adds category
        result3 = self.parser.parse("neural networks @hinton #cs.LG")
        assert result3.success
        assert "cat:cs.LG" in result3.query_string

        # Changes count and sort
        result4 = self.parser.parse("neural networks @hinton #cs.LG 50 rd")
        assert result4.success
        assert result4.search.max_results == 50
        assert result4.search.sort_by.name == "Relevance"
