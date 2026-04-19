import pytest
from pathlib import Path
from envforge.template import (
    save_template, load_template, list_templates, delete_template, instantiate_template
)


@pytest.fixture
def tmp_template_dir(tmp_path):
    return tmp_path / "templates"


def test_save_and_load_template(tmp_template_dir):
    save_template("myapp", {"PORT": "8080", "DEBUG": "false"}, tmp_template_dir)
    tmpl = load_template("myapp", tmp_template_dir)
    assert tmpl["name"] == "myapp"
    assert tmpl["variables"]["PORT"] == "8080"
    assert tmpl["variables"]["DEBUG"] == "false"


def test_load_missing_template_raises(tmp_template_dir):
    with pytest.raises(FileNotFoundError):
        load_template("ghost", tmp_template_dir)


def test_list_templates_empty(tmp_template_dir):
    assert list_templates(tmp_template_dir) == []


def test_list_templates(tmp_template_dir):
    save_template("a", {"X": "1"}, tmp_template_dir)
    save_template("b", {"Y": "2"}, tmp_template_dir)
    result = list_templates(tmp_template_dir)
    assert set(result) == {"a", "b"}


def test_delete_template(tmp_template_dir):
    save_template("todelete", {"K": "v"}, tmp_template_dir)
    delete_template("todelete", tmp_template_dir)
    assert "todelete" not in list_templates(tmp_template_dir)


def test_delete_nonexistent_is_noop(tmp_template_dir):
    delete_template("nope", tmp_template_dir)  # should not raise


def test_instantiate_no_overrides(tmp_template_dir):
    save_template("base", {"HOST": "localhost", "PORT": "5432"}, tmp_template_dir)
    result = instantiate_template("base", base=tmp_template_dir)
    assert result == {"HOST": "localhost", "PORT": "5432"}


def test_instantiate_with_overrides(tmp_template_dir):
    save_template("base", {"HOST": "localhost", "PORT": "5432"}, tmp_template_dir)
    result = instantiate_template("base", overrides={"PORT": "9999"}, base=tmp_template_dir)
    assert result["PORT"] == "9999"
    assert result["HOST"] == "localhost"


def test_instantiate_does_not_mutate_template(tmp_template_dir):
    save_template("base", {"K": "original"}, tmp_template_dir)
    instantiate_template("base", overrides={"K": "changed"}, base=tmp_template_dir)
    tmpl = load_template("base", tmp_template_dir)
    assert tmpl["variables"]["K"] == "original"
