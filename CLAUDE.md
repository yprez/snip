# snip - Code Snippet Manager

A CLI tool to save, search, and retrieve code snippets with syntax highlighting, clipboard support, and direct execution.

## General guidelines

- When suggesting changes to a file, prefer breaking them into smaller chunks
- Never tell the user "you're absolutely right" or similar affirmations. Assume the user might be wrong and double-check their assumptions before proceeding
- Commit after every small step - don't batch changes

## Development commands

### Environment setup
```bash
uv sync                           # Install dependencies
uv sync --dev                     # Install with dev dependencies
```

### Running the application
```bash
uv run snip --help                # Show CLI help
uv run snip list                  # List all snippets
uv run snip add <name>            # Add snippet from stdin
uv run snip get <name>            # Display a snippet
uv run snip get <name> -c         # Copy snippet to clipboard
uv run snip search <query>        # Search snippets
uv run snip run <name>            # Execute a snippet
uv run snip edit <name>           # Edit in $EDITOR
uv run snip export <name>         # Export to file
uv run snip import <file>         # Import file as snippet
uv run snip delete <name>         # Delete a snippet
uv run snip path                  # Show storage directory
```

### Testing
```bash
uv run pytest                     # Run all tests
uv run pytest -v                  # Verbose output
uv run pytest --cov snip          # With coverage
uv run pytest tests/test_file.py  # Run specific test file
```

### Linting
```bash
uv run ruff check .               # Run linter
uv run ruff check . --fix         # Auto-fix issues
```

## Architecture

### Project structure
- `src/snip/` - Main package
  - `cli.py` - Click-based CLI commands (add, get, list, search, run, edit, export, import, delete, path)
  - `storage.py` - File-based storage for snippets
- `tests/` - Test suite
- `pyproject.toml` - Project configuration

### Storage system
Snippets are stored in `~/.snip/snippets/` as file pairs:
- `<name>.<ext>` - The actual code file (extension based on language)
- `<name>.meta.json` - Metadata (name, language, tags, created timestamp)

### Key components
- **CLI** (`cli.py`): Uses Click for command parsing, Rich for terminal output (syntax highlighting, tables)
- **Storage** (`storage.py`): Handles file I/O, name sanitization, language-to-extension mapping

### Supported languages
The `LANG_EXTENSIONS` dict in `storage.py` maps language names to file extensions. Supports 60+ languages including Python, JavaScript, Rust, Go, shell scripts, and more.

### Executable snippets
The `run` command can directly execute snippets in: Python, Bash, Shell, Node.js, Ruby, Perl

## Code practices

### Naming and structure
- Use descriptive variable and function names (avoid abbreviations except very common ones)
- Naming conventions: `snake_case` for variables/functions, `PascalCase` for classes
- Use PEP 585 built-in generic types (`list[str]` instead of `typing.List[str]`)
- Use `from __future__ import annotations` for Python 3.8 compatibility

### Documentation
- Write docstrings for all public functions
- Keep docstrings brief - explain what the function does
- Use clarifying inline comments for complex logic

### Code quality
- Python 3.8+ compatible
- Dependencies: click, rich, pyperclip
- Dev dependencies: pytest, pytest-cov, ruff
- Prefer well maintained libraries over custom code
- Write minimal, readable code
- Each function should do one thing clearly
- Handle errors explicitly with informative messages

## Git standards

- Make sure changes are committed on a feature or fix branch, not directly on main
- Before staging files with `git add`, review what changed with `git status` and `git diff`
- Commit after every small step - don't batch changes
- Group related changes in a single logical commit with a descriptive message
- Never add co-authorship attribution or AI-generated markers to commit messages

## Documentation standards

- Never include line numbers or line counts in documentation
- Reference files by path only, not with specific line numbers
- Always use sentence case in headings
