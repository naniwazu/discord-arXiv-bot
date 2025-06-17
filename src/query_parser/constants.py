"""Constants for query parser."""

import arxiv

# Default values
DEFAULT_RESULT_COUNT = 10
RESULT_COUNT_LIMIT = 1000
DEFAULT_TIMEZONE_OFFSET = -9  # JST

# Category shortcuts
CATEGORY_SHORTCUTS = {
    "cs": "cs.*",
    "physics": "physics.*",
    "math": "math.*",
    "stat": "stat.*",
    "econ": "econ.*",
    "q-bio": "q-bio.*",
    "q-fin": "q-fin.*",
    "cond-mat": "cond-mat.*",
    "astro-ph": "astro-ph.*",
    "quant-ph": "quant-ph.*",
    "nlin": "nlin.*",
    "math-ph": "math-ph.*",
}

# Category name corrections (lowercase -> correct case)
CATEGORY_CORRECTIONS = {
    # Computer Science
    "cs.ai": "cs.AI",
    "cs.ar": "cs.AR",
    "cs.cc": "cs.CC",
    "cs.ce": "cs.CE",
    "cs.cg": "cs.CG",
    "cs.cl": "cs.CL",
    "cs.cr": "cs.CR",
    "cs.cv": "cs.CV",
    "cs.cy": "cs.CY",
    "cs.db": "cs.DB",
    "cs.dc": "cs.DC",
    "cs.dl": "cs.DL",
    "cs.dm": "cs.DM",
    "cs.ds": "cs.DS",
    "cs.et": "cs.ET",
    "cs.fl": "cs.FL",
    "cs.gl": "cs.GL",
    "cs.gr": "cs.GR",
    "cs.gt": "cs.GT",
    "cs.hc": "cs.HC",
    "cs.ir": "cs.IR",
    "cs.it": "cs.IT",
    "cs.lg": "cs.LG",
    "cs.lo": "cs.LO",
    "cs.ma": "cs.MA",
    "cs.mm": "cs.MM",
    "cs.ms": "cs.MS",
    "cs.na": "cs.NA",
    "cs.ne": "cs.NE",
    "cs.ni": "cs.NI",
    "cs.oh": "cs.OH",
    "cs.os": "cs.OS",
    "cs.pf": "cs.PF",
    "cs.pl": "cs.PL",
    "cs.ro": "cs.RO",
    "cs.sc": "cs.SC",
    "cs.sd": "cs.SD",
    "cs.se": "cs.SE",
    "cs.si": "cs.SI",
    "cs.sy": "cs.SY",
    # Statistics
    "stat.ap": "stat.AP",
    "stat.co": "stat.CO",
    "stat.me": "stat.ME",
    "stat.ml": "stat.ML",
    "stat.ot": "stat.OT",
    "stat.th": "stat.TH",
    # Mathematics
    "math.ac": "math.AC",
    "math.ag": "math.AG",
    "math.ap": "math.AP",
    "math.at": "math.AT",
    "math.ca": "math.CA",
    "math.co": "math.CO",
    "math.ct": "math.CT",
    "math.cv": "math.CV",
    "math.dg": "math.DG",
    "math.ds": "math.DS",
    "math.fa": "math.FA",
    "math.gm": "math.GM",
    "math.gn": "math.GN",
    "math.gr": "math.GR",
    "math.gt": "math.GT",
    "math.ho": "math.HO",
    "math.it": "math.IT",
    "math.kt": "math.KT",
    "math.lo": "math.LO",
    "math.mg": "math.MG",
    "math.mp": "math.MP",
    "math.na": "math.NA",
    "math.nt": "math.NT",
    "math.oa": "math.OA",
    "math.oc": "math.OC",
    "math.pr": "math.PR",
    "math.qa": "math.QA",
    "math.ra": "math.RA",
    "math.rt": "math.RT",
    "math.sg": "math.SG",
    "math.sp": "math.SP",
    "math.st": "math.ST",
    # Add more as needed
}

# Sort mappings
SORT_MAPPINGS = {
    # New format
    "sd": (arxiv.SortCriterion.SubmittedDate, arxiv.SortOrder.Descending),
    "sa": (arxiv.SortCriterion.SubmittedDate, arxiv.SortOrder.Ascending),
    "rd": (arxiv.SortCriterion.Relevance, arxiv.SortOrder.Descending),
    "ra": (arxiv.SortCriterion.Relevance, arxiv.SortOrder.Ascending),
    "ld": (arxiv.SortCriterion.LastUpdatedDate, arxiv.SortOrder.Descending),
    "la": (arxiv.SortCriterion.LastUpdatedDate, arxiv.SortOrder.Ascending),
    # Short forms (default to descending)
    "s": (arxiv.SortCriterion.SubmittedDate, arxiv.SortOrder.Descending),
    "r": (arxiv.SortCriterion.Relevance, arxiv.SortOrder.Descending),
    "l": (arxiv.SortCriterion.LastUpdatedDate, arxiv.SortOrder.Descending),
}

# Default sort
DEFAULT_SORT = (arxiv.SortCriterion.SubmittedDate, arxiv.SortOrder.Descending)

# arXiv field mappings
ARXIV_FIELDS = {
    "ti": "title",
    "au": "author",
    "abs": "abstract",
    "co": "comment",
    "jr": "journal reference",
    "cat": "category",
    "rn": "report number",
    "id": "id",
    "all": "all",
}
