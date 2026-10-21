"""RSS / Atom fetching with the standard library only."""

from __future__ import annotations

import hashlib
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass

UA = "SlowDigest/0.1 (+https://github.com/Shaykiin-Leung/slow-digest)"
NS = {"atom": "http://www.w3.org/2005/Atom"}


@dataclass
class Entry:
    title: str
    link: str
    summary: str
    source: str

    @property
    def uid(self) -> str:
        return hashlib.sha256(self.link.encode()).hexdigest()[:16]


def _text(node, *tags) -> str:
    for tag in tags:
        el = node.find(tag)
        if el is not None and el.text:
            return " ".join(el.text.split())[:600]
    return ""


def _parse_rss(root, source: str) -> list[Entry]:
    out = []
    for item in root.iter("item"):
        out.append(Entry(
            title=_text(item, "title"),
            link=_text(item, "link"),
            summary=_text(item, "description"),
            source=source,
        ))
    return out


def _parse_atom(root, source: str) -> list[Entry]:
    out = []
    for e in root.iter("{http://www.w3.org/2005/Atom}entry"):
        link = ""
        for ln in e.findall("atom:link", NS):
            if ln.get("rel") in (None, "alternate"):
                link = ln.get("href", "")
                break
        out.append(Entry(
            title=_text(e, "atom:title"),
            link=link,
            summary=_text(e, "atom:summary", "atom:content"),
            source=source,
        ))
    return out


def fetch(url: str, timeout: int = 20) -> list[Entry]:
    """Fetch one feed URL (http(s):// or file://) and return its entries."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = resp.read()
    root = ET.fromstring(payload)
    if root.tag.endswith("feed"):
        return _parse_atom(root, url)
    return _parse_rss(root, url)


def fetch_all(urls: list[str]) -> tuple[list[Entry], list[str]]:
    """Fetch every feed; a broken feed never sinks the whole run."""
    entries: list[Entry] = []
    errors: list[str] = []
    for url in urls:
        try:
            entries.extend(fetch(url))
        except Exception as exc:  # noqa: BLE001 - report and continue
            errors.append(f"{url}: {exc}")
    return entries, errors
