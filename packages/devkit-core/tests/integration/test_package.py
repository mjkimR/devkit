"""The foundation is installable without application wheels or transport dependencies."""

from __future__ import annotations

import ast
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/devkit_core"


def test_foundation_imports_only_its_own_code_advisory_yaml_and_stdlib() -> None:
    violations = []
    for path in SOURCE.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                names = [node.module]
            else:
                continue
            for name in names:
                if name.split(".")[0] in {*sys.stdlib_module_names, "devkit_core", "yaml"}:
                    continue
                if name == "devkit.advisory" or name.startswith("devkit.advisory."):
                    continue
                violations.append(f"{path.relative_to(SOURCE)}:{node.lineno}: {name}")
    assert violations == []


def test_package_owns_one_independent_root_and_no_entry_points() -> None:
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text())
    assert metadata["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"] == ["src/devkit_core"]
    assert not (ROOT / "src/devkit").exists()
    assert not metadata["project"].get("scripts")
    assert not metadata["project"].get("entry-points")
    assert metadata["project"]["dependencies"] == [
        f"devkit-advisory=={metadata['project']['version']}",
        "pyyaml>=6.0.1",
    ]


def test_public_foundation_import_does_not_load_application_or_transport_modules() -> None:
    script = """
import sys
from devkit_core.core import Deadline, Frontmatter, run_git, file_lock
from devkit_core.base.mcp import McpTool
assert not any(name.startswith(('devkit_dist', 'devkit_agt', 'devkit_spec', 'devkit_viewer', 'devkit_mcp')) for name in sys.modules)
assert not any(name in sys.modules for name in ('click', 'mcp', 'jinja2'))
"""
    subprocess.run([sys.executable, "-c", script], check=True)


def test_base_imports_only_contracts_advisory_and_stdlib() -> None:
    from importlib.util import resolve_name

    violations = []
    for path in (SOURCE / "base").rglob("*.py"):
        relative = path.relative_to(SOURCE.parent).with_suffix("")
        package = ".".join(relative.parts[:-1])
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if node.level:
                    module = resolve_name("." * node.level + module, package)
                names = [module, *(f"{module}.{alias.name}" for alias in node.names)]
            else:
                continue
            for name in names:
                if name.split(".")[0] in sys.stdlib_module_names or name == "devkit_core":
                    continue
                if any(
                    name == prefix or name.startswith(prefix + ".")
                    for prefix in ("devkit_core.base", "devkit.advisory")
                ):
                    continue
                violations.append(f"{path.relative_to(SOURCE)}:{node.lineno}: {name}")
    assert violations == []


def test_base_imports_do_not_initialize_implementations_or_yaml() -> None:
    script = """
import sys
from devkit_core.base.errors import GitError, DeadlineExceededError
from devkit_core.base.mcp import McpTool
assert GitError.__module__ == 'devkit_core.base.errors'
assert McpTool.__module__ == 'devkit_core.base.mcp'
assert not any(name == 'devkit_core.core' or name.startswith('devkit_core.core.') for name in sys.modules)
assert not any(name in sys.modules for name in ('yaml', 'click', 'mcp', 'jinja2'))
"""
    subprocess.run([sys.executable, "-c", script], check=True)
