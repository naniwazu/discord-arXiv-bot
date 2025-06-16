"""Tests for the query parser."""

import pytest
from src.query_parser import QueryParser


class TestQueryParser:
    """Test the main QueryParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = QueryParser()
    
    def test_simple_keyword(self):
        """Test simple keyword search."""
        result = self.parser.parse("quantum")
        assert result.success
        assert result.query_string == "ti:quantum"
        assert result.search.max_results == 10
    
    def test_multiple_keywords(self):
        """Test multiple keywords."""
        result = self.parser.parse("quantum computing")
        assert result.success
        assert result.query_string == "ti:quantum AND ti:computing"
    
    def test_author_prefix(self):
        """Test author prefix."""
        result = self.parser.parse("@hinton")
        assert result.success
        assert result.query_string == "au:hinton"
    
    def test_category_prefix(self):
        """Test category prefix."""
        result = self.parser.parse("#cs.AI")
        assert result.success
        assert result.query_string == "cat:cs.AI"
    
    def test_category_shortcut(self):
        """Test category shortcuts."""
        result = self.parser.parse("#cs")
        assert result.success
        assert result.query_string == "cat:cs.*"
    
    def test_category_case_correction(self):
        """Test category case correction."""
        result = self.parser.parse("#cs.ai")
        assert result.success
        assert result.query_string == "cat:cs.AI"
    
    def test_all_fields_prefix(self):
        """Test all fields prefix."""
        result = self.parser.parse("*quantum")
        assert result.success
        assert result.query_string == "all:quantum"
    
    def test_abstract_prefix(self):
        """Test abstract prefix."""
        result = self.parser.parse("$quantum")
        assert result.success
        assert result.query_string == "abs:quantum"
    
    def test_number_specification(self):
        """Test result count specification."""
        result = self.parser.parse("quantum 50")
        assert result.success
        assert result.search.max_results == 50
    
    def test_sort_specification(self):
        """Test sort specification."""
        # New format
        result = self.parser.parse("quantum rd")
        assert result.success
        assert result.search.sort_by.name == "Relevance"
        assert result.search.sort_order.name == "Descending"
        
        # Short form
        result = self.parser.parse("quantum r")
        assert result.success
        assert result.search.sort_by.name == "Relevance"
        
        # Legacy format
        result = self.parser.parse("quantum R")
        assert result.success
        assert result.search.sort_by.name == "Relevance"
    
    def test_complex_query(self):
        """Test complex query with multiple components."""
        result = self.parser.parse("quantum @hinton #cs.AI 20 rd")
        assert result.success
        assert "ti:quantum" in result.query_string
        assert "au:hinton" in result.query_string
        assert "cat:cs.AI" in result.query_string
        assert result.search.max_results == 20
        assert result.search.sort_by.name == "Relevance"
    
    def test_phrase_search(self):
        """Test phrase search."""
        result = self.parser.parse('"quantum computing"')
        assert result.success
        assert result.query_string == 'ti:"quantum computing"'
    
    def test_mixed_query(self):
        """Test mixed query types."""
        result = self.parser.parse('neural @lecun #cs.LG 50')
        assert result.success
        assert "ti:neural" in result.query_string
        assert "au:lecun" in result.query_string
        assert "cat:cs.LG" in result.query_string
        assert result.search.max_results == 50
    
    def test_invalid_number(self):
        """Test invalid number handling."""
        result = self.parser.parse("quantum 5000")
        assert not result.success
        assert "must be between 1-1000" in result.error
    
    def test_invalid_category(self):
        """Test invalid category handling."""
        result = self.parser.parse("#invalid.category")
        assert not result.success
        assert "Category not found" in result.error
    
    def test_empty_query(self):
        """Test empty query handling."""
        result = self.parser.parse("")
        assert not result.success
        assert result.error == "Empty query"
    
    def test_default_sort(self):
        """Test default sort is submitted date descending."""
        result = self.parser.parse("quantum")
        assert result.success
        assert result.search.sort_by.name == "SubmittedDate"
        assert result.search.sort_order.name == "Descending"