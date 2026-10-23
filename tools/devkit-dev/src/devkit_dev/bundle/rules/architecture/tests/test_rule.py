"""Layout, dependency and import resolution checks from temporary repositories."""

from __future__ import annotations

from pathlib import Path

import pytest
from devkit_agt.features.rules import match_path
from devkit_agt.features.rules.services.testing import check, evaluate, load_rule, opened_files, write_files

RULE = load_rule(__file__)
inspect_architecture = RULE.__module__  # load_rule isolates dynamically loaded rule names


def _inspect(root: Path, files: dict[str, str], extra: str = "") -> list[str]:
    import sys

    config = """schema = 1
[[packages]]
namespace = "sample"
root = "src/sample"
kind = "features"
features = ["one", "two"]
feature_dependencies = { one = ["sample.features.two"], two = [] }
dependencies = []
"""
    for rel, content in {".devkit/architecture.toml": config + extra, **files}.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return [message for _, _, message in sys.modules[inspect_architecture].inspect_architecture(root)]


def test_allowed_layer_directions_and_single_file_layers(tmp_path: Path) -> None:
    assert not _inspect(
        tmp_path,
        {
            "src/sample/features/one/cli.py": "from .usecases import run\n",
            "src/sample/features/one/usecases.py": "from . import services\ndef run(): return services.execute()\n",
            "src/sample/features/one/services.py": "from . import repositories\ndef execute(): return repositories.read()\n",
            "src/sample/features/one/repositories.py": "from .models import Model\ndef read(): return Model()\n",
            "src/sample/features/one/models.py": "class Model: pass\n",
        },
    )


def test_relative_nested_imports_cannot_reverse_layers(tmp_path: Path) -> None:
    found = _inspect(
        tmp_path,
        {
            "src/sample/features/one/models/contracts.py": "def run():\n from ..usecases import execute\n",
            "src/sample/features/one/usecases.py": "def execute(): pass\n",
        },
    )
    assert any("models cannot import usecases" in message for message in found)


def test_from_package_import_submodule_is_checked(tmp_path: Path) -> None:
    found = _inspect(
        tmp_path,
        {
            "src/sample/features/one/repositories/__init__.py": "from .. import services\n",
            "src/sample/features/one/services.py": "pass\n",
        },
    )
    assert any("repositories cannot import services" in message for message in found)


def test_layout_base_feature_public_and_legacy_namespace(tmp_path: Path) -> None:
    found = _inspect(
        tmp_path,
        {
            "src/sample/core/git.py": "pass\n",
            "src/sample/base/model.py": "from sample.features.one.models import Model\n",
            "src/sample/features/one/models.py": "pass\n",
            "src/sample/features/two/usecases.py": "from sample.features.one.models import Model\nimport devkit.core\n",
        },
    )
    assert any("not core" in message for message in found)
    assert any("base depends on implementation" in message for message in found)
    assert any("cross-feature import bypasses public API" in message for message in found)
    assert any("legacy shared namespace" in message for message in found)


def test_constant_dynamic_imports_and_entrypoint_strings(tmp_path: Path) -> None:
    found = _inspect(
        tmp_path,
        {
            "src/sample/features/one/models.py": 'import importlib\nimportlib.import_module("sample.features.one.usecases")\nENTRY = "devkit.core.cli:main"\n',
            "src/sample/features/one/usecases.py": "pass\n",
        },
    )
    assert any("models cannot import usecases" in message for message in found)
    assert any("legacy shared namespace" in message for message in found)


def test_explicit_public_module_and_narrow_exception(tmp_path: Path) -> None:
    files = {
        "src/sample/features/one/models.py": "from .services import helper\n",
        "src/sample/features/one/services.py": "pass\n",
    }
    exception = """
[[import_exceptions]]
source = "sample.features.one.models"
target = "sample.features.one.services"
reason = "Existing combined parsing contract pending responsibility split."
"""
    assert not _inspect(tmp_path, files, exception)
    files["src/sample/features/one/models.py"] = "pass\n"
    assert any("unused import exception" in message for message in _inspect(tmp_path, files, exception))


def test_missing_and_invalid_declaration_fail(tmp_path: Path) -> None:
    import sys

    inspect = sys.modules[inspect_architecture].inspect_architecture
    assert "missing" in inspect(tmp_path)[0][2]
    found = _inspect(
        tmp_path, {"src/sample/__init__.py": ""}, '\n[[import_exceptions]]\nsource="*"\ntarget="*"\nreason="all"\n'
    )
    assert any("cannot use wildcards" in message for message in found)


