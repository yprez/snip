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
@click.option("-l", "--language", default="text", help="Programming language for syntax highlighting")
@click.option("-t", "--tags", multiple=True, help="Tags for the snippet (can be used multiple times)")
def add(name: str, language: str, tags: tuple[str, ...]):
    """Add a new snippet. Reads code from stdin."""
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

    syntax = Syntax(snippet["code"], snippet["language"], theme="monokai", line_numbers=True)
    console.print(syntax)

    if copy:
        try:
            import pyperclip
            pyperclip.copy(snippet["code"])
            console.print("\n[green]Copied to clipboard![/green]")
        except Exception:
            console.print("\n[yellow]Could not copy to clipboard (pyperclip not working)[/yellow]")


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
        snippets = {k: v for k, v in snippets.items() if v["language"].lower() == language.lower()}
    if tag:
        snippets = {k: v for k, v in snippets.items() if tag.lower() in [t.lower() for t in v["tags"]]}

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
    console.print(f"\n[dim]Use 'snip get <name>' to view a snippet[/dim]")


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


if __name__ == "__main__":
    main()
