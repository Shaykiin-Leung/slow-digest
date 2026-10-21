"""Render the morning digest as one calm Markdown page."""

from __future__ import annotations

from datetime import date

from .triage import Scored


def render(picks: list[Scored], surfaced: list[dict], deferred_count: int,
           errors: list[str], today: date) -> str:
    lines = [f"# Slow Digest — {today.isoformat()}", ""]
    if not picks and not surfaced:
        lines += ["Nothing crossed the bar today. Enjoy the quiet.", ""]
    for i, s in enumerate(picks, 1):
        lines.append(f"{i}. **[{s.entry.title}]({s.entry.link})**")
        lines.append(f"   _{s.reason}_ · score {s.score:.2f}")
    if surfaced:
        lines += ["", "## From the weekend pool", ""]
        for d in surfaced:
            lines.append(f"- **[{d['title']}]({d['link']})** _{d['reason']}_")
    lines += ["", f"---",
              f"{deferred_count} item(s) deferred by the budget valve. "
              f"They will surface on the weekend, not in your morning."]
    if errors:
        lines += ["", "<details><summary>Feed errors</summary>", ""]
        lines += [f"- {e}" for e in errors]
        lines += ["</details>"]
    return "\n".join(lines) + "\n"
