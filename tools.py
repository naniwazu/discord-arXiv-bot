import datetime
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

default_since = datetime.datetime(1900, 1, 1, 0, 0, 0)
default_until = datetime.datetime(2100, 1, 1, 0, 0, 0)


def parse(search_query):
    queries = []
    max_results = default_max_result
    since = default_since
    until = default_until
    sort_by = arxiv.SortCriterion.SubmittedDate
    chunks = list(search_query.split())
    for chunk in chunks:
        if chunk in sort_by_dict:
            sort_by = sort_by_dict[chunk]
        elif chunk[0] == '<':
            continue  # ignore mention chunk
        elif chunk.isdecimal():
            new_max_results = int(chunk)
            if 1 <= new_max_results <= 100:
                max_results = new_max_results
        elif chunk.count(":") == 1:
            prefix, body = chunk.split(":")
            if prefix == 'since':
                if len(body) == 8:
                    since = datetime.datetime.strptime(
                        body, '%Y%m%d') + datetime.timedelta(hours=-9)
                elif len(body) == 12:
                    since = datetime.datetime.strptime(
                        body, '%Y%m%d%H%M') + datetime.timedelta(hours=-9)
                elif len(body) == 14:
                    since = datetime.datetime.strptime(
                        body, '%Y%m%d%H%M%S') + datetime.timedelta(hours=-9)
                else:
                    return None
                continue
            if prefix == 'until':
                if len(body) == 8:
                    until = datetime.datetime.strptime(
                        body, '%Y%m%d') + datetime.timedelta(days=1, hours=-9)  # end of the day
                elif len(body) == 12:
                    until = datetime.datetime.strptime(
                        body, '%Y%m%d%H%M') + datetime.timedelta(hours=-9)
                elif len(body) == 14:
                    until = datetime.datetime.strptime(
                        body, '%Y%m%d%H%M%S') + datetime.timedelta(hours=-9)
                else:
                    return None
                continue
            if prefix not in search_field:
                continue
            keywords = body.split(",")
            for keyword in keywords:
                queries.append(prefix + ":" + keyword)
        else:
            return None
    if since != default_since or until != default_until:
        queries.append('submittedDate:[{} TO {}]'.format(
            datetime.datetime.strftime(since, '%Y%m%d%H%M%S'), datetime.datetime.strftime(until, '%Y%m%d%H%M%S')))
    query = " AND ".join(queries)
    return arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=sort_by,
        sort_order=arxiv.SortOrder.Descending
    )
