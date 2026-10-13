from __future__ import annotations

import sys
from pathlib import Path

import pytest
from devkit.core import PluginFailure, iter_plugin_files, load_subclasses
from devkit.core.plugins import module_name

# The base class plugin files subclass; they import it from this test module.
BASE_MODULE = "devkit.core_test_plugin_base"


class Base:
    name = "base"


class Other:
    pass


@pytest.fixture(autouse=True)
def _base_module(monkeypatch: pytest.MonkeyPatch) -> None:
    module = type(sys)(BASE_MODULE)
    module.Base = Base  # type: ignore[attr-defined]
    module.Other = Other  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, BASE_MODULE, module)


def plugin(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"from {BASE_MODULE} import Base, Other\n\n{body}")
    return path


def test_loads_defined_concrete_subclasses_in_definition_order(tmp_path: Path) -> None:
    path = plugin(
        tmp_path,
        "rules.py",
        "import abc\n"
        "class Zeta(Base):\n    name = 'zeta'\n"
        "class Alpha(Base):\n    name = 'alpha'\n"
        "class NotAPlugin(Other):\n    pass\n"
        "class Abstract(Base, abc.ABC):\n    @abc.abstractmethod\n    def run(self): ...\n"
        "class Concrete(Abstract):\n    name = 'concrete'\n    def run(self): return 1\n",
    )
    result = load_subclasses([path], Base, namespace="test_plugin")
    assert result.errors == ()
    assert [p.name for p in result.instances] == ["zeta", "alpha", "concrete"]
    assert all(p.path == path for p in result.plugins)
    assert module_name(path, "test_plugin") in sys.modules
    sys.modules.pop(module_name(path, "test_plugin"))


def test_imported_classes_and_the_base_are_ignored(tmp_path: Path) -> None:
    plugin(tmp_path, "lib/shared.py", "class Shared(Base):\n    name = 'shared'\n")
    sys.path.insert(0, str(tmp_path / "lib"))
    try:
        path = plugin(tmp_path, "uses.py", "from shared import Shared\nclass Own(Base):\n    name = 'own'\n")
        result = load_subclasses([path], Base, namespace="test_plugin")
    finally:
        sys.path.remove(str(tmp_path / "lib"))
        sys.modules.pop("shared", None)
    assert [p.name for p in result.instances] == ["own"]
    sys.modules.pop(module_name(path, "test_plugin"))


def test_failing_file_is_atomic_and_leaves_no_module(tmp_path: Path) -> None:
    good = plugin(tmp_path, "good.py", "class Good(Base):\n    name = 'good'\n")
    bad = plugin(
        tmp_path,
        "bad.py",
        "class First(Base):\n    name = 'first'\n"
        "class Broken(Base):\n    def __init__(self):\n        raise RuntimeError('cannot build')\n",
    )
    crash = plugin(tmp_path, "crash.py", "raise ValueError('import failed')\n")
    result = load_subclasses([bad, good, crash], Base, namespace="test_plugin")
    assert [p.name for p in result.instances] == ["good"]
    assert result.errors == (
        PluginFailure(bad, "cannot build"),
        PluginFailure(crash, "import failed"),
    )
    assert str(result.errors[0]) == f"{bad}: cannot build"
    assert module_name(bad, "test_plugin") not in sys.modules
    assert module_name(crash, "test_plugin") not in sys.modules
    sys.modules.pop(module_name(good, "test_plugin"))


def test_validation_failure_rejects_the_whole_file(tmp_path: Path) -> None:
    path = plugin(tmp_path, "v.py", "class A(Base):\n    name = 'ok'\nclass B(Base):\n    name = 'Bad Name'\n")

    def validate(instance: Base) -> None:
        if " " in instance.name:
            raise ValueError(f"invalid name {instance.name!r}")

    result = load_subclasses([path], Base, namespace="test_plugin", validate=validate)
    assert result.instances == ()
    assert result.errors == (PluginFailure(path, "invalid name 'Bad Name'"),)
    assert module_name(path, "test_plugin") not in sys.modules


