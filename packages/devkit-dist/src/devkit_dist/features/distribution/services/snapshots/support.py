"""Static supported-import and declarative-handler boundary; never executes source code."""

from __future__ import annotations

import ast
import sys
import tomllib
from pathlib import PurePosixPath

from devkit_core.core.plugins import plugin_module_name

from devkit_dist.features.distribution.models.content import Content
from devkit_dist.features.distribution.models.snapshots import SnapshotUnsupportedError
from devkit_dist.features.distribution.services.bundles import Bundle
from devkit_dist.features.distribution.services.bundles.common import read_frontmatter

# Public API surfaces used by bundle rules/gates; this is an inspectable subset, not a Python sandbox.
PUBLIC_DISTRIBUTIONS = {
    "devkit-core": ("base", "core"),
    "devkit-agt": ("features.rules", "features.gate"),
    "devkit-cli": ("",),
}


def public_api(module: str) -> bool:
    # Distribution names describe required consumer installations; no engine module is imported or inspected.
    if module == "devkit.advisory" or module.startswith("devkit.advisory."):
        return True
    for distribution, suffixes in PUBLIC_DISTRIBUTIONS.items():
        namespace = distribution.replace("-", "_")
        for suffix in suffixes:
            prefix = namespace + ("." + suffix if suffix else "")
            if module == prefix or module.startswith(prefix + "."):
                return True
    return False


def inert_initializer(data: bytes, name: str) -> None:
    try:
        body = ast.parse(data, filename=name).body
    except (SyntaxError, UnicodeError) as exc:
        raise SnapshotUnsupportedError(f"invalid resource initializer: {name}") from exc
    if body and not (
        len(body) == 1
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        raise SnapshotUnsupportedError(f"resource initializer must be empty or docstring-only: {name}")


def _relative_import(node: ast.ImportFrom, rel: str, files: dict[str, Content]) -> bool:
    parent = list(PurePosixPath(rel).parent.parts)
    if node.level > len(parent):
        return False
    base = parent[: len(parent) - node.level + 1]
    module = base + (node.module.split(".") if node.module else [])
    if node.module:
        prefix = "/".join(module)
        return f"{prefix}.py" in files or f"{prefix}/__init__.py" in files
    return all(
        item.name != "*"
        and (f"{'/'.join([*base, item.name])}.py" in files or f"{'/'.join([*base, item.name])}/__init__.py" in files)
        for item in node.names
    )


def check_python(files: dict[str, Content]) -> None:
    for rel, content in files.items():
        if plugin_module_name(rel) is None:
            continue
        try:
            tree = ast.parse(content.data, filename=rel)
        except (SyntaxError, UnicodeError) as exc:
            raise SnapshotUnsupportedError(f"unsupported Python syntax: {rel}: {exc}") from exc
        imported_dynamic = {
            alias.asname or alias.name
            for declaration in ast.walk(tree)
            if isinstance(declaration, ast.ImportFrom)
            for alias in declaration.names
            if alias.name in {"import_module", "__import__", "eval", "exec"}
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and (
                (
                    isinstance(node.func, ast.Name)
                    and node.func.id in ({"__import__", "eval", "exec"} | imported_dynamic)
                )
                or (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr in {"import_module", "exec_module", "load_module"}
                )
            ):
                raise SnapshotUnsupportedError(f"dynamic Python execution/import is unsupported: {rel}:{node.lineno}")
            if isinstance(node, ast.ImportFrom) and node.level:
                if not _relative_import(node, rel, files):
                    raise SnapshotUnsupportedError(f"relative import leaves copied helpers: {rel}:{node.lineno}")
                continue
            modules = (
                [item.name for item in node.names]
                if isinstance(node, ast.Import)
                else [node.module or ""]
                if isinstance(node, ast.ImportFrom)
                else []
            )
            for module in modules:
                if module.split(".")[0] in sys.stdlib_module_names or public_api(module):
                    continue
                raise SnapshotUnsupportedError(
                    f"external Python import is unsupported: {rel}:{getattr(node, 'lineno', 0)}: {module}"
                )


def check_declarations(bundle: Bundle, files: dict[str, Content]) -> None:
    for asset in bundle.assets:
        for _, source in asset.sources:
            if asset.kind == "hook":
                hook = tomllib.loads(files[source].data.decode())
                if hook.get("handler") != "observe":
                    raise SnapshotUnsupportedError(
                        f"external hook handler is unsupported: {source}: {hook.get('handler')}"
                    )
            if asset.kind == "workflow":
                _, _, header = read_frontmatter(files[source].data, source, "workflow")
                checks = header.get("checks", [])
                if not isinstance(checks, list):
                    raise SnapshotUnsupportedError(f"unsupported workflow checks: {source}")
                for check in checks:
                    if not isinstance(check, dict) or check.get("class") not in {"human", "runner", "disk", "lint"}:
                        raise SnapshotUnsupportedError(f"external workflow check/plugin is unsupported: {source}")
                    if set(check) & {"module", "plugin", "handler", "service"}:
                        raise SnapshotUnsupportedError(f"external workflow check/plugin is unsupported: {source}")
