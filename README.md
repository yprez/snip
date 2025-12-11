# snip

A CLI tool to save, search, and retrieve code snippets.

## Installation

```bash
uv venv
uv pip install -e .
```

## Usage

### Add a snippet

```bash
# From stdin
echo 'print("Hello")' | snip add hello -l python -t greeting

# Multiple tags
cat myfile.py | snip add mysnippet -l python -t util -t helper
```

### List snippets

```bash
snip list
snip list -l python      # Filter by language
snip list -t util        # Filter by tag
```

### Get a snippet

```bash
snip get hello           # Display snippet
snip get hello -c        # Copy to clipboard
```

### Search snippets

```bash
snip search python       # Search by name, language, or tag
```

### Delete a snippet

```bash
snip delete hello        # With confirmation
snip delete hello -f     # Force delete
```

## Storage

Snippets are stored in `~/.snip/snippets.json`.

## Development

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```
