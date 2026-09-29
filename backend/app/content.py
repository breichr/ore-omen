"""Loads game content from content/ (docs: CLAUDE.md, "Inhalte als Daten")."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import jsonschema
import yaml

from app.game import constants as c

CATEGORIES = ("core", "production", "character", "defense", "supernatural")
COST_KEYS = set(c.RESOURCES) | {"dollars"}


def content_dir() -> Path:
    env = os.environ.get("OO_CONTENT_DIR")
    if env:
        return Path(env)
    # repo layout: backend/app/content.py → ../../content; Docker copies it to /app/content
    for candidate in (Path(__file__).resolve().parents[2] / "content", Path("/app/content")):
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError("content/ directory not found; set OO_CONTENT_DIR")


@dataclass(frozen=True)
class BuildingDef:
    code: str
    category: str
    name: str
    description: str
    cost: dict[str, int]
    time_min: int
    produces: dict[str, float] = field(default_factory=dict)
    produces_from_level: dict[str, int] = field(default_factory=dict)
    black_ore_per_level: int = 0
    excludes: tuple[str, ...] = ()

    @property
    def time_seconds(self) -> int:
        return self.time_min * 60


def parse_buildings(data: dict) -> dict[str, BuildingDef]:
    raw = data.get("buildings") or {}
    result: dict[str, BuildingDef] = {}
    for code, b in raw.items():
        d = BuildingDef(
            code=code,
            category=b["category"],
            name=b["name"],
            description=b.get("description", ""),
            cost=dict(b["cost"]),
            time_min=int(b["time_min"]),
            produces=dict(b.get("produces") or {}),
            produces_from_level=dict(b.get("produces_from_level") or {}),
            black_ore_per_level=int(b.get("black_ore_per_level", 0)),
            excludes=tuple(b.get("excludes") or ()),
        )
        if d.category not in CATEGORIES:
            raise ValueError(f"{code}: unknown category {d.category}")
        if not set(d.cost) <= COST_KEYS or any(v <= 0 for v in d.cost.values()):
            raise ValueError(f"{code}: invalid cost {d.cost}")
        if not set(d.produces) <= set(c.RESOURCES):
            raise ValueError(f"{code}: invalid produces {d.produces}")
        if not set(d.produces_from_level) <= set(d.produces):
            raise ValueError(f"{code}: produces_from_level without produces")
        if d.time_min <= 0:
            raise ValueError(f"{code}: time_min must be positive")
        result[code] = d
    for d in result.values():
        for other in d.excludes:
            if other not in result or d.code not in result[other].excludes:
                raise ValueError(f"{d.code}: exclusion with {other} must be mutual")
    if "main_house" not in result or "storehouse" not in result:
        raise ValueError("main_house and storehouse are required")
    return result


@lru_cache
def buildings() -> dict[str, BuildingDef]:
    with open(content_dir() / "buildings.yaml", encoding="utf-8") as f:
        return parse_buildings(yaml.safe_load(f))


@dataclass(frozen=True)
class JobDef:
    code: str
    name: str
    description: str
    minutes: int
    yield_: dict[str, int]
    xp: int

    @property
    def seconds(self) -> int:
        return self.minutes * 60


def parse_jobs(data: dict) -> dict[str, JobDef]:
    result: dict[str, JobDef] = {}
    for code, j in (data.get("jobs") or {}).items():
        d = JobDef(
            code=code,
            name=j["name"],
            description=j.get("description", ""),
            minutes=int(j["minutes"]),
            yield_=dict(j["yield"]),
            xp=int(j["xp"]),
        )
        if d.minutes <= 0 or d.xp < 0:
            raise ValueError(f"{code}: minutes must be positive, xp non-negative")
        if not d.yield_ or not set(d.yield_) <= COST_KEYS or any(v <= 0 for v in d.yield_.values()):
            raise ValueError(f"{code}: invalid yield {d.yield_}")
        result[code] = d
    return result


@lru_cache
def jobs() -> dict[str, JobDef]:
    with open(content_dir() / "jobs.yaml", encoding="utf-8") as f:
        return parse_jobs(yaml.safe_load(f))


@dataclass(frozen=True)
class ItemDef:
    code: str
    name: str
    description: str


@lru_cache
def items() -> dict[str, ItemDef]:
    with open(content_dir() / "items.yaml", encoding="utf-8") as f:
        raw = (yaml.safe_load(f) or {}).get("items") or {}
    return {k: ItemDef(k, v["name"], v.get("description", "")) for k, v in raw.items()}


def _quest_schema() -> dict:
    with open(content_dir() / "quests" / "schema.json", encoding="utf-8") as f:
        return json.load(f)


def _effect_refs(effects: dict) -> list[tuple[str, str]]:
    return [("item", i) for i in effects.get("items", [])]


def validate_quests(quests: dict[str, dict]) -> None:
    """Cross-checks beyond the JSON schema: references must exist and fit together."""
    item_codes, job_codes, building_codes = set(items()), set(jobs()), set(buildings())
    for qid, q in quests.items():
        if "after" in q and q["after"] not in quests:
            raise ValueError(f"{qid}: after '{q['after']}' does not exist")
        task = q.get("task") or {}
        if "job" in task and task["job"] not in job_codes:
            raise ValueError(f"{qid}: unknown job {task['job']}")
        if "build" in task and task["build"] not in building_codes:
            raise ValueError(f"{qid}: unknown building {task['build']}")
        if not (q.get("options") or task or "effects" in q or "text" in q):
            raise ValueError(f"{qid}: needs options, a task or a direct outcome")
        branches = [q]
        for opt in q.get("options") or []:
            branches += [opt, opt.get("success") or {}, opt.get("failure") or {}]
            req = opt.get("requires") or {}
            if "item" in req and req["item"] not in item_codes:
                raise ValueError(f"{qid}: requires unknown item {req['item']}")
            check = opt.get("check") or {}
            if "skill" in check and check["skill"] not in c.SKILLS_BY_ATTRIBUTE[check["attribute"]]:
                raise ValueError(
                    f"{qid}: skill {check['skill']} does not belong to {check['attribute']}"
                )
        for b in branches:
            for kind, ref in _effect_refs(b.get("effects") or {}):
                if kind == "item" and ref not in item_codes:
                    raise ValueError(f"{qid}: unknown item {ref}")
            nxt = (b.get("effects") or {}).get("next")
            if nxt and nxt not in quests:
                raise ValueError(f"{qid}: next '{nxt}' does not exist")


def load_quests(directory: Path) -> dict[str, dict]:
    validator = jsonschema.Draft202012Validator(_quest_schema())
    result: dict[str, dict] = {}
    for path in sorted(directory.rglob("*.json")):
        if path.name == "schema.json":
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
        if errors:
            e = errors[0]
            where = "/".join(str(p) for p in e.path)
            raise ValueError(f"{path.name}: {where}: {e.message}")
        if data["id"] in result:
            raise ValueError(f"{path.name}: duplicate id {data['id']}")
        result[data["id"]] = data
    validate_quests(result)
    return result


@lru_cache
def quests() -> dict[str, dict]:
    return load_quests(content_dir() / "quests")
