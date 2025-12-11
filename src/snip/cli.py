"""CLI interface for snip."""

from __future__ import annotations

import sys

import click
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from . import storage

console = Console()


@click.group()
@click.version_option()
def main():
    """Snip - A CLI tool to save, search, and retrieve code snippets."""
    pass


@main.command()
@click.argument("name")
@click.option(
    "-l",
    "--language",
    default="text",
    help="Programming language for syntax highlighting",
)
@click.option(
    "-t",
    "--tags",
    multiple=True,
    help="Tags for the snippet (can be used multiple times)",
)
def add(name: str, language: str, tags: tuple[str, ...]):
    """Add a new snippet. Reads code from stdin."""
    # Validate name
    sanitized = storage.sanitize_name(name)
    if sanitized == "unnamed":
        console.print("[red]Error: Invalid snippet name[/red]")
        console.print("[dim]Name must contain at least one alphanumeric character[/dim]")
        raise SystemExit(1)

    if sys.stdin.isatty():
        console.print("[yellow]Enter your code snippet (Ctrl+D when done):[/yellow]")

    code = sys.stdin.read()

    if not code.strip():
        console.print("[red]Error: Empty snippet[/red]")
        raise SystemExit(1)

    storage.add_snippet(name, code, language, list(tags))
    console.print(f"[green]Snippet '{name}' saved![/green]")


@main.command()
@click.argument("name")
@click.option("-c", "--copy", is_flag=True, help="Copy snippet to clipboard")
def get(name: str, copy: bool):
    """Get and display a snippet by name."""
    snippet = storage.get_snippet(name)

    if not snippet:
        console.print(f"[red]Snippet '{name}' not found[/red]")
        raise SystemExit(1)

    console.print(f"[bold cyan]{name}[/bold cyan] ({snippet['language']})")
    if snippet["tags"]:
        console.print(f"[dim]Tags: {', '.join(snippet['tags'])}[/dim]")
    console.print()

    syntax = Syntax(
        snippet["code"], snippet["language"], theme="monokai", line_numbers=True
    )
    console.print(syntax)

    if copy:
        try:
            import pyperclip

            pyperclip.copy(snippet["code"])
            console.print("\n[green]Copied to clipboard![/green]")
        except Exception:
            console.print(
                "\n[yellow]Could not copy to clipboard (pyperclip not working)[/yellow]"
            )


@main.command("list")
@click.option("-l", "--language", help="Filter by language")
@click.option("-t", "--tag", help="Filter by tag")
def list_snippets(language: str, tag: str):
    """List all saved snippets."""
    snippets = storage.list_all_snippets()

    if not snippets:
        console.print("[dim]No snippets saved yet.[/dim]")
        return

    # Apply filters
    if language:
        snippets = {
            k: v
            for k, v in snippets.items()
            if v["language"].lower() == language.lower()
        }
    if tag:
        snippets = {
            k: v
            for k, v in snippets.items()
            if tag.lower() in [t.lower() for t in v["tags"]]
        }

    if not snippets:
        console.print("[dim]No snippets match the filters.[/dim]")
        return

    table = Table(title="Saved Snippets")
    table.add_column("Name", style="cyan")
    table.add_column("Language", style="green")
    table.add_column("Tags", style="yellow")
    table.add_column("Created", style="dim")

    for name, data in snippets.items():
        created = data.get("created", "")[:10]  # Just the date part
        table.add_row(
            name,
            data["language"],
            ", ".join(data["tags"]) or "-",
            created,
        )

    console.print(table)


@main.command()
@click.argument("query")
def search(query: str):
    """Search snippets by name, language, or tag."""
    results = storage.search_snippets(query)

    if not results:
        console.print(f"[dim]No snippets matching '{query}'[/dim]")
        return

    table = Table(title=f"Search Results: '{query}'")
    table.add_column("Name", style="cyan")
    table.add_column("Language", style="green")
    table.add_column("Tags", style="yellow")

    for name, data in results.items():
        table.add_row(
            name,
            data["language"],
            ", ".join(data["tags"]) or "-",
        )

    console.print(table)
    console.print("\n[dim]Use 'snip get <name>' to view a snippet[/dim]")


