"""Storage module for managing snippets."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_storage_path() -> Path:
    """Get the path to the snippets storage file."""
    storage_dir = Path.home() / ".snip"
    storage_dir.mkdir(exist_ok=True)
    return storage_dir / "snippets.json"


def load_snippets() -> dict:
    """Load snippets from storage."""
    path = get_storage_path()
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_snippets(snippets: dict) -> None:
    """Save snippets to storage."""
    path = get_storage_path()
    with open(path, "w") as f:
        json.dump(snippets, f, indent=2)


def add_snippet(
    name: str,
    code: str,
    language: str = "text",
    tags: Optional[list[str]] = None,
) -> None:
    """Add a new snippet."""
    snippets = load_snippets()
    snippets[name] = {
        "code": code,
        "language": language,
        "tags": tags or [],
        "created": datetime.now().isoformat(),
    }
    save_snippets(snippets)


def get_snippet(name: str) -> Optional[dict]:
    """Get a snippet by name."""
    snippets = load_snippets()
    return snippets.get(name)


def delete_snippet(name: str) -> bool:
    """Delete a snippet by name. Returns True if deleted, False if not found."""
    snippets = load_snippets()
    if name in snippets:
        del snippets[name]
        save_snippets(snippets)
        return True
    return False


def search_snippets(query: str) -> dict:
    """Search snippets by name, language, or tags."""
    snippets = load_snippets()
    query = query.lower()
    results = {}
    for name, data in snippets.items():
        if (
            query in name.lower()
            or query in data["language"].lower()
            or any(query in tag.lower() for tag in data["tags"])
        ):
            results[name] = data
    return results


def list_all_snippets() -> dict:
    """List all snippets."""
    return load_snippets()