def test_facade_does_not_hide_layer_direction(tmp_path: Path) -> None:
    found = _inspect(
        tmp_path,
        {
            "src/sample/features/one/models.py": "from sample.features.two import execute\n",
            "src/sample/features/two/__init__.py": "from .usecases import execute\n",
            "src/sample/features/two/usecases.py": "def execute(): pass\n",
        },
    )
    assert any("models cannot import usecases" in message for message in found)


def test_declared_public_module_is_available_across_features(tmp_path: Path) -> None:
    assert not _inspect(
        tmp_path,
        {
            "src/sample/features/one/services.py": "from sample.features.two.models import Result\n",
            "src/sample/features/two/models.py": "class Result: pass\n",
        },
        'public_modules = ["sample.features.two.models"]\n',
    )


def test_aliased_dynamic_relative_import(tmp_path: Path) -> None:
    found = _inspect(
        tmp_path,
        {
            "src/sample/features/one/models.py": 'from importlib import import_module as load\nload(".usecases", package="sample.features.one")\n',
            "src/sample/features/one/usecases.py": "pass\n",
        },
    )
    assert any("models cannot import usecases" in message for message in found)


def test_configuration_reports_package_cycles_and_entrypoint_targets(tmp_path: Path) -> None:
    found = _inspect(
        tmp_path,
        {
            "src/sample/__init__.py": "",
            "pyproject.toml": '[project.scripts]\nsample="sample.missing:main"\n',
        },
        'dependencies = ["sample"]\n',
    )
    # Duplicate TOML keys fail rather than silently overriding architecture policy.
    assert any("invalid architecture declaration" in message for message in found)
    found = _inspect(tmp_path, {"src/sample/__init__.py": ""})
    assert any("entry-point module is missing" in message for message in found)


def test_package_dependencies_are_declared_and_cycles_fail(tmp_path: Path) -> None:
    import sys

    _inspect(tmp_path, {"src/sample/features/one/models.py": "import other\n", "src/other/__init__.py": ""})
    config = tmp_path / ".devkit/architecture.toml"
    config.write_text(
        config.read_text()
        + """
[[packages]]
namespace = "other"
root = "src/other"
kind = "content"
dependencies = ["sample"]
"""
    )
    inspect = sys.modules[inspect_architecture].inspect_architecture
    assert any("undeclared package dependency" in message for _, _, message in inspect(tmp_path))
    config.write_text(config.read_text().replace("dependencies = []", 'dependencies = ["other"]'))
    assert any("package dependency cycle" in message for _, _, message in inspect(tmp_path))


def test_resource_rule_tests_and_static_assets_are_not_product_modules(tmp_path: Path) -> None:
    assert not _inspect(
        tmp_path,
        {
            "src/sample/bundle/rules/check/rule.py": "this is deployed rule data\n",
            "src/sample/static/generated.py": "not product source\n",
            "src/sample/features/one/services/builtins/rule/tests/test_rule.py": "a bundled rule test\n",
        },
        'data_roots = ["bundle", "static"]\nembedded_test_roots = ["features/one/services/builtins"]\n',
    )


def test_cross_package_imports_keep_layers_and_public_api(tmp_path: Path) -> None:
    import sys

    _inspect(
        tmp_path,
        {
            "src/sample/features/one/models.py": "from other.features.two.usecases import run\n",
            "src/other/features/two/usecases.py": "def run(): pass\n",
        },
    )
    config = tmp_path / ".devkit/architecture.toml"
    config.write_text(
        config.read_text()
        .replace("dependencies = []", 'dependencies = ["other"]')
        .replace('one = ["sample.features.two"]', 'one = ["sample.features.two", "other.features.two"]')
        + """
[[packages]]
namespace = "other"
root = "src/other"
kind = "features"
features = ["two"]
feature_dependencies = { two = [] }
dependencies = []
public_modules = ["other.features.two.usecases"]
"""
    )
    inspect = sys.modules[inspect_architecture].inspect_architecture
    assert any("models cannot import usecases" in message for _, _, message in inspect(tmp_path))
    model = tmp_path / "src/sample/features/one/models.py"
    model.rename(model.with_name("usecases.py"))
    assert not inspect(tmp_path)
    config.write_text(
        config.read_text().replace('public_modules = ["other.features.two.usecases"]', "public_modules = []")
    )
    assert any("bypasses public API" in message for _, _, message in inspect(tmp_path))