@main.command()
@click.argument("name")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation")
def delete(name: str, force: bool):
    """Delete a snippet by name."""
    snippet = storage.get_snippet(name)

    if not snippet:
        console.print(f"[red]Snippet '{name}' not found[/red]")
        raise SystemExit(1)

    if not force:
        if not click.confirm(f"Delete snippet '{name}'?"):
            console.print("[dim]Cancelled[/dim]")
            return

    storage.delete_snippet(name)
    console.print(f"[green]Snippet '{name}' deleted[/green]")


@main.command("export")
@click.argument("name")
@click.argument("dest", type=click.Path(), required=False)
def export_snippet(name: str, dest: str):
    """Export a snippet to a file."""
    from pathlib import Path

    snippet = storage.get_snippet(name)

    if not snippet:
        console.print(f"[red]Snippet '{name}' not found[/red]")
        raise SystemExit(1)

    # Default destination: current dir with proper extension
    if not dest:
        ext = storage.get_extension(snippet["language"])
        dest = f"{storage.sanitize_name(name)}{ext}"

    dest_path = Path(dest)
    dest_path.write_text(snippet["code"])
    console.print(f"[green]Exported '{name}' to {dest_path}[/green]")


@main.command("import")
@click.argument("file", type=click.Path(exists=True))
@click.option("-n", "--name", help="Name for the snippet (default: filename)")
@click.option("-l", "--language", help="Language (default: detect from extension)")
@click.option("-t", "--tags", multiple=True, help="Tags for the snippet")
def import_snippet(file: str, name: str, language: str, tags: tuple[str, ...]):
    """Import a file as a snippet."""
    from pathlib import Path

    file_path = Path(file)
    code = file_path.read_text()

    # Default name from filename (without extension)
    if not name:
        name = file_path.stem

    # Validate name
    sanitized = storage.sanitize_name(name)
    if sanitized == "unnamed":
        console.print("[red]Error: Invalid snippet name[/red]")
        console.print("[dim]Name must contain at least one alphanumeric character[/dim]")
        raise SystemExit(1)

    # Detect language from extension
    if not language:
        ext = file_path.suffix.lower()
        # Reverse lookup in LANG_EXTENSIONS
        for lang, lang_ext in storage.LANG_EXTENSIONS.items():
            if lang_ext == ext:
                language = lang
                break
        else:
            language = "text"

    storage.add_snippet(name, code, language, list(tags))
    console.print(f"[green]Imported '{file_path.name}' as snippet '{name}'[/green]")


@main.command()
@click.argument("name")
@click.argument("args", nargs=-1)
def run(name: str, args: tuple[str, ...]):
    """Execute a snippet (supports python, bash, sh, zsh, node, ruby, perl)."""
    import subprocess
    import tempfile
    from pathlib import Path

    snippet = storage.get_snippet(name)

    if not snippet:
        console.print(f"[red]Snippet '{name}' not found[/red]")
        raise SystemExit(1)

    lang = snippet["language"].lower()
    code = snippet["code"]

    # Determine how to run the snippet
    runners = {
        "python": ["python3", "-c", code],
        "bash": ["bash", "-c", code],
        "shell": ["sh", "-c", code],
        "sh": ["sh", "-c", code],
        "zsh": ["zsh", "-c", code],
        "node": ["node", "-e", code],
        "javascript": ["node", "-e", code],
        "js": ["node", "-e", code],
        "ruby": ["ruby", "-e", code],
        "perl": ["perl", "-e", code],
    }

    if lang in runners:
        cmd = runners[lang]
        if args:
            # For -c style commands, args need to be passed differently
            if "-c" in cmd or "-e" in cmd:
                # Write to temp file and run with args
                ext = storage.get_extension(lang)
                try:
                    with tempfile.NamedTemporaryFile(
                        mode="w", suffix=ext, delete=False
                    ) as f:
                        f.write(code)
                        temp_path = f.name
                except OSError as e:
                    console.print(f"[red]Error creating temp file: {e}[/red]")
                    raise SystemExit(1)
                try:
                    interpreter = cmd[0]
                    result = subprocess.run([interpreter, temp_path, *args])
                    raise SystemExit(result.returncode)
                finally:
                    Path(temp_path).unlink()
            else:
                cmd.extend(args)
        result = subprocess.run(cmd)
        raise SystemExit(result.returncode)
    else:
        console.print(f"[red]Cannot execute '{lang}' snippets directly[/red]")
        console.print(
            "[dim]Supported: python, bash, sh, zsh, node/javascript/js, ruby, perl[/dim]"
        )
        raise SystemExit(1)


