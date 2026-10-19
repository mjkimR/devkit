from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from devkit.core import PluginFailure, PluginPackage, iter_plugin_packages, load_subclasses
from devkit.core.plugins import check_plugin_modules, module_name, plugin_module_name, plugin_modules

# The base class plugin modules subclass; they import it from this test module.
BASE_MODULE = "devkit.core_test_plugin_base"
NAMESPACE = "test_plugin"


class Base:
    name = "base"


class Other:
    pass


@pytest.fixture(autouse=True)
def _base_module(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    module = type(sys)(BASE_MODULE)
    module.Base = Base  # type: ignore[attr-defined]
    module.Other = Other  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, BASE_MODULE, module)
    finders = list(sys.meta_path)
    modules = set(sys.modules)
    yield
    sys.meta_path[:] = finders
    for name in set(sys.modules) - modules:
        if name.startswith(f"{NAMESPACE}_"):
            del sys.modules[name]


def write(root: Path, files: dict[str, str]) -> Path:
    for rel, body in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"from {BASE_MODULE} import Base, Other\n\n{body}")
    return root


def package(root: Path, files: dict[str, str] | None = None) -> PluginPackage:
    return PluginPackage.from_directory(write(root, files or {}))


def name_of(pkg: PluginPackage) -> str:
    return module_name(pkg.key, NAMESPACE)


def finder_names() -> list[str]:
    return [getattr(finder, "name", "") for finder in sys.meta_path]


def test_loads_defined_concrete_subclasses_in_definition_order(tmp_path: Path) -> None:
    pkg = package(
        tmp_path / "p",
        {
            "rules.py": "import abc\n"
            "class Zeta(Base):\n    name = 'zeta'\n"
            "class Alpha(Base):\n    name = 'alpha'\n"
            "class NotAPlugin(Other):\n    pass\n"
            "class Abstract(Base, abc.ABC):\n    @abc.abstractmethod\n    def run(self): ...\n"
            "class Concrete(Abstract):\n    name = 'concrete'\n    def run(self): return 1\n",
        },
    )
    result = load_subclasses([pkg], Base, namespace=NAMESPACE)
    assert result.errors == ()
    assert [p.name for p in result.instances] == ["zeta", "alpha", "concrete"]
    assert all(p.path == tmp_path / "p/rules.py" and p.package is pkg for p in result.plugins)
    assert f"{name_of(pkg)}.rules" in sys.modules
    assert type(result.instances[0]).__module__ == f"{name_of(pkg)}.rules"


def test_modules_load_packages_first_then_submodules_and_classes_count_once(tmp_path: Path) -> None:
    pkg = package(
        tmp_path / "p",
        {
            "__init__.py": "from .b import B\nclass Init(Base):\n    name = 'init'\n",
            "b.py": "class B(Base):\n    name = 'b'\n",
            "a.py": "from .b import B\nclass A(Base):\n    name = 'a'\n",
            "sub/c.py": "class C(Base):\n    name = 'c'\n",
        },
    )
    assert list(pkg.modules) == ["", "a", "b", "sub.c"]
    result = load_subclasses([pkg], Base, namespace=NAMESPACE)
    assert result.errors == ()
    assert [p.name for p in result.instances] == ["init", "a", "b", "c"]  # B is defined in b, counted once


def test_relative_imports_including_lazy_ones_at_run_time(tmp_path: Path) -> None:
    pkg = package(
        tmp_path / "p",
        {
            "rule.py": "from .helpers import parse\n"
            "class R(Base):\n"
            "    name = parse('r')\n"
            "    def later(self):\n"
            "        from .sub.deep import value\n"
            "        return value()\n",
            "helpers.py": "def parse(text):\n    return text.upper()\n",
            "sub/deep.py": "from ..helpers import parse\ndef value():\n    return parse('deep')\n",
        },
    )
    result = load_subclasses([pkg], Base, namespace=NAMESPACE)
    assert result.errors == ()
    (rule,) = result.instances
    assert rule.name == "R"
    sys.modules.pop(f"{name_of(pkg)}.sub.deep")
    assert rule.later() == "DEEP"  # type: ignore[attr-defined]


def test_package_without_init_has_an_empty_package_module(tmp_path: Path) -> None:
    pkg = package(tmp_path / "p", {"only.py": "class Only(Base):\n    name = 'only'\n"})
    result = load_subclasses([pkg], Base, namespace=NAMESPACE)
    assert [p.name for p in result.instances] == ["only"]
    root = sys.modules[name_of(pkg)]
    assert root.__path__ == []  # type: ignore[attr-defined]
    assert not hasattr(root, "__file__") or root.__file__ is None


