# snip

A CLI tool to save, search, and retrieve code snippets.

**Why?** You have useful code snippets scattered across projects, gists, and notes. `snip` gives you a fast, local, searchable library that lives in your terminal. Snippets are stored as real files, so you can use them directly, version them with git, or sync them however you like.

## Installation

```bash
uv venv && source .venv/bin/activate
uv pip install -e .
```

## Quick Start

```bash
# Save a snippet
echo 'print("Hello, World!")' | snip add hello -l python -t example

# List your snippets
snip list

# View a snippet with syntax highlighting
snip get hello

# Run it directly
snip run hello
```

## Usage

### Add a snippet

```bash
# From stdin
echo 'console.log("hi")' | snip add greet -l javascript

# With tags
cat script.py | snip add myscript -l python -t util -t automation

# From a file (preserves language detection)
snip import existing_file.py -t imported
```

### List snippets

```bash
$ snip list
                   Saved Snippets
┏━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Name     ┃ Language   ┃ Tags            ┃ Created    ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ hello    │ python     │ example         │ 2025-12-11 │
│ greet    │ javascript │ -               │ 2025-12-11 │
│ deploy   │ bash       │ util, devops    │ 2025-12-11 │
└──────────┴────────────┴─────────────────┴────────────┘

$ snip list -l python        # Filter by language
$ snip list -t util          # Filter by tag
```

### Get a snippet

```bash
$ snip get hello
hello (python)
Tags: example

  1 print("Hello, World!")

$ snip get hello -c          # Also copy to clipboard
```

### Search snippets

```bash
$ snip search deploy
        Search Results: 'deploy'
┏━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Name   ┃ Language ┃ Tags         ┃
┡━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ deploy │ bash     │ util, devops │
└────────┴──────────┴──────────────┘
```

### Edit a snippet

```bash
snip edit hello              # Open in $EDITOR
snip edit hello -l bash      # Change language (renames file)
snip edit hello --add-tag x  # Add a tag
snip edit hello --remove-tag x
snip edit hello -t a -t b    # Replace all tags
```

### Run a snippet

```bash
snip run hello               # Execute the snippet
snip run hello arg1 arg2     # Pass arguments
```

Supported: `python`, `bash`, `shell`, `node`/`javascript`, `ruby`, `perl`

### Export / Import

```bash
# Export to use elsewhere
snip export hello              # Creates ./hello.py
snip export hello ~/scripts/   # Export to specific path

# Import existing files
snip import script.py                    # Auto-detects language
snip import script.py -n myscript -t util
```

### Other commands

```bash
snip delete hello        # Delete (with confirmation)
snip delete hello -f     # Force delete
snip path                # Show storage directory
```

## Storage

Snippets live in `~/.snip/snippets/` as plain files:

```
~/.snip/snippets/
├── hello.py           # The actual code
├── hello.meta.json    # Metadata (language, tags, created)
├── deploy.sh
└── deploy.meta.json
```

This means you can:
- Use snippets directly (`python ~/.snip/snippets/hello.py`)
- Back them up or sync with git/rsync/Dropbox
- Edit them with any tool

## Development

```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

pytest                  # Run tests
pytest --cov=snip       # With coverage
ruff check src tests    # Lint
ruff format src tests   # Format
```

## Possible next steps

- Package for PyPI/pipx with a proper `pyproject.toml`, metadata, and CLI entry points
- Improve `snip edit` ergonomics (better `$EDITOR` integration and workflows)
- Allow language changes during edit and rename files accordingly
- Support tag operations: add, remove, and replace
- Add overwrite protection on `snip add` with `--force`
- Load defaults and themes from `~/.snip/config.toml`
- Provide sorting and limiting options in `snip list`
- Add fuzzy search via `snip search -f`
- Offer an interactive picker (`snip pick`) with optional `fzf` integration
- Add a snippet rename command
- Track snippet history and versions with automatic backups on overwrite
- Add `snip log`, `snip show`, and `snip diff`
- Support optional git-based sync in the snippets directory
- Provide snippet templates and `snip new`
- Add shell completions for bash, zsh, and fish
