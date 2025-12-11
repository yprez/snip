# snip - Code Snippet Manager

## Workflow

- **Commit after every small step** - don't batch changes
- Use `uv` for package management, not pip

## Project Structure

- `src/snip/` - Main package
  - `cli.py` - Click-based CLI commands
  - `storage.py` - File-based storage for snippets
- `pyproject.toml` - Project config with uv

## Development

```bash
uv venv && source .venv/bin/activate
uv pip install -e .
```

## Key Details

- Python 3.8+ compatible (uses `from __future__ import annotations`)
- Dependencies: click, rich, pyperclip
- Snippets stored in `~/.snip/snippets/` as individual files:
  - `<name>.<ext>` - The actual code file
  - `<name>.meta.json` - Metadata (language, tags, created)
- CLI entry point: `snip` -> `snip.cli:main`
