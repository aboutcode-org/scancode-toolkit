import re

# Keywords that indicate patent-related references
PATENT_KEYWORDS = [
    "patent pending",
    "patented",
    "patent application",
    "patent number",
]

# Precompile keyword regex patterns (case-insensitive)
KEYWORD_REGEXES = [
    re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)
    for keyword in PATENT_KEYWORDS
]

# Regex for patent numbers and international formats
PATENT_NUMBER_REGEX = re.compile(
    r"""
    \b
    (?:
        (?:US|EP|WO|JP|CN|KR|GB|IN)       # Country codes
        \s*
        (?:Patent(?:\s+No\.?)?\s*)?      # Optional 'Patent' or 'Patent No.'
        \d+(?:[,\/]\d+)*                 # Number part (allow commas/slashes)
        \s*(?:A1|A2|B1|B2)?              # Optional kind codes
    )
    \b
    """,
    re.IGNORECASE | re.VERBOSE,
)


def find_patents(location):
    """
    Detect patent references and patent-related keywords in a file.

    Return a list of tuples:
        (kind, value, line_number)
    where:
        kind: "number" or "keyword"
        value: matched text (original casing preserved)
        line_number: line where match occurred
    """
    results = []

    try:
        with open(location, "r", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return results

    for line_num, line in enumerate(lines, start=1):

        # Detect patent numbers
        for match in PATENT_NUMBER_REGEX.finditer(line):
            results.append(("number", match.group().strip(), line_num))

        # Detect keyword references
        for regex in KEYWORD_REGEXES:
            match = regex.search(line)
            if match:
                results.append(("keyword", match.group(), line_num))

    return results
    
