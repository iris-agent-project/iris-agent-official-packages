"""The Search package's program: web_search and web_extract, through Firecrawl.

The declaration beside this folder, iris-package.json, says what each tool
takes and gives back. This file holds the function behind each. A request
goes to the worker's broker, which adds the Firecrawl key, so the program
never holds it. Nothing here logs or raises a query, a URL or a page's text.
"""
from iris_sdk import Failure, http, log, serve, tool

SEARCH = "https://api.firecrawl.dev/v2/search"
SCRAPE = "https://api.firecrawl.dev/v2/scrape"

# The bounds the output schemas give.
LONGEST_TITLE, LONGEST_URL, LONGEST_DESCRIPTION = 300, 2000, 1000
LONGEST_PAGE = 15000

# A refusal by the service, as the code a tool fails with.
REFUSALS = {401: "key-refused", 403: "key-refused", 402: "out-of-credit", 429: "rate-limited"}


def refusal(status):
    """The code for an answer whose status isn't 200."""
    if status in REFUSALS:
        return REFUSALS[status]
    return "service-failed" if status >= 500 else "service-refused"


def read(answer):
    """An answer's JSON, which is an object."""
    try:
        body = answer.json()
    except (ValueError, RecursionError):
        raise Failure("bad-answer") from None
    if not isinstance(body, dict):
        raise Failure("bad-answer")
    return body


def text(value, longest):
    """A string no longer than its bound, or none."""
    return value[:longest] if isinstance(value, str) else ""


@tool("web_search")
def web_search(query, limit=5):
    answer = http.post(SEARCH, json={"query": query, "limit": limit})
    if answer.status != 200:
        raise Failure(refusal(answer.status))
    data = read(answer).get("data")
    if not isinstance(data, dict):
        raise Failure("bad-answer")
    found = data.get("web") or data.get("results") or []
    if not isinstance(found, list):
        raise Failure("bad-answer")
    results = []
    for entry in found[:limit]:
        if isinstance(entry, dict):
            results.append({
                "title": text(entry.get("title"), LONGEST_TITLE),
                "url": text(entry.get("url"), LONGEST_URL),
                "description": text(entry.get("description"), LONGEST_DESCRIPTION),
            })
    log.event("search.answered", results=len(results))
    return {"results": results}


@tool("web_extract")
def web_extract(urls):
    pages = [page(url) for url in urls]
    log.event("extract.answered", pages=len(pages), failed=sum(1 for one in pages if one["error"]))
    return {"pages": pages}


def page(url):
    """One page: its text, or the code that says why it wasn't read."""
    if not url.startswith(("http://", "https://")):
        return unread(url, "bad-url")
    answer = http.post(SCRAPE, json={"url": url, "formats": ["markdown"]})
    if answer.status != 200:
        return unread(url, "not-found" if answer.status == 404 else refusal(answer.status))
    try:
        body = read(answer)
    except Failure as failure:
        return unread(url, failure.code)
    if body.get("success") is False:
        return unread(url, "service-refused")
    data = body.get("data")
    if not isinstance(data, dict):
        return unread(url, "bad-answer")
    metadata = data.get("metadata")
    title = metadata.get("title") if isinstance(metadata, dict) else None
    markdown = data.get("markdown")
    if not isinstance(markdown, str):
        markdown = ""
    return {
        "url": url,
        "title": text(title, LONGEST_TITLE),
        "content": markdown[:LONGEST_PAGE],
        "cut": len(markdown) > LONGEST_PAGE,
        "error": "",
    }


def unread(url, code):
    return {"url": url, "title": "", "content": "", "cut": False, "error": code}


serve()