@main.command()
def path():
    """Show the snippets storage directory."""
    snippets_dir = storage.get_snippets_dir()
    console.print(f"{snippets_dir}")


@main.command()
@click.argument("name")
@click.option("-l", "--language", help="Change the snippet language")
@click.option("-t", "--tags", multiple=True, help="Set tags (replaces existing)")
@click.option("--add-tag", multiple=True, help="Add a tag")
@click.option("--remove-tag", multiple=True, help="Remove a tag")
def edit(
    name: str,
    language: str,
    tags: tuple[str, ...],
    add_tag: tuple[str, ...],
    remove_tag: tuple[str, ...],
):
    """Edit a snippet in your $EDITOR."""
    import os
    import subprocess

    snippet = storage.get_snippet(name)

    if not snippet:
        console.print(f"[red]Snippet '{name}' not found[/red]")
        raise SystemExit(1)

    # Handle metadata-only updates (no editor)
    if language or tags or add_tag or remove_tag:
        current_tags = snippet.get("tags", [])
        new_language = language or snippet["language"]

        # Determine new tags
        if tags:
            new_tags = list(tags)
        else:
            new_tags = current_tags.copy()
            for tag in add_tag:
                if tag not in new_tags:
                    new_tags.append(tag)
            for tag in remove_tag:
                if tag in new_tags:
                    new_tags.remove(tag)

        # If language changed, we need to rename the file
        if new_language != snippet["language"]:
            # Delete old and create new with updated language
            code = snippet["code"]
            storage.delete_snippet(name)
            storage.add_snippet(name, code, new_language, new_tags)
            console.print(f"[green]Updated '{name}' (language: {new_language})[/green]")
        else:
            # Just update metadata
            storage.update_snippet_meta(name, tags=new_tags)
            console.print(f"[green]Updated '{name}' metadata[/green]")
        return

    # Open in editor
    import shutil

    editor = os.environ.get("EDITOR", os.environ.get("VISUAL", "vi"))

    if not shutil.which(editor):
        console.print(f"[red]Editor '{editor}' not found[/red]")
        console.print("[dim]Set $EDITOR or $VISUAL to a valid editor[/dim]")
        raise SystemExit(1)

    code_path, _ = storage.find_snippet_files(name)

    if not code_path or not code_path.exists():
        console.print("[red]Snippet file not found[/red]")
        raise SystemExit(1)

    # Get file modification time before editing
    mtime_before = code_path.stat().st_mtime

    # Open editor
    result = subprocess.run([editor, str(code_path)])

    if result.returncode != 0:
        console.print("[red]Editor exited with error[/red]")
        raise SystemExit(result.returncode)

    # Check if file was modified
    mtime_after = code_path.stat().st_mtime

    if mtime_after > mtime_before:
        console.print(f"[green]Snippet '{name}' updated[/green]")
    else:
        console.print(f"[dim]No changes made to '{name}'[/dim]")


if __name__ == "__main__":
    main()