def test_package_management_functions_and_dynamic_loading_in_init_are_allowed(tmp_path: Path) -> None:
    assert not _inspect(
        tmp_path,
        {
            "src/sample/features/one/__init__.py": (
                "from importlib import import_module\n"
                "__all__ = ['Result']\n"
                "def __getattr__(name):\n"
                "    return getattr(import_module('.models', package=__name__), name)\n"
            ),
            "src/sample/features/one/models.py": "class Result: pass\n",
        },
    )


def test_package_tests_require_a_boundary_category_but_keep_root_fixtures(tmp_path: Path) -> None:
    found = _inspect(
        tmp_path,
        {
            "src/sample/__init__.py": "",
            "tests/test_misplaced.py": "pass\n",
            "tests/features/test_misplaced.py": "pass\n",
            "tests/unit/features/one/test_models.py": "pass\n",
            "tests/integration/features/one/test_repository.py": "pass\n",
            "tests/e2e/test_cli.py": "pass\n",
            "tests/support/factories.py": "pass\n",
            "tests/conftest.py": "pass\n",
            "tests/__init__.py": "",
        },
    )
    assert found == ["tests belong under unit, integration, e2e or support"] * 2


def test_executable_bundle_manifests_use_the_named_resource_directory(tmp_path: Path) -> None:
    found = _inspect(
        tmp_path,
        {
            "src/sample/bundle/bundle.toml": "name='old'\n",
            "src/sample/bundles/example/bundle/bundle.toml": "name='example'\n",
        },
        'data_roots = ["bundles"]\n',
    )
    assert found == ["executable bundle belongs at bundles/<name>/bundle"]


def test_feature_dependencies_have_explicit_direction(tmp_path: Path) -> None:
    found = _inspect(
        tmp_path,
        {
            "src/sample/features/two/usecases.py": "from sample.features.one import run\n",
            "src/sample/features/one/__init__.py": "from .usecases import run\n",
            "src/sample/features/one/usecases.py": "def run(): pass\n",
        },
    )
    assert any(
        "undeclared feature dependency sample.features.two -> sample.features.one" in message for message in found
    )


def test_actual_feature_cycle_is_reported_even_with_public_facades(tmp_path: Path) -> None:
    import sys

    _inspect(
        tmp_path,
        {
            "src/sample/features/one/usecases.py": "from sample.features.two import second\ndef first(): pass\n",
            "src/sample/features/one/__init__.py": "from .usecases import first\n",
            "src/sample/features/two/usecases.py": "from sample.features.one import first\ndef second(): pass\n",
            "src/sample/features/two/__init__.py": "from .usecases import second\n",
        },
    )
    config = tmp_path / ".devkit/architecture.toml"
    config.write_text(config.read_text().replace("two = []", 'two = ["sample.features.one"]'))
    found = sys.modules[inspect_architecture].inspect_architecture(tmp_path)
    assert any("feature dependency cycle:" in message for _, _, message in found)


def test_module_alias_attribute_cannot_hide_facade_layer(tmp_path: Path) -> None:
    found = _inspect(
        tmp_path,
        {
            "src/sample/features/one/cli.py": "import sample.features.one.usecases as operations\noperations.run()\n",
            "src/sample/features/one/usecases.py": "from .services import run\n",
            "src/sample/features/one/services.py": "def run(): pass\n",
        },
    )
    assert any("cli cannot import services" in message for message in found)


def test_invalid_feature_dependency_is_rejected(tmp_path: Path) -> None:
    import sys

    _inspect(tmp_path, {"src/sample/__init__.py": ""})
    config = tmp_path / ".devkit/architecture.toml"
    config.write_text(config.read_text().replace("sample.features.two", "sample.features.missing"))
    assert any(
        "unknown feature dependency" in message
        for _, _, message in sys.modules[inspect_architecture].inspect_architecture(tmp_path)
    )


def test_facade_module_reexport_cannot_hide_attribute_layer(tmp_path: Path) -> None:
    found = _inspect(
        tmp_path,
        {
            "src/sample/features/one/cli.py": "from sample.features.two import operations\noperations.run()\n",
            "src/sample/features/two/__init__.py": "import sample.features.two.usecases as operations\n",
            "src/sample/features/two/usecases.py": "from .services import run\n",
            "src/sample/features/two/services.py": "def run(): pass\n",
        },
    )
    assert any("cli cannot import services" in message for message in found)


