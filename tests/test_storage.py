"""Tests for the storage module."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from snip import storage


@pytest.fixture
def temp_snippets_dir(tmp_path):
    """Create a temporary snippets directory and patch storage to use it."""
    snippets_dir = tmp_path / "snippets"
    snippets_dir.mkdir()
    with patch.object(storage, "get_snippets_dir", return_value=snippets_dir):
        yield snippets_dir


class TestGetExtension:
    """Tests for get_extension function."""

    def test_known_languages(self):
        assert storage.get_extension("python") == ".py"
        assert storage.get_extension("javascript") == ".js"
        assert storage.get_extension("rust") == ".rs"
        assert storage.get_extension("go") == ".go"
        assert storage.get_extension("bash") == ".sh"

    def test_case_insensitive(self):
        assert storage.get_extension("Python") == ".py"
        assert storage.get_extension("PYTHON") == ".py"
        assert storage.get_extension("JavaScript") == ".js"

    def test_unknown_language_defaults_to_txt(self):
        assert storage.get_extension("unknown") == ".txt"
        assert storage.get_extension("foobar") == ".txt"


class TestSanitizeName:
    """Tests for sanitize_name function."""

    def test_normal_names(self):
        assert storage.sanitize_name("hello") == "hello"
        assert storage.sanitize_name("my_snippet") == "my_snippet"
        assert storage.sanitize_name("test-123") == "test-123"

    def test_removes_problematic_characters(self):
        assert storage.sanitize_name("test<>file") == "test__file"
        assert storage.sanitize_name("path/to\\file") == "path_to_file"
        assert storage.sanitize_name("file:name") == "file_name"
        assert storage.sanitize_name("test?*file") == "test__file"

    def test_removes_leading_trailing_dots_and_spaces(self):
        assert storage.sanitize_name("...test") == "test"
        assert storage.sanitize_name("test...") == "test"
        assert storage.sanitize_name("  test  ") == "test"
        assert storage.sanitize_name("..test..") == "test"

    def test_empty_name_becomes_unnamed(self):
        assert storage.sanitize_name("") == "unnamed"
        assert storage.sanitize_name("...") == "unnamed"
        assert storage.sanitize_name("   ") == "unnamed"


class TestAddSnippet:
    """Tests for add_snippet function."""

    def test_add_basic_snippet(self, temp_snippets_dir):
        storage.add_snippet("hello", "print('hello')", "python")

        code_path = temp_snippets_dir / "hello.py"
        meta_path = temp_snippets_dir / "hello.meta.json"

        assert code_path.exists()
        assert meta_path.exists()
        assert code_path.read_text() == "print('hello')"

        meta = json.loads(meta_path.read_text())
        assert meta["name"] == "hello"
        assert meta["language"] == "python"
        assert meta["tags"] == []
        assert "created" in meta

    def test_add_snippet_with_tags(self, temp_snippets_dir):
        storage.add_snippet(
            "greet", "def greet(): pass", "python", ["util", "function"]
        )

        meta_path = temp_snippets_dir / "greet.meta.json"
        meta = json.loads(meta_path.read_text())

        assert meta["tags"] == ["util", "function"]

    def test_add_snippet_different_languages(self, temp_snippets_dir):
        storage.add_snippet("script", "echo hello", "bash")
        storage.add_snippet("app", "console.log('hi')", "javascript")

        assert (temp_snippets_dir / "script.sh").exists()
        assert (temp_snippets_dir / "app.js").exists()

    def test_add_snippet_overwrites_existing(self, temp_snippets_dir):
        storage.add_snippet("test", "original", "python")
        storage.add_snippet("test", "updated", "python")

        code_path = temp_snippets_dir / "test.py"
        assert code_path.read_text() == "updated"

    def test_add_snippet_with_special_characters_in_name(self, temp_snippets_dir):
        storage.add_snippet("my/test:snippet", "code", "python")

        # Name should be sanitized
        assert (temp_snippets_dir / "my_test_snippet.py").exists()
        assert (temp_snippets_dir / "my_test_snippet.meta.json").exists()


class TestGetSnippet:
    """Tests for get_snippet function."""

    def test_get_existing_snippet(self, temp_snippets_dir):
        storage.add_snippet("hello", "print('hello')", "python", ["test"])

        snippet = storage.get_snippet("hello")

        assert snippet is not None
        assert snippet["name"] == "hello"
        assert snippet["language"] == "python"
        assert snippet["code"] == "print('hello')"
        assert snippet["tags"] == ["test"]

    def test_get_nonexistent_snippet(self, temp_snippets_dir):
        snippet = storage.get_snippet("nonexistent")
        assert snippet is None

    def test_get_snippet_with_missing_code_file(self, temp_snippets_dir):
        # Create only metadata file
        meta_path = temp_snippets_dir / "broken.meta.json"
        meta_path.write_text(
            json.dumps({"name": "broken", "language": "python", "tags": []})
        )

        snippet = storage.get_snippet("broken")

        assert snippet is not None
        assert snippet["code"] == ""


class TestDeleteSnippet:
    """Tests for delete_snippet function."""

    def test_delete_existing_snippet(self, temp_snippets_dir):
        storage.add_snippet("to_delete", "code", "python")

        result = storage.delete_snippet("to_delete")

        assert result is True
        assert not (temp_snippets_dir / "to_delete.py").exists()
        assert not (temp_snippets_dir / "to_delete.meta.json").exists()

    def test_delete_nonexistent_snippet(self, temp_snippets_dir):
        result = storage.delete_snippet("nonexistent")
        assert result is False

    def test_delete_snippet_with_only_meta(self, temp_snippets_dir):
        # Create only metadata
        meta_path = temp_snippets_dir / "orphan.meta.json"
        meta_path.write_text(
            json.dumps({"name": "orphan", "language": "python", "tags": []})
        )

        result = storage.delete_snippet("orphan")

        assert result is True
        assert not meta_path.exists()


class TestUpdateSnippetMeta:
    """Tests for update_snippet_meta function."""

    def test_update_tags(self, temp_snippets_dir):
        storage.add_snippet("test", "code", "python", ["old"])

        result = storage.update_snippet_meta("test", tags=["new1", "new2"])

        assert result is True
        snippet = storage.get_snippet("test")
        assert snippet["tags"] == ["new1", "new2"]

    def test_update_nonexistent_returns_false(self, temp_snippets_dir):
        result = storage.update_snippet_meta("nonexistent", tags=["tag"])
        assert result is False

    def test_update_preserves_other_metadata(self, temp_snippets_dir):
        storage.add_snippet("test", "code", "python", ["old"])

        storage.update_snippet_meta("test", tags=["new"])

        snippet = storage.get_snippet("test")
        assert snippet["name"] == "test"
        assert snippet["language"] == "python"
        assert "created" in snippet


class TestListAllSnippets:
    """Tests for list_all_snippets function."""

    def test_list_empty(self, temp_snippets_dir):
        snippets = storage.list_all_snippets()
        assert snippets == {}

    def test_list_multiple_snippets(self, temp_snippets_dir):
        storage.add_snippet("one", "code1", "python")
        storage.add_snippet("two", "code2", "javascript")
        storage.add_snippet("three", "code3", "bash")

        snippets = storage.list_all_snippets()

        assert len(snippets) == 3
        assert "one" in snippets
        assert "two" in snippets
        assert "three" in snippets

    def test_list_does_not_include_code(self, temp_snippets_dir):
        storage.add_snippet("test", "some code here", "python")

        snippets = storage.list_all_snippets()

        # list_all_snippets only loads metadata, not code
        assert "code" not in snippets["test"]


class TestSearchSnippets:
    """Tests for search_snippets function."""

    def test_search_by_name(self, temp_snippets_dir):
        storage.add_snippet("hello_world", "code", "python")
        storage.add_snippet("goodbye", "code", "python")

        results = storage.search_snippets("hello")

        assert len(results) == 1
        assert "hello_world" in results

    def test_search_by_language(self, temp_snippets_dir):
        storage.add_snippet("one", "code", "python")
        storage.add_snippet("two", "code", "javascript")
        storage.add_snippet("three", "code", "python")

        results = storage.search_snippets("python")

        assert len(results) == 2
        assert "one" in results
        assert "three" in results

    def test_search_by_tag(self, temp_snippets_dir):
        storage.add_snippet("one", "code", "python", ["util", "helper"])
        storage.add_snippet("two", "code", "python", ["test"])
        storage.add_snippet("three", "code", "python", ["util"])

        results = storage.search_snippets("util")

        assert len(results) == 2
        assert "one" in results
        assert "three" in results

    def test_search_case_insensitive(self, temp_snippets_dir):
        storage.add_snippet("MySnippet", "code", "Python", ["UTIL"])

        assert len(storage.search_snippets("mysnippet")) == 1
        assert len(storage.search_snippets("python")) == 1
        assert len(storage.search_snippets("util")) == 1

    def test_search_no_results(self, temp_snippets_dir):
        storage.add_snippet("test", "code", "python")

        results = storage.search_snippets("nonexistent")

        assert results == {}


class TestGetSnippetPaths:
    """Tests for get_snippet_paths function."""

    def test_paths_for_python(self, temp_snippets_dir):
        code_path, meta_path = storage.get_snippet_paths("test", "python")

        assert code_path == temp_snippets_dir / "test.py"
        assert meta_path == temp_snippets_dir / "test.meta.json"

    def test_paths_for_javascript(self, temp_snippets_dir):
        code_path, meta_path = storage.get_snippet_paths("app", "javascript")

        assert code_path == temp_snippets_dir / "app.js"
        assert meta_path == temp_snippets_dir / "app.meta.json"

    def test_paths_sanitize_name(self, temp_snippets_dir):
        code_path, meta_path = storage.get_snippet_paths("bad/name", "python")

        assert code_path == temp_snippets_dir / "bad_name.py"
        assert meta_path == temp_snippets_dir / "bad_name.meta.json"
