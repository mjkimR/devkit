"""Layout, dependency and import resolution checks from temporary repositories."""

from __future__ import annotations

from pathlib import Path

from devkit_agt.features.rules.services.testing import load_rule

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
