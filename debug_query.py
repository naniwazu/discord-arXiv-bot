#!/usr/bin/env python3
"""Debug the specific failing query."""

import sys
sys.path.insert(0, 'src')

from query_parser.tokenizer import Tokenizer
from query_parser.validator import QueryValidator
from query_parser.types import Token, TokenType

def debug_query(query: str):
    """Debug a query by showing tokenization and validation results."""
    print(f"Query: '{query}'")
    print("=" * 50)
    
    # Tokenize
    tokenizer = Tokenizer()
    tokens = tokenizer.tokenize(query)
    
    print("Tokens:")
    for i, token in enumerate(tokens):
        print(f"  {i}: {token.type.name} = '{token.value}' (pos: {token.position})")
    
    print()
    
    # Validate
    validator = QueryValidator()
    result = validator.validate(tokens)
    
    print(f"Validation result: {'VALID' if result.is_valid else 'INVALID'}")
    if result.error:
        print(f"Error: {result.error}")
    
    print()
    
    # Test the specific category validation
    category_tokens = [t for t in tokens if t.type == TokenType.CATEGORY]
    if category_tokens:
        print("Category validation details:")
        for token in category_tokens:
            is_valid = validator._is_valid_category_pattern(token.value)
            print(f"  Category '{token.value}': {'VALID' if is_valid else 'INVALID'}")
            
            # Test the regex pattern manually
            import re
            pattern = r"^[a-zA-Z]+([-.][a-zA-Z]+)*$"
            regex_match = bool(re.match(pattern, token.value))
            print(f"    Regex pattern match: {regex_match}")
            print(f"    Pattern: {pattern}")
    
    print()

if __name__ == "__main__":
    # Test the failing query
    failing_query = "#cond-mat.str-el >202506120600 <202506150600"
    debug_query(failing_query)
    
    # Test a few other category formats to compare
    test_queries = [
        "#cs.AI",
        "#cond-mat",
        "#quant-ph", 
        "#physics.gen-ph",
        "#cond-mat.str-el",
    ]
    
    for query in test_queries:
        print(f"\nTesting category: {query}")
        debug_query(query)