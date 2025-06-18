#!/usr/bin/env python3
from src.query_parser import QueryParser

p = QueryParser()
test_cases = [
    'quantum | neural',
    'quantum machine | neural networks', 
    'quantum | neural | ai',
    '@smith | @johnson',
    '@einstein | #physics',
    'quantum - |',
    'quantum -'
]

for case in test_cases:
    result = p.parse(case)
    if result.success:
        print(f'{case:30} -> {result.search.query}')
    else:
        print(f'{case:30} -> ERROR: {result.error}')