def test_failure_restores_a_previously_loaded_module(tmp_path: Path) -> None:
    path = plugin(tmp_path, "p.py", "class A(Base):\n    name = 'v1'\n")
    first = load_subclasses([path], Base, namespace="test_plugin")
    name = module_name(path, "test_plugin")
    loaded = sys.modules[name]
    path.write_text("raise SystemExit(3)\n")
    second = load_subclasses([path], Base, namespace="test_plugin")
    assert [p.name for p in first.instances] == ["v1"]
    assert second.instances == () and second.errors == (PluginFailure(path, "3"),)
    assert sys.modules[name] is loaded
    sys.modules.pop(name)


def test_exception_without_message_reports_its_type(tmp_path: Path) -> None:
    path = plugin(tmp_path, "e.py", "raise KeyError\n")
    assert load_subclasses([path], Base, namespace="test_plugin").errors == (PluginFailure(path, "KeyError"),)


def test_non_python_and_missing_files(tmp_path: Path) -> None:
    text = tmp_path / "notes.txt"
    text.write_text("x")
    missing = tmp_path / "missing.py"
    result = load_subclasses([text, missing], Base, namespace="test_plugin")
    assert result.instances == ()
    assert [e.path for e in result.errors] == [text, missing]
    assert "cannot be loaded" in result.errors[0].message


def test_keyboard_interrupt_propagates_after_cleanup(tmp_path: Path) -> None:
    path = plugin(tmp_path, "k.py", "raise KeyboardInterrupt\n")
    with pytest.raises(KeyboardInterrupt):
        load_subclasses([path], Base, namespace="test_plugin")
    assert module_name(path, "test_plugin") not in sys.modules


def test_namespace_must_be_an_identifier(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="identifier"):
        load_subclasses([], Base, namespace="not-valid")


def test_module_name_is_stable_and_path_based(tmp_path: Path) -> None:
    a = tmp_path / "a.py"
    assert module_name(a, "ns") == module_name(tmp_path / "." / "a.py", "ns")
    assert module_name(a, "ns") != module_name(tmp_path / "b.py", "ns")
    assert module_name(a, "ns").startswith("ns_") and len(module_name(a, "ns")) == len("ns_") + 16


def test_iter_plugin_files(tmp_path: Path) -> None:
    for rel in [
        "b.py",
        "a.py",
        "_private.py",
        ".hidden.py",
        "__init__.py",
        "sub/c.py",
        "sub/_skip.py",
        "_internal/d.py",
        ".cache/e.py",
        "__pycache__/f.py",
        "notes.md",
    ]:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("")
    (tmp_path / "dir.py").mkdir()
    assert [p.relative_to(tmp_path).as_posix() for p in iter_plugin_files(tmp_path)] == ["a.py", "b.py", "sub/c.py"]
    assert iter_plugin_files(tmp_path / "missing") == []
    assert iter_plugin_files(tmp_path / "a.py") == []


def test_file_without_plugins_loads_nothing(tmp_path: Path) -> None:
    path = plugin(tmp_path, "empty.py", "VALUE = 1\n")
    result = load_subclasses([path], Base, namespace="test_plugin", validate=lambda instance: None)
    assert result.instances == () and result.errors == ()
    sys.modules.pop(module_name(path, "test_plugin"))


def test_loading_writes_no_bytecode_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "dont_write_bytecode", False)
    monkeypatch.delenv("PYTHONPYCACHEPREFIX", raising=False)
    monkeypatch.setattr(sys, "pycache_prefix", None)
    path = plugin(tmp_path / "managed", "cached.py", "class Cached(Base):\n    name = 'cached'\n")
    result = load_subclasses([path], Base, namespace="test_plugin")
    assert [p.name for p in result.instances] == ["cached"]
    assert not (path.parent / "__pycache__").exists()
    sys.modules.pop(module_name(path, "test_plugin"))
