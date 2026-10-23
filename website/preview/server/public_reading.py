"""Cache policy for public, identical static bytes; never for workflow state."""

from pathlib import PurePosixPath
from urllib.parse import urlsplit


PUBLIC_PAGES = frozenset({
    "/", "/index.html", "/project.html", "/participate.html",
    "/research-review-platforms.html", "/report-templates.html",
    "/exemplary-cases.html", "/privacy.html", "/terms.html",
    "/robots.txt", "/sitemap.xml",
})


def cache_control(target, method, status, extra=None):
    request = urlsplit(target)
    path = request.path
    # An unknown query is not assumed harmless. Only successful, canonical
    # static reads with no session-setting response may enter a shared cache.
    if (
        method not in {"GET", "HEAD"}
        or status != 200
        or request.query
        or "%" in path
        or "\\" in path
        or any(key.casefold() == "set-cookie" for key in (extra or {}))
    ):
        return "no-store"
    public = (
        path in PUBLIC_PAGES
        or path.startswith("/atlas/")
        or path.startswith("/assets/report-templates/")
        or (path.count("/") == 1 and PurePosixPath(path).suffix in {
            ".css", ".js", ".svg", ".woff2",
        })
    )
    if not public:
        return "no-store"
    # These stable URLs may change in a later release: do not label them
    # immutable. Deployments purge them; stale content is bounded to one day
    # during origin errors. Account, availability and attachment APIs bypass.
    return "public, max-age=300, s-maxage=3600, stale-if-error=86400"