# --- declared inputs: targeted runs skip the rule when no target can change its findings ---------------------------

INPUTS: tuple[str, ...] = getattr(RULE, "inputs", None) or ()

SEEDED_CONFIG = """schema = 1
[[packages]]
namespace = "sample"
root = "src/sample"
kind = "features"
features = ["one", "two"]
feature_dependencies = { one = ["sample.features.two"], two = [] }
dependencies = []

[[import_exceptions]]
source = "sample.features.one.cli"
target = "sample.features.two.unused"
reason = "seeded"
"""
# One seeded violation per declared input pattern, plus files the rule must never read.
SEEDED = {
    ".devkit/architecture.toml": SEEDED_CONFIG,
    "src/sample/features/one/models.py": "from sample.features.one.usecases import run\n",
    "src/sample/features/one/usecases.py": "def run(): pass\n",
    "src/sample/features/two/__init__.py": "",
    "pyproject.toml": '[project]\nname = "sample"\n[project.scripts]\nsample = "sample.missing:main"\n',
    "src/sample/misplaced/bundle.toml": "",
    "docs/a.md": "# A\n",
    "README.md": "# Sample\n",
    "src/sample/features/one/notes.txt": "notes\n",
    "data.json": "{}\n",
}
SEEDED_MESSAGES = {
    "unused import exception: sample.features.one.cli -> sample.features.two.unused",
    "models cannot import usecases: sample.features.one.usecases",
    "entry-point module is missing: sample.missing",
    "executable bundle belongs at bundles/<name>/bundle",
}

# One target per declared pattern, each holding (or being) a seeded violation.
MATCHING_TARGETS = [
    ".devkit/architecture.toml",
    "src/sample/features/one/usecases.py",
    "pyproject.toml",
    "src/sample/misplaced/bundle.toml",
]


def test_the_declaration_and_one_matching_target_per_pattern() -> None:
    assert INPUTS == ("**/*.py", "**/pyproject.toml", "**/bundle.toml", ".devkit/architecture.toml")
    assert all(any(match_path(pattern, target) for target in MATCHING_TARGETS) for pattern in INPUTS)


def test_documentation_targets_skip_the_rule(tmp_path: Path) -> None:
    result = evaluate(RULE, tmp_path, SEEDED, targets=["docs/a.md", "README.md"])
    assert result.skipped == [RULE.id] and result.violations == []


@pytest.mark.parametrize("target", MATCHING_TARGETS)
def test_a_target_matching_each_declared_input_reports_the_seeded_violations(tmp_path: Path, target: str) -> None:
    found = check(RULE, tmp_path, SEEDED, targets=["docs/a.md", target])
    assert {v.message for v in found} == SEEDED_MESSAGES


def test_a_violation_outside_the_targets_is_reported_only_when_a_python_file_is_targeted(tmp_path: Path) -> None:
    seeded = ("src/sample/features/one/models.py", "models cannot import usecases: sample.features.one.usecases")
    files = {**SEEDED, "src/sample/features/two/other.py": "VALUE = 1\n"}
    whole = check(RULE, tmp_path, files)
    python = check(RULE, tmp_path, targets=["src/sample/features/two/other.py"])
    documentation = check(RULE, tmp_path, targets=["docs/a.md"])
    assert seeded in {(v.file, v.message) for v in whole}
    assert seeded in {(v.file, v.message) for v in python}
    assert documentation == []


def test_every_file_the_rule_opens_matches_its_inputs(tmp_path: Path) -> None:
    write_files(tmp_path, SEEDED)
    with opened_files(tmp_path) as opened:
        check(RULE, tmp_path)
    assert {".devkit/architecture.toml", "pyproject.toml", "src/sample/features/one/models.py"} <= opened
    assert [name for name in sorted(opened) if not any(match_path(p, name) for p in INPUTS)] == []


