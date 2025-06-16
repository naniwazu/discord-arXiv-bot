#!/usr/bin/env python3
"""Test script to check if arXiv API supports wildcard searches for categories"""

import arxiv

# Test queries with different category patterns
test_queries = [
    "cat:cs.AI",           # Specific category
    "cat:cs.*",            # Wildcard attempt
    "cat:cs.AI OR cat:cs.LG OR cat:cs.CV",  # Multiple categories with OR
    "cat:cs.AI+OR+cat:cs.LG",  # URL-encoded version
]

print("Testing arXiv API wildcard support for categories:")
print("=" * 60)

for query in test_queries:
    print(f"\nTesting query: {query}")
    try:
        search = arxiv.Search(
            query=query,
            max_results=5,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        results = list(search.results())
        print(f"  Results found: {len(results)}")
        
        if results:
            # Check categories of first result
            first_result = results[0]
            print(f"  First result title: {first_result.title[:60]}...")
            print(f"  Categories: {', '.join(first_result.categories)}")
            
            # Check if we got results from multiple CS subcategories
            all_categories = set()
            for result in results:
                all_categories.update(result.categories)
            
            cs_categories = [cat for cat in all_categories if cat.startswith('cs.')]
            if len(cs_categories) > 1:
                print(f"  Found multiple CS categories: {', '.join(sorted(cs_categories))}")
        else:
            print("  No results found")
            
    except Exception as e:
        print(f"  Error: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("Conclusion:")
print("Check if cs.* returned results from multiple CS subcategories.")
print("If not, wildcard expansion may be needed.")