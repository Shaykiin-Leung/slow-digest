"""The push-budget valve — the heart of Slow Digest.

Attention is finite, so the digest is too. At most `daily_budget`
items may reach your morning. Everything else is deferred to a
weekend pool instead of interrupting you today; the pool is capped
and drains oldest-first, so nothing nags forever.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date
from pathlib import Path

from .triage import Scored


class Budget:
    def __init__(self, state_path: Path):
        self.state_path = state_path
        self.seen: set[str] = set()
        self.deferred: list[dict] = []
        if state_path.exists():
            raw = json.loads(state_path.read_text(encoding="utf-8"))
            self.seen = set(raw.get("seen", []))
            self.deferred = raw.get("deferred", [])

    def save(self) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps({
            "seen": sorted(self.seen),
            "deferred": self.deferred,
        }, ensure_ascii=False, indent=1), encoding="utf-8")

    def apply(self, scored: list[Scored], daily_budget: int,
              weekend_cap: int, today: date) -> tuple[list[Scored], list[dict]]:
        """Return (today's picks, deferred items surfaced on weekends)."""
        fresh = [s for s in scored if s.entry.uid not in self.seen]
        picks = fresh[:daily_budget]
        overflow = fresh[daily_budget:]
        for s in picks:
            self.seen.add(s.entry.uid)
        for s in overflow:
            self.seen.add(s.entry.uid)
            self.deferred.append({
                "title": s.entry.title, "link": s.entry.link,
                "score": round(s.score, 2), "reason": s.reason,
                "deferred_on": today.isoformat(),
            })
        surfaced: list[dict] = []
        if today.weekday() >= 5:  # Saturday / Sunday: drain the pool
            surfaced = self.deferred[:weekend_cap]
            self.deferred = self.deferred[weekend_cap:]
        self.deferred = self.deferred[-200:]  # hard cap, oldest dropped
        return picks, surfaced
