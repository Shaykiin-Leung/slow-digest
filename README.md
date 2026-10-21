# Slow Digest 🐌

**Every other tool wants you to read faster. This one wants you to read less.**

Slow Digest is a local-first morning digest. While you sleep, it reads
your RSS/Atom feeds, judges every article with a **local open-weight
model** (Ollama, e.g. `qwen2.5:3b`), and enforces a **strict push
budget**: at most *N* items may claim your morning. Everything else is
quietly deferred to a weekend pool — it surfaces on Saturday, not in
your notifications on Tuesday.

One calm Markdown page. Zero API cost. Your reading habits never
leave your machine.

## Why

Feeds are infinite; attention is not. Doomscrolling is what happens
when software has no budget. Slow Digest gives your information diet
the same discipline as a money budget:

- **Overnight, not real-time.** Nothing interrupts you during the day.
- **A budget valve, not a ranking.** Ranking still shows you everything,
  just sorted. A budget *withholds* — overflow waits for the weekend
  pool, which is capped and drains oldest-first.
- **Local judgment.** Triage runs on your own hardware with a local
  model. No cloud LLM, no API key, no bill, no telemetry. If Ollama
  isn't running, a transparent heuristic scorer takes over.

## How it works

```
        overnight (cron / Task Scheduler)
 feeds ───────► fetch ──► triage ──► budget valve ──► morning digest
 RSS/Atom      stdlib     local LLM    ≤ N today      data/digests/
                          or heuristic rest → weekend pool   YYYY-MM-DD.md
```

| Stage | What happens |
| --- | --- |
| Fetch | RSS/Atom via the Python standard library only. A broken feed never sinks the run. |
| Triage | Ollama scores each entry 0–1 with a one-line reason, against *your* stated interests. Falls back to a heuristic scorer when the model is unavailable. |
| Budget | Top `daily_budget` items are picked; the rest are deferred. On weekends the pool surfaces up to `weekend_budget` items. Seen items never repeat. |
| Digest | One Markdown page: picks with reasons, weekend pool, and a count of what was withheld. |

## Quickstart

Requires **Python 3.11+**. No third-party dependencies.

```bash
git clone https://github.com/Shaykiin-Leung/slow-digest.git
cd slow-digest
cp config.example.toml config.toml   # edit feeds, interests, budget
python -m slow_digest run --dry-run  # preview today's digest
python -m slow_digest run            # write data/digests/<date>.md
```

For LLM triage, run [Ollama](https://ollama.com) locally and pull a
small model (`ollama pull qwen2.5:3b`). Without it, set
`model = "heuristic"` in `config.toml` — everything still works.

Schedule it overnight, e.g. cron at 06:30:

```cron
30 6 * * * cd /path/to/slow-digest && python -m slow_digest run
```

Then read `data/digests/` with your morning coffee — from any notes
app, static site, or just `cat`.

## Configuration

See `config.example.toml`. The knobs that matter:

- `daily_budget` — the whole point. Start with 5. Lower it when life is busy.
- `interests` / `ignore_keywords` — fed to both the model prompt and the heuristic.
- `model` — any Ollama model name, or `"heuristic"`.

## Roadmap

- [ ] Email / webhook delivery of the digest page
- [ ] Per-feed budgets (a noisy feed shouldn't eat the whole budget)
- [ ] "Focus of the week" — one interest boosted for seven days
- [ ] A tiny static HTML view for the digest archive

## Development

```bash
python -m unittest discover -s tests
```

Design note: *informed by a private prototype built earlier in
October 2026; all code in this repository was written fresh during
the DEV Hacktoberfest Week 3 challenge window (Oct 19–25, 2026).*

## License

MIT — see [LICENSE](LICENSE).
