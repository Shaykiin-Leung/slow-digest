import tempfile
import unittest
from datetime import date
from pathlib import Path

from slow_digest.budget import Budget
from slow_digest.feeds import Entry
from slow_digest.triage import Scored


def scored(n):
    return [Scored(Entry(f"t{i}", f"https://x/{i}", "s", "src"),
                   1.0 - i * 0.1, "r") for i in range(n)]


class BudgetTest(unittest.TestCase):
    def test_budget_caps_and_defers(self):
        with tempfile.TemporaryDirectory() as td:
            b = Budget(Path(td) / "state.json")
            picks, surfaced = b.apply(scored(8), 5, 15, date(2026, 10, 21))
            self.assertEqual(len(picks), 5)       # Wednesday: cap holds
            self.assertEqual(len(surfaced), 0)    # nothing surfaces midweek
            self.assertEqual(len(b.deferred), 3)  # the rest waits quietly

    def test_weekend_drains_pool(self):
        with tempfile.TemporaryDirectory() as td:
            b = Budget(Path(td) / "state.json")
            b.apply(scored(8), 5, 15, date(2026, 10, 21))
            _, surfaced = b.apply([], 5, 15, date(2026, 10, 24))  # Saturday
            self.assertEqual(len(surfaced), 3)

    def test_seen_items_never_repeat(self):
        with tempfile.TemporaryDirectory() as td:
            b = Budget(Path(td) / "state.json")
            first = scored(3)
            b.apply(first, 5, 15, date(2026, 10, 21))
            picks, _ = b.apply(first, 5, 15, date(2026, 10, 22))
            self.assertEqual(picks, [])


if __name__ == "__main__":
    unittest.main()
