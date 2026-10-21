"""Triage: score how much each entry deserves your morning.

Primary path: a local open-weight model served by Ollama — the
article text never leaves your machine and there is no API bill.
Fallback path: a transparent heuristic scorer, used when Ollama is
not running or when the config sets model = "heuristic".
"""

from __future__ import annotations

import json
import re
import urllib.request
from dataclasses import dataclass

from .config import Config
from .feeds import Entry


@dataclass
class Scored:
    entry: Entry
    score: float          # 0..1
    reason: str


PROMPT = """You are the night editor of a personal morning digest.
The reader's interests: {interests}.
Score the article from 0.0 to 1.0 for how much it deserves a place
in tomorrow's digest. Reward substance, originality and relevance;
punish clickbait, listicles and repetition.
Reply with ONLY a JSON object: {{"score": 0.0, "reason": "one short line"}}.

Title: {title}
Source: {source}
Summary: {summary}
"""


def _ollama_score(cfg: Config, entry: Entry) -> Scored | None:
    prompt = PROMPT.format(
        interests=", ".join(cfg.interests) or "technology, open source",
        title=entry.title, source=entry.source, summary=entry.summary[:400],
    )
    body = json.dumps({
        "model": cfg.model, "prompt": prompt, "stream": False,
        "options": {"temperature": 0.1},
    }).encode()
    req = urllib.request.Request(
        cfg.ollama_url.rstrip("/") + "/api/generate",
        data=body, headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            text = json.loads(resp.read())["response"]
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            return None
        data = json.loads(match.group(0))
        return Scored(entry, float(data["score"]), str(data["reason"])[:120])
    except Exception:  # noqa: BLE001 - any failure falls back to heuristic
        return None


def _heuristic_score(cfg: Config, entry: Entry) -> Scored:
    hay = (entry.title + " " + entry.summary).lower()
    for bad in cfg.ignore_keywords:
        if bad.lower() in hay:
            return Scored(entry, 0.05, f"ignored keyword: {bad}")
    hits = [k for k in cfg.interests if k.lower() in hay]
    score = 0.35 + 0.2 * len(hits)
    if len(entry.summary) > 240:
        score += 0.1                      # substance proxy
    if re.search(r"\b(top \d+|you won't believe|shocking)\b", hay):
        score -= 0.25                     # clickbait proxy
    reason = "matches: " + ", ".join(hits) if hits else "general interest"
    return Scored(entry, max(0.0, min(1.0, score)), reason)


def triage(cfg: Config, entries: list[Entry]) -> list[Scored]:
    use_llm = cfg.model != "heuristic"
    out: list[Scored] = []
    for entry in entries:
        scored = _ollama_score(cfg, entry) if use_llm else None
        out.append(scored or _heuristic_score(cfg, entry))
    out.sort(key=lambda s: s.score, reverse=True)
    return out
