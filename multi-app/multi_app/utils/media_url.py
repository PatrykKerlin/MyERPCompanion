from __future__ import annotations

from urllib.parse import urlparse, urlunparse


def normalize_media_url(url: str | None, api_url: str) -> str | None:
    if not url:
        return url
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return url
    if "/media/" not in parsed.path and not parsed.path.endswith("/media"):
        return url
    api_parsed = urlparse(api_url)
    if not api_parsed.scheme or not api_parsed.netloc:
        return url
    if parsed.scheme == api_parsed.scheme and parsed.netloc == api_parsed.netloc:
        return url
    return urlunparse(
        (api_parsed.scheme, api_parsed.netloc, parsed.path, parsed.params, parsed.query, parsed.fragment)
    )
