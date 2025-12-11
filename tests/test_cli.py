"""Tests for the CLI module."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from snip import storage
from snip.cli import main


@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_snippets_dir(tmp_path):
    """Create a temporary snippets directory and patch storage to use it."""
    snippets_dir = tmp_path / "snippets"
    snippets_dir.mkdir()
    with patch.object(storage, "get_snippets_dir", return_value=snippets_dir):
        yield snippets_dir


class TestMainCommand:
    """Tests for the main command group."""

    def test_help(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Snip" in result.output
        assert "add" in result.output
        assert "get" in result.output
        assert "list" in result.output

    def test_version(self, runner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output


class TestAddCommand:
    """Tests for the add command."""

    def test_add_basic_snippet(self, runner, temp_snippets_dir):
        result = runner.invoke(main, ["add", "hello", "-l", "python"], input="print('hello')\n")

        assert result.exit_code == 0
        assert "saved" in result.output.lower()
        assert (temp_snippets_dir / "hello.py").exists()

    def test_add_with_tags(self, runner, temp_snippets_dir):
        result = runner.invoke(
            main,
            ["add", "greet", "-l", "python", "-t", "util", "-t", "function"],
            input="def greet(): pass\n",
        )

        assert result.exit_code == 0
        meta = json.loads((temp_snippets_dir / "greet.meta.json").read_text())
        assert meta["tags"] == ["util", "function"]

    def test_add_empty_snippet_fails(self, runner, temp_snippets_dir):
        result = runner.invoke(main, ["add", "empty", "-l", "python"], input="\n")

        assert result.exit_code == 1
        assert "empty" in result.output.lower()

    def test_add_default_language_is_text(self, runner, temp_snippets_dir):
        result = runner.invoke(main, ["add", "note"], input="some text\n")

        assert result.exit_code == 0
        assert (temp_snippets_dir / "note.txt").exists()


class TestGetCommand:
    """Tests for the get command."""

    def test_get_existing_snippet(self, runner, temp_snippets_dir):
        storage.add_snippet("hello", "print('hello')", "python", ["test"])

        result = runner.invoke(main, ["get", "hello"])

        assert result.exit_code == 0
        assert "hello" in result.output
        assert "python" in result.output

    def test_get_nonexistent_snippet(self, runner, temp_snippets_dir):
        result = runner.invoke(main, ["get", "nonexistent"])

        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    def test_get_with_copy_flag(self, runner, temp_snippets_dir):
        storage.add_snippet("hello", "print('hello')", "python")

        # The CLI handles clipboard failures gracefully, so this should not crash
        # even if pyperclip can't access the clipboard in the test environment
        result = runner.invoke(main, ["get", "hello", "-c"])

        assert result.exit_code == 0
        assert "hello" in result.output


class TestListCommand:
    """Tests for the list command."""

    def test_list_empty(self, runner, temp_snippets_dir):
        result = runner.invoke(main, ["list"])

        assert result.exit_code == 0
        assert "no snippets" in result.output.lower()

    def test_list_multiple_snippets(self, runner, temp_snippets_dir):
        storage.add_snippet("one", "code1", "python")
        storage.add_snippet("two", "code2", "javascript")

        result = runner.invoke(main, ["list"])

        assert result.exit_code == 0
        assert "one" in result.output
        assert "two" in result.output
        assert "python" in result.output
        assert "javascript" in result.output

    def test_list_filter_by_language(self, runner, temp_snippets_dir):
        storage.add_snippet("py1", "code", "python")
        storage.add_snippet("js1", "code", "javascript")
        storage.add_snippet("py2", "code", "python")

        result = runner.invoke(main, ["list", "-l", "python"])

        assert result.exit_code == 0
        assert "py1" in result.output
        assert "py2" in result.output
        assert "js1" not in result.output

    def test_list_filter_by_tag(self, runner, temp_snippets_dir):
        storage.add_snippet("one", "code", "python", ["util"])
        storage.add_snippet("two", "code", "python", ["test"])
        storage.add_snippet("three", "code", "python", ["util"])

        result = runner.invoke(main, ["list", "-t", "util"])

        assert result.exit_code == 0
        assert "one" in result.output
        assert "three" in result.output
        assert "two" not in result.output

    def test_list_no_matches(self, runner, temp_snippets_dir):
        storage.add_snippet("test", "code", "python")

        result = runner.invoke(main, ["list", "-l", "rust"])

        assert result.exit_code == 0
        assert "no snippets match" in result.output.lower()


class TestSearchCommand:
    """Tests for the search command."""

    def test_search_finds_by_name(self, runner, temp_snippets_dir):
        storage.add_snippet("hello_world", "code", "python")
        storage.add_snippet("goodbye", "code", "python")

        result = runner.invoke(main, ["search", "hello"])

        assert result.exit_code == 0
        assert "hello_world" in result.output
        assert "goodbye" not in result.output

    def test_search_finds_by_language(self, runner, temp_snippets_dir):
        storage.add_snippet("one", "code", "rust")
        storage.add_snippet("two", "code", "python")

        result = runner.invoke(main, ["search", "rust"])

        assert result.exit_code == 0
        assert "one" in result.output

    def test_search_no_results(self, runner, temp_snippets_dir):
        storage.add_snippet("test", "code", "python")

        result = runner.invoke(main, ["search", "nonexistent"])

        assert result.exit_code == 0
        assert "no snippets matching" in result.output.lower()


class TestDeleteCommand:
    """Tests for the delete command."""

    def test_delete_with_confirmation(self, runner, temp_snippets_dir):
        storage.add_snippet("to_delete", "code", "python")

        result = runner.invoke(main, ["delete", "to_delete"], input="y\n")

        assert result.exit_code == 0
        assert "deleted" in result.output.lower()
        assert not (temp_snippets_dir / "to_delete.py").exists()

    def test_delete_cancelled(self, runner, temp_snippets_dir):
        storage.add_snippet("keep_me", "code", "python")

        result = runner.invoke(main, ["delete", "keep_me"], input="n\n")

        assert result.exit_code == 0
        assert "cancelled" in result.output.lower()
        assert (temp_snippets_dir / "keep_me.py").exists()

    def test_delete_force(self, runner, temp_snippets_dir):
        storage.add_snippet("force_delete", "code", "python")

        result = runner.invoke(main, ["delete", "force_delete", "-f"])

        assert result.exit_code == 0
        assert "deleted" in result.output.lower()

    def test_delete_nonexistent(self, runner, temp_snippets_dir):
        result = runner.invoke(main, ["delete", "nonexistent"])

        assert result.exit_code == 1
        assert "not found" in result.output.lower()


class TestExportCommand:
    """Tests for the export command."""

    def test_export_to_default_path(self, runner, temp_snippets_dir):
        storage.add_snippet("hello", "print('hello')", "python")

        with runner.isolated_filesystem():
            result = runner.invoke(main, ["export", "hello"])

            assert result.exit_code == 0
            assert "exported" in result.output.lower()
            assert Path("hello.py").exists()
            assert Path("hello.py").read_text() == "print('hello')"

    def test_export_to_custom_path(self, runner, temp_snippets_dir):
        storage.add_snippet("hello", "print('hello')", "python")

        with runner.isolated_filesystem():
            result = runner.invoke(main, ["export", "hello", "custom.py"])

            assert result.exit_code == 0
            assert Path("custom.py").exists()

    def test_export_nonexistent(self, runner, temp_snippets_dir):
        result = runner.invoke(main, ["export", "nonexistent"])

        assert result.exit_code == 1
        assert "not found" in result.output.lower()


class TestImportCommand:
    """Tests for the import command."""

    def test_import_python_file(self, runner, temp_snippets_dir):
        with runner.isolated_filesystem():
            Path("script.py").write_text("print('imported')")

            result = runner.invoke(main, ["import", "script.py"])

            assert result.exit_code == 0
            assert "imported" in result.output.lower()

            snippet = storage.get_snippet("script")
            assert snippet is not None
            assert snippet["language"] == "python"
            assert snippet["code"] == "print('imported')"

    def test_import_with_custom_name(self, runner, temp_snippets_dir):
        with runner.isolated_filesystem():
            Path("original.py").write_text("code")

            result = runner.invoke(main, ["import", "original.py", "-n", "custom_name"])

            assert result.exit_code == 0
            assert storage.get_snippet("custom_name") is not None

    def test_import_with_tags(self, runner, temp_snippets_dir):
        with runner.isolated_filesystem():
            Path("script.py").write_text("code")

            result = runner.invoke(main, ["import", "script.py", "-t", "util", "-t", "imported"])

            assert result.exit_code == 0
            snippet = storage.get_snippet("script")
            assert snippet["tags"] == ["util", "imported"]

    def test_import_detects_language_from_extension(self, runner, temp_snippets_dir):
        with runner.isolated_filesystem():
            Path("app.js").write_text("console.log('hi')")

            result = runner.invoke(main, ["import", "app.js"])

            assert result.exit_code == 0
            snippet = storage.get_snippet("app")
            assert snippet["language"] == "javascript"

    def test_import_override_language(self, runner, temp_snippets_dir):
        with runner.isolated_filesystem():
            Path("script.txt").write_text("echo hello")

            result = runner.invoke(main, ["import", "script.txt", "-l", "bash"])

            assert result.exit_code == 0
            snippet = storage.get_snippet("script")
            assert snippet["language"] == "bash"


class TestRunCommand:
    """Tests for the run command."""

    def test_run_python_snippet(self, runner, temp_snippets_dir):
        storage.add_snippet("hello", "print('hello from snippet')", "python")

        result = runner.invoke(main, ["run", "hello"])

        assert result.exit_code == 0

    def test_run_bash_snippet(self, runner, temp_snippets_dir):
        storage.add_snippet("echo_test", "echo 'bash test'", "bash")

        result = runner.invoke(main, ["run", "echo_test"])

        assert result.exit_code == 0

    def test_run_nonexistent_snippet(self, runner, temp_snippets_dir):
        result = runner.invoke(main, ["run", "nonexistent"])

        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    def test_run_unsupported_language(self, runner, temp_snippets_dir):
        storage.add_snippet("styles", "body { color: red; }", "css")

        result = runner.invoke(main, ["run", "styles"])

        assert result.exit_code == 1
        assert "cannot execute" in result.output.lower()


class TestPathCommand:
    """Tests for the path command."""

    def test_path_shows_directory(self, runner, temp_snippets_dir):
        result = runner.invoke(main, ["path"])

        assert result.exit_code == 0
        assert str(temp_snippets_dir) in result.output
