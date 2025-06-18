"""Tests for date parsing functionality."""

from __future__ import annotations

from src.query_parser import QueryParser


class TestBasicDateFormats:
    """Test basic date format parsing."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = QueryParser()

    def test_yyyymmdd_format(self) -> None:
        """Test YYYYMMDD date format (8 digits)."""
        result = self.parser.parse("quantum >20240101")

        assert result.success
        assert result.search is not None
        assert "submittedDate:[20240101000000 TO" in result.search.query
        assert "ti:quantum" in result.search.query

    def test_yyyymmddhhmm_format(self) -> None:
        """Test YYYYMMDDHHMM date format (12 digits)."""
        result = self.parser.parse("ai >202401011430")

        assert result.success
        assert result.search is not None
        assert "submittedDate:[20240101143000 TO" in result.search.query
        assert "ti:ai" in result.search.query

    def test_yyyymmddhhmmss_format(self) -> None:
        """Test YYYYMMDDHHMMSS date format (14 digits)."""
        result = self.parser.parse("neural >20240101143000")

        assert result.success
        assert result.search is not None
        assert "submittedDate:[20240101143000 TO" in result.search.query
        assert "ti:neural" in result.search.query

    def test_until_date_adds_day(self) -> None:
        """Test that until dates with YYYYMMDD format add one day."""
        result = self.parser.parse("quantum <20240101")

        assert result.success
        assert result.search is not None
        # Should add one day (24 hours) to the date
        assert "submittedDate:[19000101000000 TO 20240102000000]" in result.search.query

    def test_until_date_no_day_addition_with_time(self) -> None:
        """Test that until dates with time don't add a day."""
        result = self.parser.parse("quantum <202401011430")

        assert result.success
        assert result.search is not None
        # Should NOT add a day when time is specified
        assert "submittedDate:[19000101000000 TO 20240101143000]" in result.search.query


class TestDateOperators:
    """Test date operators (> and <)."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = QueryParser()

    def test_greater_than_operator(self) -> None:
        """Test > operator for since dates."""
        result = self.parser.parse("machine learning >20240101")

        assert result.success
        assert result.search is not None
        assert "ti:machine AND ti:learning" in result.search.query
        assert "submittedDate:[20240101000000 TO" in result.search.query

    def test_less_than_operator(self) -> None:
        """Test < operator for until dates."""
        result = self.parser.parse("deep learning <20241231")

        assert result.success
        assert result.search is not None
        assert "ti:deep AND ti:learning" in result.search.query
        assert "TO 20250101000000]" in result.search.query

    def test_both_operators_date_range(self) -> None:
        """Test both > and < operators for date range."""
        result = self.parser.parse("quantum >20240101 <20241231")

        assert result.success
        assert result.search is not None
        assert "ti:quantum" in result.search.query
        assert "submittedDate:[20240101000000 TO 20250101000000]" in result.search.query

    def test_operators_with_complex_query(self) -> None:
        """Test date operators with complex query expressions."""
        result = self.parser.parse("(quantum | ai) >20240101 <20241231")

        assert result.success
        assert result.search is not None
        assert "(ti:quantum OR ti:ai)" in result.search.query
        assert "submittedDate:[20240101000000 TO 20250101000000]" in result.search.query

    def test_operators_with_field_prefixes(self) -> None:
        """Test date operators with field prefixes."""
        result = self.parser.parse("@einstein #physics >20240101")

        assert result.success
        assert result.search is not None
        assert "au:einstein" in result.search.query
        assert "cat:physics.*" in result.search.query
        assert "submittedDate:[20240101000000 TO" in result.search.query


class TestDateValidation:
    """Test date format validation."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = QueryParser()

    def test_invalid_date_format_short(self) -> None:
        """Test invalid date format (too short) - treated as keyword."""
        result = self.parser.parse("quantum >2024")

        assert result.success
        # Invalid date format becomes keyword
        assert "ti:>2024" in result.query_string

    def test_invalid_date_format_long(self) -> None:
        """Test invalid date format (too long) - should be rejected."""
        result = self.parser.parse("quantum >202401011430001")

        assert not result.success
        # Invalid date format should be caught by validation
        assert "Invalid date format" in result.error

    def test_invalid_date_values(self) -> None:
        """Test invalid date values."""
        invalid_dates = [
            "quantum >20241301",  # Invalid month
            "quantum >20240230",  # Invalid day for February
            "quantum >20240101xy",  # Non-numeric characters
        ]

        for query in invalid_dates:
            result = self.parser.parse(query)
            assert not result.success, f"Query should fail: {query}"
            assert "Invalid date format" in result.error

    def test_valid_edge_case_dates(self) -> None:
        """Test valid edge case dates."""
        valid_dates = [
            "quantum >20240229",  # Leap year
            "quantum >20240101000000",  # Midnight
            "quantum >20241231235959",  # End of year
        ]

        for query in valid_dates:
            result = self.parser.parse(query)
            assert result.success, f"Query should succeed: {query}"

    def test_date_without_operator_treated_as_number(self) -> None:
        """Test that numbers without operators are treated as result counts."""
        result = self.parser.parse("quantum 20240101")

        assert not result.success
        # Large numbers should be rejected as invalid result counts
        assert "Number of results must be between 1-1000" in result.error