def test_test_files_hidden_entries_and_caches_are_not_modules(tmp_path: Path) -> None:
    pkg = package(
        tmp_path / "p",
        {
            "rule.py": "class R(Base):\n    name = 'r'\n",
            "test_rule.py": "raise RuntimeError('a test was imported')\n",
            "rule_test.py": "raise RuntimeError('a test was imported')\n",
            "tests/conftest.py": "raise RuntimeError('a test was imported')\n",
            "tests/helpers.py": "raise RuntimeError('a test was imported')\n",
            ".hidden.py": "raise RuntimeError('hidden')\n",
            ".cache/x.py": "raise RuntimeError('hidden')\n",
            "__pycache__/y.py": "raise RuntimeError('cache')\n",
            "_private.py": "VALUE = 1\n",
        },
    )
    assert list(pkg.modules) == ["_private", "rule"]
    assert [p.name for p in load_subclasses([pkg], Base, namespace=NAMESPACE).instances] == ["r"]


def test_plugin_module_name() -> None:
    assert plugin_module_name("__init__.py") == ""
    assert plugin_module_name("a/__init__.py") == "a"
    assert plugin_module_name("a/b.py") == "a.b"
    assert plugin_module_name("tests.py") == "tests"
    for rel in (
        "a.md",
        "tests/a.py",
        "a/tests/b.py",
        "test_a.py",
        "a_test.py",
        ".a.py",
        "a/.b/c.py",
        "__pycache__/a.py",
    ):
        assert plugin_module_name(rel) is None, rel


def test_an_unlisted_sibling_file_cannot_be_imported(tmp_path: Path) -> None:
    root = write(
        tmp_path / "p",
        {
            "rule.py": "class R(Base):\n    name = 'r'\n    def run(self):\n        from . import sibling\n",
            "sibling.py": "VALUE = 1\n",
        },
    )
    pkg = PluginPackage("only-rule", root, plugin_modules([("rule", root / "rule.py")]))
    result = load_subclasses([pkg], Base, namespace=NAMESPACE)
    (rule,) = result.instances
    with pytest.raises(ImportError):
        rule.run()  # type: ignore[attr-defined]

    importer = PluginPackage(
        "imports", root, plugin_modules([("", write(tmp_path / "i", {"x.py": "from . import y\n"}) / "x.py")])
    )
    failed = load_subclasses([importer], Base, namespace=NAMESPACE)
    assert failed.instances == () and "y" in failed.errors[0].message


def test_one_package_may_mix_files_from_several_trees(tmp_path: Path) -> None:
    write(tmp_path / "managed", {"rule.py": "from .helpers import NAME\nclass R(Base):\n    name = NAME\n"})
    write(tmp_path / "managed", {"helpers.py": "NAME = 'managed'\n"})
    write(tmp_path / "overrides", {"helpers.py": "NAME = 'override'\n"})
    pkg = PluginPackage(
        "split",
        tmp_path / "managed",
        plugin_modules([("rule", tmp_path / "managed/rule.py"), ("helpers", tmp_path / "overrides/helpers.py")]),
    )
    result = load_subclasses([pkg], Base, namespace=NAMESPACE)
    assert [p.name for p in result.instances] == ["override"]
    assert result.plugins[0].path == tmp_path / "managed/rule.py"


def test_failing_package_is_atomic_and_cleans_modules_and_finder(tmp_path: Path) -> None:
    good = package(tmp_path / "good", {"good.py": "class Good(Base):\n    name = 'good'\n"})
    bad = package(
        tmp_path / "bad",
        {
            "first.py": "class First(Base):\n    name = 'first'\n",
            "second.py": "class Broken(Base):\n    def __init__(self):\n        raise RuntimeError('cannot build')\n",
        },
    )
    crash = package(tmp_path / "crash", {"ok.py": "VALUE = 1\n", "z.py": "raise ValueError('import failed')\n"})
    result = load_subclasses([bad, good, crash], Base, namespace=NAMESPACE)
    assert [p.name for p in result.instances] == ["good"]
    assert result.errors == (
        PluginFailure(tmp_path / "bad", "cannot build"),
        PluginFailure(tmp_path / "crash", "import failed"),
    )
    assert str(result.errors[0]) == f"{tmp_path / 'bad'}: cannot build"
    for failed in (bad, crash):
        assert not [m for m in sys.modules if m.startswith(name_of(failed))]
        assert name_of(failed) not in finder_names()
    assert name_of(good) in finder_names()


