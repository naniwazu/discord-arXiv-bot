#!/usr/bin/env python3
"""Test the complete query parsing pipeline with the originally failing query."""

import sys
sys.path.insert(0, 'src')

from query_parser import parse

def test_complete_query(query: str):
    """Test complete query parsing."""
    print(f"Testing query: '{query}'")
    print("=" * 50)
    
    try:
        result = parse(query)
        print("Parse result:")
        print(f"  Valid: {result.is_valid}")
        if result.error:
            print(f"  Error: {result.error}")
        else:
            print(f"  arXiv query: {result.arxiv_query}")
            print(f"  Max results: {result.max_results}")
            print(f"  Sort by: {result.sort_by}")
            print(f"  Sort order: {result.sort_order}")
            if result.date_range:
                print(f"  Date range: {result.date_range}")
    except Exception as e:
        print(f"Exception: {e}")
    
    print()

if __name__ == "__main__":
    # Test the originally failing query
    failing_query = "#cond-mat.str-el >202506120600 <202506150600"
    test_complete_query(failing_query)
    
    # Test a few variations
    test_queries = [
        "#cond-mat.str-el",
        "#physics.gen-ph >20250101 <20250201",
        "#astro-ph.CO quantum mechanics 10",
        "#q-bio.QM AND neural networks"
    ]
    
    for query in test_queries:
        test_complete_query(query)