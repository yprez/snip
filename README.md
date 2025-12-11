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

### Run a snippet

```bash
snip run hello           # Execute the snippet
snip run hello arg1 arg2 # Pass arguments
```

Supported languages: python, bash, shell, node/javascript, ruby, perl

### Export / Import

```bash
snip export hello              # Export to ./hello.py
snip export hello ~/code/      # Export to specific path
snip import script.py          # Import file as snippet
snip import script.py -n myscript -t util
```

### Delete a snippet

```bash
snip delete hello        # With confirmation
snip delete hello -f     # Force delete
```

### Show storage path

```bash
snip path                # Shows ~/.snip/snippets/
```

## Storage

Snippets are stored in `~/.snip/snippets/` as individual files:
- `<name>.<ext>` - The actual code file (e.g., `hello.py`)
- `<name>.meta.json` - Metadata (language, tags, created date)

## Development

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Future Plans

- [ ] Edit snippets in-place with `$EDITOR`
- [ ] Snippet versioning / history
- [ ] Sync snippets across machines (git-based)
- [ ] Snippet templates with variable substitution
- [ ] Shell completions (bash, zsh, fish)
