"""Load and persist saved city names with timestamps (JSON file next to this module)."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

_DATA_PATH = Path(__file__).resolve().parent / "saved_cities.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_entries() -> list[dict]:
    """Return list of {"id", "city", "saved_at"}; ensure each row has an id."""
    if not _DATA_PATH.is_file():
        return []
    try:
        raw = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(raw, list):
        return []
    out: list[dict] = []
    changed = False
    for row in raw:
        if not isinstance(row, dict):
            continue
        city = row.get("city")
        saved_at = row.get("saved_at")
        if not isinstance(city, str) or not city.strip():
            continue
        if not isinstance(saved_at, str):
            saved_at = _now_iso()
            changed = True
        eid = row.get("id")
        if not isinstance(eid, str) or not eid:
            eid = str(uuid.uuid4())
            changed = True
        out.append({"id": eid, "city": city.strip(), "saved_at": saved_at})
    if changed:
        write_entries(out)
    return out


def write_entries(entries: list[dict]) -> None:
    _DATA_PATH.write_text(
        json.dumps(entries, indent=2),
        encoding="utf-8",
    )


def upsert_city(city: str) -> list[dict]:
    """Add or update a city (case-insensitive match); refresh saved_at on update."""
    name = city.strip()
    if not name:
        return load_entries()
    entries = load_entries()
    key = name.casefold()
    for row in entries:
        if row["city"].casefold() == key:
            row["saved_at"] = _now_iso()
            row["city"] = name
            write_entries(entries)
            return entries
    entries.append({"id": str(uuid.uuid4()), "city": name, "saved_at": _now_iso()})
    write_entries(entries)
    return entries


def format_saved_at(iso: str) -> str:
    """Format stored ISO UTC time for display (local timezone)."""
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return iso
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    local = dt.astimezone()
    return local.strftime("%Y-%m-%d %H:%M")
