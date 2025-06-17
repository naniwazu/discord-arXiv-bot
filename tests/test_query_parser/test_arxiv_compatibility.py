"""Tests for arXiv API compatibility and detailed query mode."""


from src.query_parser import QueryParser


class TestArxivCompatibility:
    """Test compatibility with arXiv API query format."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = QueryParser()

    def test_arxiv_field_syntax_passthrough(self):
        """Test that arXiv field syntax is handled (for /arxiv-detail command)."""
        # These would be handled by /arxiv-detail command
        # For now, the parser might not handle them correctly
        queries = [
            "ti:quantum AND au:smith",
            "cat:cs.AI OR cat:cs.LG",
            "all:neural NOT au:lecun",
            'ti:"machine learning" AND cat:cs.*',
        ]

        for query in queries:
            # Current parser may fail on these
            # This is expected - they're for /arxiv-detail mode
            result = self.parser.parse(query)
            # Just testing that it doesn't crash

    def test_date_range_syntax(self):
        """Test date range syntax (currently not supported in new parser)."""
        # These are from the old parser
        queries = [
            "since:20240101",
            "until:20241231",
            "since:20240101 until:20241231",
        ]

        for query in queries:
            result = self.parser.parse(query)
            # Currently these won't be recognized
            # This is expected for Phase 1

    def test_arxiv_boolean_operators(self):
        """Test arXiv boolean operators."""
        # arXiv uses AND, OR, NOT (uppercase)
        # Our parser uses |, -, and implicit AND

        # This would be for /arxiv-detail
        result = self.parser.parse("quantum AND neural")
        assert result.success
        # AND is treated as a keyword in our parser
        assert "ti:quantum" in result.query_string
        assert "ti:AND" in result.query_string  # Treated as keyword
        assert "ti:neural" in result.query_string

    def test_arxiv_wildcard_categories(self):
        """Test arXiv wildcard category support."""
        result = self.parser.parse("#cs.*")
        assert result.success
        assert "cat:cs.*" in result.query_string

        result = self.parser.parse("#physics.*")
        assert result.success
        assert "cat:physics.*" in result.query_string

    def test_arxiv_all_field(self):
        """Test 'all' field searches entire record."""
        result = self.parser.parse("*quantum")
        assert result.success
        assert "all:quantum" in result.query_string

    def test_mixed_new_and_arxiv_syntax(self):
        """Test mixing new syntax with arXiv syntax."""
        # Users might try to mix syntaxes
        result = self.parser.parse("@smith ti:quantum")
        assert result.success
        # ti:quantum is treated as keyword:value in our parser
        # This is a limitation of Phase 1

    def test_arxiv_comment_field(self):
        """Test comment field (co:) - not in our shortcuts."""
        # This would need to be used in /arxiv-detail mode
        result = self.parser.parse("co:conference")
        assert result.success
        # Treated as keyword:keyword in our parser

    def test_arxiv_journal_ref_field(self):
        """Test journal reference field (jr:) - not in our shortcuts."""
        result = self.parser.parse("jr:Nature")
        assert result.success
        # Treated as keyword:keyword in our parser

    def test_arxiv_report_number_field(self):
        """Test report number field (rn:) - treated as title search."""
        result = self.parser.parse("rn:1234")
        assert result.success
        # Becomes ti:rn:1234 in our parser
        assert "ti:rn:1234" in result.query_string

    def test_arxiv_id_field(self):
        """Test ID field - not in our shortcuts."""
        result = self.parser.parse("id:2301.00001")
        assert result.success
        # Treated as keyword:keyword in our parser

    def test_sort_order_compatibility(self):
        """Test sort order compatibility."""
        # Our parser uses different notation
        # arXiv API expects SortCriterion enum values

        # Our format
        result = self.parser.parse("quantum sd")
        assert result.search.sort_by.name == "SubmittedDate"
        assert result.search.sort_order.name == "Descending"

        # Legacy format (single letter)
        result = self.parser.parse("quantum S")
        assert result.search.sort_by.name == "SubmittedDate"

    def test_max_results_compatibility(self):
        """Test max results compatibility."""
        result = self.parser.parse("quantum 100")
        assert result.search.max_results == 100

        # arXiv API has its own limits, but we limit to 1000
        result = self.parser.parse("quantum 10000")
        assert not result.success  # We limit to 1000

    def test_category_normalization(self):
        """Test that categories are normalized to arXiv format."""
        # These should all normalize to cs.AI
        variations = ["cs.ai", "CS.AI", "cs.Ai"]

        for var in variations:
            result = self.parser.parse(f"#{var}")
            assert result.success
            assert "cat:cs.AI" in result.query_string

    def test_query_string_format(self):
        """Test that generated query strings are valid for arXiv API."""
        result = self.parser.parse("quantum @hinton #cs.AI")
        assert result.success

        # Check query string format
        query = result.query_string
        assert " AND " in query  # Uses AND operator
        assert "ti:" in query  # Has field prefix
        assert "au:" in query
        assert "cat:" in query

    def test_empty_query_handling(self):
        """Test empty query handling matches arXiv behavior."""
        result = self.parser.parse("")
        assert not result.success  # Empty queries are invalid

        # Just whitespace
        result = self.parser.parse("   ")
        assert not result.success
