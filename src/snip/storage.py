"""Storage module for managing snippets."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

# Map languages to file extensions
LANG_EXTENSIONS = {
    "python": ".py",
    "javascript": ".js",
    "typescript": ".ts",
    "rust": ".rs",
    "go": ".go",
    "ruby": ".rb",
    "java": ".java",
    "c": ".c",
    "cpp": ".cpp",
    "c++": ".cpp",
    "csharp": ".cs",
    "c#": ".cs",
    "php": ".php",
    "swift": ".swift",
    "kotlin": ".kt",
    "scala": ".scala",
    "shell": ".sh",
    "bash": ".sh",
    "zsh": ".zsh",
    "fish": ".fish",
    "powershell": ".ps1",
    "sql": ".sql",
    "html": ".html",
    "css": ".css",
    "scss": ".scss",
    "sass": ".sass",
    "less": ".less",
    "json": ".json",
    "yaml": ".yaml",
    "yml": ".yaml",
    "toml": ".toml",
    "xml": ".xml",
    "markdown": ".md",
    "md": ".md",
    "lua": ".lua",
    "perl": ".pl",
    "r": ".r",
    "julia": ".jl",
    "haskell": ".hs",
    "elixir": ".ex",
    "erlang": ".erl",
    "clojure": ".clj",
    "lisp": ".lisp",
    "scheme": ".scm",
    "ocaml": ".ml",
    "fsharp": ".fs",
    "f#": ".fs",
    "zig": ".zig",
    "nim": ".nim",
    "v": ".v",
    "dart": ".dart",
    "vue": ".vue",
    "svelte": ".svelte",
    "jsx": ".jsx",
    "tsx": ".tsx",
    "text": ".txt",
}


def get_extension(language: str) -> str:
    """Get file extension for a language."""
    return LANG_EXTENSIONS.get(language.lower(), ".txt")


def get_snippets_dir() -> Path:
    """Get the path to the snippets directory."""
    snippets_dir = Path.home() / ".snip" / "snippets"
    snippets_dir.mkdir(parents=True, exist_ok=True)
    return snippets_dir


def sanitize_name(name: str) -> str:
    """Sanitize snippet name for use as filename."""
    # Replace problematic characters with underscores
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", name)
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(". ")
    return sanitized or "unnamed"


def get_snippet_paths(name: str, language: str) -> tuple[Path, Path]:
    """Get paths for code file and metadata file."""
    snippets_dir = get_snippets_dir()
    safe_name = sanitize_name(name)
    ext = get_extension(language)
    code_path = snippets_dir / f"{safe_name}{ext}"
    meta_path = snippets_dir / f"{safe_name}.meta.json"
    return code_path, meta_path


def find_snippet_files(name: str) -> tuple[Optional[Path], Optional[Path]]:
    """Find existing snippet files by name (searches for matching .meta.json)."""
    snippets_dir = get_snippets_dir()
    safe_name = sanitize_name(name)
    meta_path = snippets_dir / f"{safe_name}.meta.json"

    if not meta_path.exists():
        return None, None

    with open(meta_path, "r") as f:
        meta = json.load(f)

    ext = get_extension(meta.get("language", "text"))
    code_path = snippets_dir / f"{safe_name}{ext}"

    if not code_path.exists():
        return None, meta_path

    return code_path, meta_path


def add_snippet(
    name: str,
    code: str,
    language: str = "text",
    tags: Optional[list[str]] = None,
) -> None:
    """Add a new snippet."""
    code_path, meta_path = get_snippet_paths(name, language)

    # Write code file
    with open(code_path, "w") as f:
        f.write(code)

    # Write metadata
    meta = {
        "name": name,
        "language": language,
        "tags": tags or [],
        "created": datetime.now().isoformat(),
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)


def get_snippet(name: str) -> Optional[dict]:
    """Get a snippet by name."""
    code_path, meta_path = find_snippet_files(name)

    if not meta_path or not meta_path.exists():
        return None

    with open(meta_path, "r") as f:
        meta = json.load(f)

    if code_path and code_path.exists():
        with open(code_path, "r") as f:
            meta["code"] = f.read()
    else:
        meta["code"] = ""

    return meta


def delete_snippet(name: str) -> bool:
    """Delete a snippet by name. Returns True if deleted, False if not found."""
    code_path, meta_path = find_snippet_files(name)

    if not meta_path:
        return False

    if code_path and code_path.exists():
        code_path.unlink()
    if meta_path.exists():
        meta_path.unlink()

    return True


def update_snippet_meta(
    name: str,
    tags: Optional[list[str]] = None,
) -> bool:
    """Update snippet metadata. Returns True if updated, False if not found."""
    _, meta_path = find_snippet_files(name)

    if not meta_path or not meta_path.exists():
        return False

    with open(meta_path, "r") as f:
        meta = json.load(f)

    if tags is not None:
        meta["tags"] = tags

    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    return True


def list_all_snippets() -> dict:
    """List all snippets."""
    snippets_dir = get_snippets_dir()
    snippets = {}

    for meta_path in snippets_dir.glob("*.meta.json"):
        with open(meta_path, "r") as f:
            meta = json.load(f)

        name = meta.get("name", meta_path.stem.replace(".meta", ""))
        snippets[name] = meta

    return snippets


def search_snippets(query: str) -> dict:
    """Search snippets by name, language, or tags."""
    snippets = list_all_snippets()
    query = query.lower()
    results = {}

    for name, data in snippets.items():
        if (
            query in name.lower()
            or query in data.get("language", "").lower()
            or any(query in tag.lower() for tag in data.get("tags", []))
        ):
            results[name] = data

    return results
