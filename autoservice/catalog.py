from functools import lru_cache
from pathlib import Path

import yaml

DATA = Path(__file__).resolve().parent.parent / "data" / "services.yaml"


@lru_cache
def _load() -> dict:
    return yaml.safe_load(DATA.read_text(encoding="utf-8"))


def site() -> dict:
    return _load()["site"]


def services() -> list[dict]:
    return _load()["services"]


def by_slug(slug: str) -> dict | None:
    return next((s for s in services() if s["slug"] == slug), None)
