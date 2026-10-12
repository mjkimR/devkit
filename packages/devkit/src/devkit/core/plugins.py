"""Load plugin classes from Python files outside any package.

Rules, gates and workflow checks are shipped as standalone ``.py`` files. Each
file is imported under a stable module name derived from its resolved path, and
every concrete subclass of a given base class *defined in that file* (not
imported into it) is instantiated without arguments.

Loading is atomic per file: if executing the file, instantiating any of its
classes or validating any instance fails, nothing from that file is returned,
the failure is recorded with the file's path, and ``sys.modules`` is restored
to what it was before the file was loaded. Plugin files run arbitrary code;
load them only from trusted sources.
"""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

PLUGIN_SUFFIX = ".py"


@dataclass(frozen=True)
class PluginFailure:
    """A file whose plugins could not be loaded."""

    path: Path
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


@dataclass(frozen=True)
class LoadedPlugin[T]:
    """One plugin instance and the file that defined its class."""

    path: Path
    instance: T


@dataclass(frozen=True)
class PluginLoad[T]:
    """Result of ``load_subclasses``: plugins in file order, then failures in file order."""

    plugins: tuple[LoadedPlugin[T], ...] = ()
    errors: tuple[PluginFailure, ...] = ()

    @property
    def instances(self) -> tuple[T, ...]:
        return tuple(plugin.instance for plugin in self.plugins)


def module_name(path: Path, namespace: str) -> str:
    """The stable module name a plugin file is imported under."""
    digest = hashlib.sha256(str(path.resolve()).encode("utf-8", errors="surrogateescape")).hexdigest()[:16]
    return f"{namespace}_{digest}"


def iter_plugin_files(directory: Path) -> list[Path]:
    """Every ``.py`` file under ``directory``, recursively, in sorted path order.

    Files and directories whose name starts with ``_`` or ``.`` are skipped
    (private helpers, ``__init__.py``, ``__pycache__``, hidden directories).
    A missing directory yields no files.
    """
    if not directory.is_dir():
        return []
    found: list[Path] = []
    for path in sorted(directory.rglob(f"*{PLUGIN_SUFFIX}")):
        relative = path.relative_to(directory)
        if any(part.startswith(("_", ".")) for part in relative.parts):
            continue
        if path.is_file():
            found.append(path)
    return found


def _defined_subclasses[T](module: ModuleType, base: type[T]) -> list[type[T]]:
    """Concrete subclasses of ``base`` defined in ``module``, in definition order."""
    classes: list[type[T]] = []
    for value in list(vars(module).values()):
        if (
            inspect.isclass(value)
            and value.__module__ == module.__name__
            and issubclass(value, base)
            and value is not base
            and not inspect.isabstract(value)
        ):
            classes.append(value)
    return classes


def _load_file[T](
    path: Path, base: type[T], namespace: str, validate: Callable[[T], None] | None
) -> list[LoadedPlugin[T]]:
    name = module_name(path, namespace)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError("cannot be loaded as a Python module")
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(name)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
        loaded = [LoadedPlugin(path, cls()) for cls in _defined_subclasses(module, base)]
        if validate is not None:
            for plugin in loaded:
                validate(plugin.instance)
    except BaseException:
        if previous is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous
        raise
    return loaded


def load_subclasses[T](
    files: Iterable[Path],
    base: type[T],
    *,
    namespace: str,
    validate: Callable[[T], None] | None = None,
) -> PluginLoad[T]:
    """Instantiate every concrete ``base`` subclass defined in each of ``files``.

    ``namespace`` prefixes the module names (``<namespace>_<sha256 prefix>``)
    and must be a valid identifier. ``validate`` is called on every instance of
    a file; raising rejects the whole file. Files are loaded in the given
    order; callers that scan a directory use ``iter_plugin_files``.
    """
    if not namespace.isidentifier():
        raise ValueError(f"plugin namespace must be an identifier: {namespace!r}")
    plugins: list[LoadedPlugin[T]] = []
    errors: list[PluginFailure] = []
    for path in files:
        try:
            plugins.extend(_load_file(path, base, namespace, validate))
        except (Exception, SystemExit) as exc:
            errors.append(PluginFailure(path, str(exc) or type(exc).__name__))
    return PluginLoad(tuple(plugins), tuple(errors))