def test_validation_failure_rejects_the_whole_package(tmp_path: Path) -> None:
    pkg = package(
        tmp_path / "v", {"a.py": "class A(Base):\n    name = 'ok'\n", "b.py": "class B(Base):\n    name = 'Bad Name'\n"}
    )

    def validate(instance: Base) -> None:
        if " " in instance.name:
            raise ValueError(f"invalid name {instance.name!r}")

    result = load_subclasses([pkg], Base, namespace=NAMESPACE, validate=validate)
    assert result.instances == ()
    assert result.errors == (PluginFailure(tmp_path / "v", "invalid name 'Bad Name'"),)
    assert name_of(pkg) not in sys.modules and name_of(pkg) not in finder_names()


def test_failure_restores_a_previously_loaded_package(tmp_path: Path) -> None:
    pkg = package(tmp_path / "p", {"p.py": "class A(Base):\n    name = 'v1'\n"})
    first = load_subclasses([pkg], Base, namespace=NAMESPACE)
    name = name_of(pkg)
    loaded = sys.modules[f"{name}.p"]
    (tmp_path / "p/p.py").write_text("raise SystemExit(3)\n")
    second = load_subclasses([pkg], Base, namespace=NAMESPACE)
    assert [p.name for p in first.instances] == ["v1"]
    assert second.instances == () and second.errors == (PluginFailure(tmp_path / "p", "3"),)
    assert sys.modules[f"{name}.p"] is loaded
    assert finder_names().count(name) == 1


def test_reloading_a_package_replaces_its_modules_and_finder(tmp_path: Path) -> None:
    pkg = package(tmp_path / "p", {"p.py": "class A(Base):\n    name = 'v1'\n"})
    load_subclasses([pkg], Base, namespace=NAMESPACE)
    (tmp_path / "p/p.py").write_text(f"from {BASE_MODULE} import Base\nclass A(Base):\n    name = 'v2'\n")
    again = load_subclasses([pkg], Base, namespace=NAMESPACE)
    assert [p.name for p in again.instances] == ["v2"]
    assert finder_names().count(name_of(pkg)) == 1


def test_two_packages_never_share_module_names(tmp_path: Path) -> None:
    a = package(tmp_path / "a", {"rule.py": "class A(Base):\n    name = 'a'\n"})
    b = package(tmp_path / "b", {"rule.py": "class B(Base):\n    name = 'b'\n"})
    result = load_subclasses([a, b, a], Base, namespace=NAMESPACE)
    assert [p.name for p in result.instances] == ["a", "b"]
    assert name_of(a) != name_of(b)
    assert result.errors == (PluginFailure(tmp_path / "a", f"duplicate plugin package {a.key}"),)


def test_exception_without_message_reports_its_type(tmp_path: Path) -> None:
    pkg = package(tmp_path / "e", {"e.py": "raise KeyError\n"})
    assert load_subclasses([pkg], Base, namespace=NAMESPACE).errors == (PluginFailure(tmp_path / "e", "KeyError"),)


def test_missing_files_and_bad_module_names_fail_the_package(tmp_path: Path) -> None:
    missing = PluginPackage("missing", None, plugin_modules([("gone", tmp_path / "gone.py")]))
    text = tmp_path / "notes.txt"
    text.write_text("x")
    wrong = PluginPackage("wrong", tmp_path, plugin_modules([("notes", text)]))
    hyphen = package(tmp_path / "h", {"my-helper.py": "VALUE = 1\n"})
    result = load_subclasses([missing, wrong, hyphen], Base, namespace=NAMESPACE)
    assert result.instances == ()
    assert [e.path for e in result.errors] == [Path("missing"), tmp_path, tmp_path / "h"]
    assert "not a Python file" in result.errors[1].message
    assert "not an importable module name" in result.errors[2].message


def test_module_file_beside_its_package_directory_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="both define module a"):
        check_plugin_modules({"a": tmp_path / "a.py", "a.b": tmp_path / "a/b.py"})
    with pytest.raises(ValueError, match="both define module a"):
        plugin_modules([("a", tmp_path / "a.py"), ("a", tmp_path / "a/__init__.py")])
    check_plugin_modules({"a": tmp_path / "a/__init__.py", "a.b": tmp_path / "a/b.py"})


def test_keyboard_interrupt_propagates_after_cleanup(tmp_path: Path) -> None:
    pkg = package(tmp_path / "k", {"k.py": "raise KeyboardInterrupt\n"})
    with pytest.raises(KeyboardInterrupt):
        load_subclasses([pkg], Base, namespace=NAMESPACE)
    assert name_of(pkg) not in sys.modules and name_of(pkg) not in finder_names()


def test_namespace_must_be_an_identifier() -> None:
    with pytest.raises(ValueError, match="identifier"):
        load_subclasses([], Base, namespace="not-valid")


