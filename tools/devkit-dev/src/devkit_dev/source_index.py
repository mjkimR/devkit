"""The source index the repository's structure rules share: one module walk over ``.devkit/architecture.toml``.

The rules are isolated plugin packages, so what they share lives here in the installed ``devkit_dev`` package:
which files are modules, their dotted names and layers, import bindings and facade re-export resolution. Nothing
here imports or executes inspected code.
"""

from __future__ import annotations

import importlib.util
from collections.abc import Callable, Container, Iterable, Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

CONFIG = ".devkit/architecture.toml"

type Status = Literal["module", "misplaced-test", "skipped"]
# One import statement: ``module`` is ``None`` for ``import a.b``, the (possibly empty) module of a from-import.
type ImportStatement = tuple[str | None, int, Iterable[tuple[str, str | None]]]


@dataclass(frozen=True)
class SourceFile:
    """One Python file below a declared package root, classified by the declaration."""

    file: Path
    path: str
    namespace: str
    relative: tuple[str, ...]
    status: Status

    @property
    def is_package(self) -> bool:
        return self.relative[-1] == "__init__"

    @property
    def parts(self) -> tuple[str, ...]:
        return self.relative[:-1] if self.is_package else self.relative

    @property
    def name(self) -> str:
        return ".".join((self.namespace, *self.parts))


def _status(relative_path: Path, package: Mapping[str, Any]) -> Status:
    data_roots = package.get("data_roots", [])
    if "tests" in relative_path.parts:
        if any(relative_path.is_relative_to(prefix) for prefix in package.get("embedded_test_roots", [])):
            return "skipped"
        return "skipped" if relative_path.parts[0] in data_roots else "misplaced-test"
    return "skipped" if relative_path.parts[0] in data_roots else "module"


def iter_sources(root: Path, packages: Iterable[Mapping[str, Any]]) -> Iterator[SourceFile]:
    """Every Python file of each declared package root, in declaration then path order.

    Data roots and embedded test roots are skipped; any other ``tests`` directory is a misplaced test.
    """
    for package in packages:
        source = root / package["root"]
        for path in sorted(source.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            relative_path = path.relative_to(source)
            yield SourceFile(
                path,
                path.relative_to(root).as_posix(),
                package["namespace"],
                relative_path.with_suffix("").parts,
                _status(relative_path, package),
            )


def feature_of(parts: tuple[str, ...]) -> str | None:
    """The feature of a module below its namespace: ``features/<feature>/...``."""
    return parts[1] if len(parts) > 1 and parts[0] == "features" else None


def layer_of(parts: tuple[str, ...]) -> str | None:
    """The layer of a module below its namespace: ``features/<feature>/<layer>`` or ``adapters``."""
    if parts and parts[0] == "adapters":
        return "adapters"
    return parts[2] if len(parts) > 2 and parts[0] == "features" else None


def context_of(name: str, is_package: bool) -> str:
    """The package relative imports of module ``name`` resolve against."""
    return name if is_package else name.rpartition(".")[0]


def resolve_relative(name: str, context: str) -> str | None:
    """Resolve a leading-dot module name against ``context``; ``None`` when it escapes the package."""
    try:
        return importlib.util.resolve_name(name, context)
    except ImportError:
        return None


def bind(statements: Iterable[ImportStatement], context: str) -> dict[str, str]:
    """The names import statements bind, mapped to the dotted target each name refers to; later bindings win."""
    bindings: dict[str, str] = {}
    for module, level, names in statements:
        if module is None:
            for name, asname in names:
                bindings[asname or name.split(".")[0]] = name if asname else name.split(".")[0]
            continue
        base = resolve_relative("." * level + module, context) if level else module
        if base is None:
            continue
        for name, asname in names:
            bindings[asname or name] = f"{base}.{name}"
    return bindings


def longest_module(symbol: str, modules: Container[str]) -> str:
    """The longest dotted prefix of ``symbol`` that names a module, or its first component when none does."""
    while symbol not in modules and "." in symbol:
        symbol = symbol.rpartition(".")[0]
    return symbol


def resolve_forward[M](
    symbol: str,
    modules: Mapping[str, M],
    forwards: Callable[[M], Mapping[str, str]],
    *,
    final: Callable[[str], bool] | None = None,
    indexed_only: bool = False,
    trail: frozenset[str] = frozenset(),
) -> str:
    """Follow facade re-exports from ``symbol`` to the symbol they forward to.

    ``forwards`` gives a module's re-exported names; ``final`` stops at a symbol that needs no forwarding. With
    ``indexed_only`` a forward is followed only to a symbol inside an indexed module and never back along the trail,
    so the result stays the last indexed hop.
    """
    if symbol in trail or (final is not None and final(symbol)):
        return symbol
    name = longest_module(symbol, modules)
    if name in modules and name != symbol:
        attribute, _, rest = symbol[len(name) + 1 :].partition(".")
        forwarded = forwards(modules[name]).get(attribute)
        if forwarded:
            forwarded += f".{rest}" if rest else ""
            hops = trail | {symbol}
            if not indexed_only or (forwarded not in hops and longest_module(forwarded, modules) in modules):
                return resolve_forward(forwarded, modules, forwards, final=final, indexed_only=indexed_only, trail=hops)
    return symbol
