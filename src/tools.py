from __future__ import annotations

import datetime

import arxiv

DEFAULT_RESULT_COUNT: int = 10
RESULT_COUNT_LIMIT: int = 1000
SORTBY_DICT: dict[str, arxiv.SortCriterion] = {
    "L": arxiv.SortCriterion.LastUpdatedDate,
    "l": arxiv.SortCriterion.LastUpdatedDate,
    "R": arxiv.SortCriterion.Relevance,
    "r": arxiv.SortCriterion.Relevance,
    "S": arxiv.SortCriterion.SubmittedDate,
    "s": arxiv.SortCriterion.SubmittedDate,
}
search_field: set[str] = {
    "ti",
    "au",
    "abs",
    "co",
    "jr",
    "cat",
    "rn",
    "id",
    "all",
}

DEFAULT_SINCE: datetime.datetime = datetime.datetime(
    1900,
    1,
    1,
    0,
    0,
    0,
    tzinfo=datetime.timezone.utc,
)
DEFAULT_UNTIL: datetime.datetime = datetime.datetime(
    2100,
    1,
    1,
    0,
    0,
    0,
    tzinfo=datetime.timezone.utc,
)


def parse(search_query: str) -> arxiv.Search | None:
    queries: list[str] = []
    max_results: int = DEFAULT_RESULT_COUNT
    since: datetime.datetime = DEFAULT_SINCE
    until: datetime.datetime = DEFAULT_UNTIL
    sort_by: arxiv.SortCriterion = arxiv.SortCriterion.SubmittedDate
    chunks: list[str] = list(search_query.split())

    for chunk in chunks:
        if chunk in SORTBY_DICT:
            sort_by = SORTBY_DICT[chunk]
        elif chunk[0] == "<":
            continue  # ignore mention chunk
        elif chunk.isdecimal():
            new_max_results = int(chunk)
            if 1 <= new_max_results <= RESULT_COUNT_LIMIT:
                max_results = new_max_results
        elif chunk.count(":") == 1:
            prefix, body = chunk.split(":")
            if prefix == "since":
                if len(body) == 8:
                    since = datetime.datetime.strptime(body, "%Y%m%d") + datetime.timedelta(
                        hours=-9,
                    )
                elif len(body) == 12:
                    since = datetime.datetime.strptime(body, "%Y%m%d%H%M") + datetime.timedelta(
                        hours=-9,
                    )
                elif len(body) == 14:
                    since = datetime.datetime.strptime(body, "%Y%m%d%H%M%S") + datetime.timedelta(
                        hours=-9,
                    )
                else:
                    return None
                continue
            if prefix == "until":
                if len(body) == 8:
                    until = datetime.datetime.strptime(body, "%Y%m%d") + datetime.timedelta(
                        days=1,
                        hours=-9,
                    )  # end of the day
                elif len(body) == 12:
                    until = datetime.datetime.strptime(body, "%Y%m%d%H%M") + datetime.timedelta(
                        hours=-9,
                    )
                elif len(body) == 14:
                    until = datetime.datetime.strptime(body, "%Y%m%d%H%M%S") + datetime.timedelta(
                        hours=-9,
                    )
                else:
                    return None
                continue
            if prefix not in search_field:
                continue
            keywords = body.split(",")
            queries.extend([f"{prefix}:{keyword}" for keyword in keywords])
        else:
            return None

    if since != DEFAULT_SINCE or until != DEFAULT_UNTIL:
        queries.append(
            "submittedDate:[{} TO {}]".format(
                datetime.datetime.strftime(since, "%Y%m%d%H%M%S"),
                datetime.datetime.strftime(until, "%Y%m%d%H%M%S"),
            ),
        )

    query = " AND ".join(queries)
    return arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=sort_by,
        sort_order=arxiv.SortOrder.Descending,
    )