def test_module_name_is_stable_and_key_based() -> None:
    assert module_name("a", "ns") == module_name("a", "ns")
    assert module_name("a", "ns") != module_name("b", "ns")
    assert module_name("a", "ns").startswith("ns_") and len(module_name("a", "ns")) == len("ns_") + 16


def test_iter_plugin_packages(tmp_path: Path) -> None:
    for rel in [
        "b/rule.py",
        "a/rule.py",
        "a/notes.md",
        "_private/x.py",
        ".hidden/x.py",
        "__pycache__/x.py",
        "empty/README.md",
        "tests/conftest.py",
        "_helpers.py",
        ".hidden.py",
        "test_loose.py",
        "notes.md",
        "loose.py",
    ]:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("")
    packages, failures = iter_plugin_packages(tmp_path)
    assert [p.root for p in packages] == [tmp_path / "a", tmp_path / "b", tmp_path / "empty"]
    assert packages[0].key == str((tmp_path / "a").resolve())
    assert dict(packages[0].modules) == {"rule": tmp_path / "a/rule.py"}
    assert [f.path for f in failures] == [tmp_path / "loose.py"]
    assert failures[0].fix == f"Move {(tmp_path / 'loose.py').as_posix()} into {tmp_path.as_posix()}/loose/"
    assert iter_plugin_packages(tmp_path / "missing") == ((), ())
    assert iter_plugin_packages(tmp_path / "loose.py") == ((), ())


def test_iter_plugin_packages_reports_a_package_with_two_files_for_one_module(tmp_path: Path) -> None:
    write(tmp_path / "p", {"a.py": "", "a/__init__.py": ""})
    packages, failures = iter_plugin_packages(tmp_path)
    assert packages == () and [f.path for f in failures] == [tmp_path / "p"]
    assert "both define module a" in failures[0].message


def test_package_without_plugins_loads_nothing(tmp_path: Path) -> None:
    pkg = package(tmp_path / "p", {"empty.py": "VALUE = 1\n"})
    result = load_subclasses([pkg], Base, namespace=NAMESPACE, validate=lambda instance: None)
    assert result.instances == () and result.errors == ()


def test_loading_writes_no_bytecode_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "dont_write_bytecode", False)
    monkeypatch.delenv("PYTHONPYCACHEPREFIX", raising=False)
    monkeypatch.setattr(sys, "pycache_prefix", None)
    pkg = package(
        tmp_path / "managed",
        {
            "__init__.py": "",
            "cached.py": "from .sub import x\nclass Cached(Base):\n    name = 'cached'\n",
            "sub/x.py": "",
        },
    )
    result = load_subclasses([pkg], Base, namespace=NAMESPACE)
    assert [p.name for p in result.instances] == ["cached"]
    assert not list((tmp_path / "managed").rglob("__pycache__"))


def test_loading_never_reads_a_planted_bytecode_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import importlib.util
    import py_compile

    monkeypatch.delenv("PYTHONPYCACHEPREFIX", raising=False)
    monkeypatch.setattr(sys, "pycache_prefix", None)
    root = write(tmp_path / "managed", {"rule.py": "class Planted(Base):\n    name = 'planted'\n"})
    source = root / "rule.py"
    cache = importlib.util.cache_from_source(str(source))
    # An unchecked-hash pyc is used without comparing it to its source by a standard loader.
    py_compile.compile(str(source), cfile=cache, invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)
    write(root, {"rule.py": "class Source(Base):\n    name = 'source'\n"})
    assert Path(cache).is_file()
    result = load_subclasses([PluginPackage.from_directory(root)], Base, namespace=NAMESPACE)
    assert [p.name for p in result.instances] == ["source"] and result.errors == ()


def test_loading_compiles_the_given_sources_instead_of_the_files(tmp_path: Path) -> None:
    root = write(
        tmp_path / "p",
        {"rule.py": "class Changed(Base):\n    name = 'changed'\n", "helpers.py": "VALUE = 'file'\n"},
    )
    verified = (
        f"from {BASE_MODULE} import Base\nfrom .helpers import VALUE\n\nclass Verified(Base):\n    name = VALUE\n"
    )
    pkg = PluginPackage(
        "verified",
        root,
        plugin_modules([("helpers", root / "helpers.py"), ("rule", root / "rule.py")]),
        {"rule": verified.encode("utf-8")},
    )
    result = load_subclasses([pkg], Base, namespace=NAMESPACE)
    assert [p.name for p in result.instances] == ["file"] and result.errors == ()
    module = sys.modules[f"{name_of(pkg)}.rule"]
    assert module.__file__ == str(root / "rule.py")
    assert module.__loader__.get_source(module.__name__) == verified  # type: ignore[union-attr]
