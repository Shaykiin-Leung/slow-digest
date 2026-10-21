"""Configuration loading (TOML, stdlib only)."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    feeds: list[str]
    model: str = "qwen2.5:3b"          # Ollama model name, or "heuristic"
    ollama_url: str = "http://localhost:11434"
    daily_budget: int = 5              # max items in the morning digest
    weekend_budget: int = 15           # deferred pool cap on Sat/Sun
    interests: list[str] = field(default_factory=list)
    ignore_keywords: list[str] = field(default_factory=list)
    data_dir: str = "data"

    @classmethod
    def load(cls, path: str | Path) -> "Config":
        raw = tomllib.loads(Path(path).read_text(encoding="utf-8"))
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in raw.items() if k in known})
