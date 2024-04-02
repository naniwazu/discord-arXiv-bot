from curses.ascii import isdigit
import arxiv

default_max_result = 10
sort_by_dict = {
    "L": arxiv.SortCriterion.LastUpdatedDate,
    "l": arxiv.SortCriterion.LastUpdatedDate,
    "R": arxiv.SortCriterion.Relevance,
    "r": arxiv.SortCriterion.Relevance,
    "S": arxiv.SortCriterion.SubmittedDate,
    "s": arxiv.SortCriterion.SubmittedDate
}
search_field = {
    "ti", "au", "abs", "co", "jr", "cat", "rn", "id", "all"
}


def parse(search_query):
    queries = []
    max_results = default_max_result
    sort_by = arxiv.SortCriterion.SubmittedDate
    chunks = list(search_query.split())
    for chunk in chunks:
        if chunk in sort_by_dict:
            sort_by = sort_by_dict[chunk]
        elif chunk.isdecimal():
            new_max_results = int(chunk)
            if 1 <= new_max_results <= 50:
                max_results = new_max_results
        elif chunk.count(":") == 1:
            prefix, body = chunk.split(":")
            if prefix not in search_field:
                continue
            keywords = body.split(",")
            for keyword in keywords:
                queries.append(prefix + ":" + keyword)
    query = " AND ".join(queries)
    return arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=sort_by,
        sort_order=arxiv.SortOrder.Descending
    )
