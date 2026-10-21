"""CLI: python -m slow_digest run [--config config.toml] [--dry-run]"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from .budget import Budget
from .config import Config
from .digest import render
from .feeds import fetch_all
from .triage import triage


def main() -> int:
    ap = argparse.ArgumentParser(prog="slow-digest")
    ap.add_argument("command", choices=["run"])
    ap.add_argument("--config", default="config.toml")
    ap.add_argument("--dry-run", action="store_true",
                    help="score and print, but write nothing")
    args = ap.parse_args()

    cfg = Config.load(args.config)
    today = date.today()
    entries, errors = fetch_all(cfg.feeds)
    scored = triage(cfg, entries)

    data_dir = Path(cfg.data_dir)
    budget = Budget(data_dir / "state.json")
    picks, surfaced = budget.apply(scored, cfg.daily_budget,
                                   cfg.weekend_budget, today)
    page = render(picks, surfaced, len(budget.deferred), errors, today)

    if args.dry_run:
        print(page)
        return 0

    out = data_dir / "digests" / f"{today.isoformat()}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    budget.save()
    log = {"date": today.isoformat(), "fetched": len(entries),
           "picked": len(picks), "deferred": len(budget.deferred),
           "errors": len(errors)}
    with open(data_dir / "log.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(log, ensure_ascii=False) + "\n")
    print(f"digest written to {out} "
          f"({len(picks)} picked, {len(budget.deferred)} deferred)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