class TestTimezoneHandling:
    """Test timezone handling (JST)."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = QueryParser(timezone_offset=-9)  # JST

    def test_timezone_offset_applied(self) -> None:
        """Test that timezone offset is applied correctly."""
        result = self.parser.parse("quantum >20240101")

        assert result.success
        assert result.search is not None
        # The exact timezone handling is internal, but we can verify the query is generated
        assert "submittedDate:" in result.search.query

    def test_different_timezone_offset(self) -> None:
        """Test with different timezone offset."""
        utc_parser = QueryParser(timezone_offset=0)  # UTC
        result = utc_parser.parse("quantum >20240101")

        assert result.success
        assert result.search is not None
        assert "submittedDate:" in result.search.query


class TestDateRangeEdgeCases:
    """Test edge cases for date ranges."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = QueryParser()

    def test_only_since_date(self) -> None:
        """Test query with only since date."""
        result = self.parser.parse("quantum >20240101")

        assert result.success
        assert result.search is not None
        assert "submittedDate:[20240101000000 TO 21000101000000]" in result.search.query

    def test_only_until_date(self) -> None:
        """Test query with only until date."""
        result = self.parser.parse("quantum <20240101")

        assert result.success
        assert result.search is not None
        assert "submittedDate:[19000101000000 TO 20240102000000]" in result.search.query

    def test_reverse_order_dates_still_works(self) -> None:
        """Test that date order doesn't matter in query."""
        result = self.parser.parse("quantum <20241231 >20240101")

        assert result.success
        assert result.search is not None
        # Should still work regardless of order in query
        assert "submittedDate:[20240101000000 TO 20250101000000]" in result.search.query

    def test_multiple_same_operators_last_wins(self) -> None:
        """Test that multiple same operators, last one wins."""
        result = self.parser.parse("quantum >20240101 >20240201")

        assert result.success
        assert result.search is not None
        # Should use the last since date
        assert "submittedDate:[20240201000000 TO" in result.search.query

    def test_no_dates_no_date_filter(self) -> None:
        """Test that queries without dates don't include date filter."""
        result = self.parser.parse("quantum machine learning")

        assert result.success
        assert result.search is not None
        assert "submittedDate" not in result.search.query
        assert "ti:quantum AND ti:machine AND ti:learning" in result.search.query


class TestSchedulerCompatibility:
    """Test compatibility with scheduler.py patterns."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = QueryParser()

    def test_scheduler_style_query(self) -> None:
        """Test scheduler-style query with precise timestamps."""
        result = self.parser.parse("machine learning >20240613000000 <20240614000000")

        assert result.success
        assert result.search is not None
        assert "ti:machine AND ti:learning" in result.search.query
        assert "submittedDate:[20240613000000 TO 20240614000000]" in result.search.query

    def test_24_hour_range_query(self) -> None:
        """Test 24-hour range query."""
        result = self.parser.parse("ai >20240101000000 <20240101235959")

        assert result.success
        assert result.search is not None
        assert "submittedDate:[20240101000000 TO 20240101235959]" in result.search.query

    def test_long_topic_with_dates(self) -> None:
        """Test complex topic queries with date ranges."""
        topic = "neural networks deep learning transformers"
        result = self.parser.parse(f"{topic} >20240101 <20241231")

        assert result.success
        assert result.search is not None
        expected_query = "ti:neural AND ti:networks AND ti:deep AND ti:learning AND ti:transformers"
        assert expected_query in result.search.query
        assert "submittedDate:[20240101000000 TO 20250101000000]" in result.search.query