def _parses_through_the_shared_cache(root: Path, monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Run the rule on a shared cache; return the Python files it scanned, each left equal to a fresh parse."""
    import ast

    from devkit_agt.features.rules import RuleContext, WorkspaceCache

    ctx = RuleContext(workspace_root=root, cache=WorkspaceCache(root))
    RULE.check(ctx)
    original = ast.parse
    parsed: list[str] = []
    monkeypatch.setattr(ast, "parse", lambda *args, **kwargs: parsed.append(str(args[0])) or original(*args, **kwargs))
    scanned = sorted(path.relative_to(root).as_posix() for path in (root / "src").rglob("*.py"))
    for name in scanned:
        tree = ctx.cache.get_python_ast(name)
        assert ast.dump(tree, include_attributes=True) == ast.dump(
            original((root / name).read_bytes()), include_attributes=True
        )
    assert parsed == []  # the rule had already parsed every scanned file through ctx.cache
    return scanned


def test_sources_are_parsed_once_through_the_shared_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_files(tmp_path, SEEDED)
    assert len(_parses_through_the_shared_cache(tmp_path, monkeypatch)) >= 2


def test_a_source_that_does_not_parse_is_reported_at_its_file(tmp_path: Path) -> None:
    write_files(tmp_path, {**SEEDED, "src/sample/features/one/broken.py": "def broken(:\n"})
    found = [(v.file, v.line, v.message) for v in check(RULE, tmp_path) if "parse" in v.message]
    assert len(found) == 1
    file, line, message = found[0]
    assert (file, line) == ("src/sample/features/one/broken.py", 1)
    assert message.startswith("cannot parse source: ") and message.endswith("(broken.py, line 1)")


def test_persistent_facts_roundtrip_and_current_policy(tmp_path: Path, monkeypatch) -> None:
    import sys

    from devkit_agt.features.rules import WorkspaceCache

    _inspect(
        tmp_path,
        {
            "src/sample/features/one/models.py": 'import importlib as loader\nfrom . import usecases\nloader.import_module(".usecases", package="sample.features.one")\nENTRY="sample.features.one.usecases:run"\n',
            "src/sample/features/one/usecases.py": "def run(): pass\n",
            "src/sample/features/two/__init__.py": "from ..one.usecases import run as exported\n",
            "src/sample/features/two/services.py": "from . import exported\n",
        },
    )
    module = sys.modules[inspect_architecture]
    (tmp_path / ".devkit/transient").mkdir()
    disabled = module.inspect_architecture(tmp_path, cache=WorkspaceCache(tmp_path, facts_enabled=False))
    cache = WorkspaceCache(tmp_path, facts_writer=True, facts_prune=True)
    assert module.inspect_architecture(tmp_path, cache=cache) == disabled
    cache.flush_file_facts()
    warm = WorkspaceCache(tmp_path)
    monkeypatch.setattr(warm, "get_python_ast", lambda *args: pytest.fail("warm facts requested AST"))
    monkeypatch.setattr(warm, "get_python_nodes", lambda *args: pytest.fail("warm facts requested nodes"))
    assert module.inspect_architecture(tmp_path, cache=warm) == disabled
    config = tmp_path / ".devkit/architecture.toml"
    config.write_text(config.read_text().replace('one = ["sample.features.two"]', "one = []"))
    assert module.inspect_architecture(tmp_path, cache=WorkspaceCache(tmp_path)) == module.inspect_architecture(
        tmp_path, cache=WorkspaceCache(tmp_path, facts_enabled=False)
    )
    assert {d.name for d in module.FACTS.source_dependencies} == {"RULE-architecture.rule", "RULE-architecture.facts"}


def test_caught_parse_failure_does_not_prune_unseen_entries(tmp_path: Path) -> None:
    import json
    import sys

    from devkit_agt.features.rules import WorkspaceCache

    _inspect(
        tmp_path,
        {
            "src/sample/features/one/good.py": "value=1\n",
            "src/sample/features/one/gone.py": "value=2\n",
        },
    )
    (tmp_path / ".devkit/transient").mkdir()
    inspect = sys.modules[inspect_architecture].inspect_architecture
    cache = WorkspaceCache(tmp_path, facts_writer=True, facts_prune=True)
    inspect(tmp_path, cache=cache)
    cache.flush_file_facts()
    gone = "src/sample/features/one/gone.py"
    (tmp_path / gone).unlink()
    bad = tmp_path / "src/sample/features/one/bad.py"
    bad.write_text("def broken(")
    cache = WorkspaceCache(tmp_path, facts_writer=True, facts_prune=True)
    assert any("cannot parse source" in m for _, _, m in inspect(tmp_path, cache=cache))
    cache.flush_file_facts()
    memo = tmp_path / ".devkit/transient/rules/facts/RULE-architecture.json"
    assert gone in json.loads(memo.read_text())["entries"]
    bad.write_text("value=3\n")
    cache = WorkspaceCache(tmp_path, facts_writer=True, facts_prune=True)
    inspect(tmp_path, cache=cache)
    cache.flush_file_facts()
    assert gone not in json.loads(memo.read_text())["entries"]
