"""Load plugin classes from plugin packages: directories of Python modules outside any installed package.

Rules, gates and workflow checks are shipped as plugin packages. A plugin
package is a directory: every ``.py`` file in it (recursively) is a module of
one package, except files under a ``tests`` directory, ``test_*.py`` and
``*_test.py`` files (tests may live beside the code; they are never imported),
``__pycache__`` and hidden entries (``plugin_module_name``). ``__init__.py`` is
optional: when present it runs first as the package module, otherwise the
package module is empty. Modules import each other relatively
(``from .helpers import parse``), also lazily inside functions at run time.

A ``PluginPackage`` maps the dotted name of each module, relative to the
package (``""`` for ``__init__.py``), to the exact file to execute, so the
files of one package may come from different trees (a project override, the
managed copy, a Git snapshot's working tree). The package is imported under a
stable name (``<namespace>_<sha256 prefix of its key>``) through a dedicated
``sys.meta_path`` finder that resolves ``<package>.<dotted>`` only to the mapped
files: a module can never import an unlisted file that happens to sit in a
plugin directory. Every concrete subclass of a given base class *defined in*
a module of the package (not imported into it) is instantiated without
arguments, in module order (packages before their submodules) then definition
order.

Loading is atomic per package: if executing any module, instantiating any of
its classes or validating any instance fails, nothing from the package is
returned, the failure is recorded once with the package's root, and
``sys.modules`` and ``sys.meta_path`` are restored to what they were before the
package was loaded. A package that loads stays importable (its finder stays
installed) so lazy relative imports keep working. Plugin packages run
arbitrary code; load them only from trusted sources.

Plugin code always runs from source, never from bytecode: a ``__pycache__``
``.pyc`` next to a plugin file is never read, and none is written (plugins live
in devkit's managed root and in project overrides, where a ``__pycache__``
directory would be an unowned file). When a package carries ``sources`` (the
bytes ``devkit.core.verified_asset_packages`` checked against the installation
receipt), a module is compiled from exactly those bytes, so a file changed
between verification and import never runs.
"""

from __future__ import annotations

import hashlib
import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import inspect
import sys
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from types import CodeType, MappingProxyType, ModuleType

PLUGIN_SUFFIX = ".py"
TESTS_DIRECTORY = "tests"


class _SourceOnlyLoader(importlib.machinery.SourceFileLoader):
    """A loader that compiles source (``source`` when given, else the file) and never reads or writes bytecode."""

    def __init__(self, fullname: str, path: str, source: bytes | None = None) -> None:
        super().__init__(fullname, path)
        self._source = source

    def _source_bytes(self) -> bytes:
        return self._source if self._source is not None else self.get_data(self.path)

    def get_source(self, fullname: str) -> str:
        return importlib.util.decode_source(self._source_bytes())

    def get_code(self, fullname: str) -> CodeType:
        return self.source_to_code(self._source_bytes(), self.path)

    def set_data(self, path: str, data: bytes, *, _mode: int = 0o666) -> None:
        return None


class _EmptyPackageLoader(importlib.abc.Loader):
    """Creates the module of a package directory without ``__init__.py``: an empty package."""

    def create_module(self, spec: importlib.machinery.ModuleSpec) -> ModuleType | None:
        return None

    def exec_module(self, module: ModuleType) -> None:
        return None


@dataclass(frozen=True)
class PluginPackage:
    """One plugin package: a stable ``key``, the directory it is reported by, and its module files.

    ``modules`` maps each dotted module name relative to the package (``""``
    for ``__init__.py``, ``"sub.helpers"`` for ``sub/helpers.py``) to the exact
    file to execute. ``key`` names the package uniquely (its module name is
    derived from it); ``root`` is the directory failures are reported with
    (``key`` when ``None``). ``sources`` maps a dotted name to the source
    bytes to compile in place of reading its file (the file still names the
    module: ``__file__``, tracebacks); a module without an entry is read from
    its file when imported.
    """

    key: str
    root: Path | None
    modules: Mapping[str, Path] = field(default_factory=lambda: MappingProxyType({}))
    sources: Mapping[str, bytes] = field(default_factory=lambda: MappingProxyType({}))

    @property
    def location(self) -> Path:
        """What a failure of this package names: ``root``, else ``key`` as a path."""
        return self.root if self.root is not None else Path(self.key)

    @classmethod
    def from_directory(cls, root: Path) -> PluginPackage:
        """The plugin package of a directory: every module file under it (``plugin_module_name``).

        Raises ``ValueError`` when two files define one module (``a.py`` and ``a/__init__.py``).
        """
        files = [
            (name, path)
            for path in sorted(root.rglob(f"*{PLUGIN_SUFFIX}"))
            if (name := plugin_module_name(path.relative_to(root).as_posix())) is not None and path.is_file()
        ]
        return cls(str(root.resolve()), root, plugin_modules(files))


@dataclass(frozen=True)
class PluginFailure:
    """A plugin package (or a file where a package was expected) that could not be loaded."""

    path: Path
    message: str
    fix: str | None = None

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


@dataclass(frozen=True)
class LoadedPlugin[T]:
    """One plugin instance, the module file that defined its class, and the package it came from."""

    path: Path
    instance: T
    package: PluginPackage


@dataclass(frozen=True)
class PluginLoad[T]:
    """Result of ``load_subclasses``: plugins in package order, then failures in package order."""

    plugins: tuple[LoadedPlugin[T], ...] = ()
    errors: tuple[PluginFailure, ...] = ()

    @property
    def instances(self) -> tuple[T, ...]:
        return tuple(plugin.instance for plugin in self.plugins)


def module_name(key: str, namespace: str) -> str:
    """The stable name a plugin package with ``key`` is imported under."""
    digest = hashlib.sha256(key.encode("utf-8", errors="surrogateescape")).hexdigest()[:16]
    return f"{namespace}_{digest}"


def plugin_module_name(relative: str) -> str | None:
    """The dotted module name of a package file at POSIX path ``relative``, or ``None`` when it is not a module.

    ``a/b.py`` is ``"a.b"``, ``a/__init__.py`` is ``"a"`` and ``__init__.py``
    is ``""``. Not modules: non-``.py`` files, files under a ``tests``
    directory, ``test_*.py`` and ``*_test.py``, anything under ``__pycache__``
    and hidden entries. Whether each part is a valid identifier is checked
    when the package is loaded.
    """
    parts = PurePosixPath(relative).parts
    if not parts or not parts[-1].endswith(PLUGIN_SUFFIX):
        return None
    if any(part.startswith(".") or part == "__pycache__" for part in parts):
        return None
    if TESTS_DIRECTORY in parts[:-1]:
        return None
    stem = parts[-1][: -len(PLUGIN_SUFFIX)]
    if stem.startswith("test_") or stem.endswith("_test"):
        return None
    names = [*parts[:-1], *([] if stem == "__init__" else [stem])]
    return ".".join(names)


def plugin_modules(files: Iterable[tuple[str, Path]]) -> Mapping[str, Path]:
    """A read-only ``PluginPackage.modules`` mapping; ``ValueError`` when two files define one module."""
    modules: dict[str, Path] = {}
    for dotted, path in files:
        if dotted in modules and modules[dotted] != path:
            raise ValueError(f"{modules[dotted]} and {path} both define module {dotted or '__init__'}")
        modules[dotted] = path
    return MappingProxyType(modules)


def iter_plugin_packages(directory: Path) -> tuple[tuple[PluginPackage, ...], tuple[PluginFailure, ...]]:
    """The plugin packages of a plugin directory, and the files that sit where a package was expected.

    Each immediate subdirectory whose name does not start with ``_`` or ``.``
    (and is not ``tests``, never imported) is one package
    (``PluginPackage.from_directory``), in sorted order. A
    ``.py`` file directly in ``directory`` is a failure telling to move it into
    a package directory; files whose name starts with ``_`` or ``.`` and test
    files are skipped. A missing directory yields nothing.
    """
    if not directory.is_dir():
        return (), ()
    packages: list[PluginPackage] = []
    failures: list[PluginFailure] = []
    for entry in sorted(directory.iterdir()):
        if entry.name.startswith(("_", ".")) or entry.name == TESTS_DIRECTORY:
            continue
        if entry.is_dir():
            try:
                packages.append(PluginPackage.from_directory(entry))
            except ValueError as exc:
                failures.append(PluginFailure(entry, str(exc)))
        elif entry.is_file() and plugin_module_name(entry.name) is not None:
            target = f"{directory.as_posix()}/{entry.stem}/"
            failures.append(
                PluginFailure(
                    entry,
                    f"not a plugin package: a plugin file belongs in a package directory such as {target}",
                    fix=f"Move {entry.as_posix()} into {target}",
                )
            )
    return tuple(packages), tuple(failures)


class _PackageFinder(importlib.abc.MetaPathFinder):
    """Resolves ``<name>`` and ``<name>.<dotted>`` to the files of one plugin package, and nothing else."""

    def __init__(self, name: str, modules: Mapping[str, Path], sources: Mapping[str, bytes] | None = None) -> None:
        self.name = name
        self.modules = dict(modules)
        self.sources = dict(sources or {})
        self.packages = {""} | {
            ".".join(parts[:index])
            for dotted in modules
            if dotted
            for parts in [dotted.split(".")]
            for index in range(1, len(parts))
        }

    def find_spec(
        self, fullname: str, path: Sequence[str] | None = None, target: ModuleType | None = None
    ) -> importlib.machinery.ModuleSpec | None:
        if fullname == self.name:
            relative = ""
        elif fullname.startswith(f"{self.name}."):
            relative = fullname[len(self.name) + 1 :]
        else:
            return None
        file = self.modules.get(relative)
        is_package = relative in self.packages or (file is not None and file.name == f"__init__{PLUGIN_SUFFIX}")
        if file is None:
            if relative not in self.packages:
                return None  # the parent's empty ``__path__`` makes this a ModuleNotFoundError
            return importlib.machinery.ModuleSpec(fullname, _EmptyPackageLoader(), is_package=True)
        return importlib.util.spec_from_file_location(
            fullname,
            file,
            loader=_SourceOnlyLoader(fullname, str(file), self.sources.get(relative)),
            submodule_search_locations=[] if is_package else None,
        )


def check_plugin_modules(modules: Mapping[str, Path]) -> None:
    """Raise ``ValueError`` unless every module of a package can be imported by its dotted name.

    Each part of a dotted name must be an identifier, each file a ``.py``
    file, and a module file ``a.py`` may not sit beside a package directory
    ``a/`` (both would be module ``a``).
    """
    for dotted, file in modules.items():
        if dotted and not all(part.isidentifier() for part in dotted.split(".")):
            raise ValueError(f"{file} is not an importable module name (use identifiers for files and directories)")
        if file.suffix != PLUGIN_SUFFIX:
            raise ValueError(f"{file} is not a Python file")
    for dotted, file in modules.items():
        if (
            dotted
            and file.name != f"__init__{PLUGIN_SUFFIX}"
            and any(other.startswith(f"{dotted}.") for other in modules)
        ):
            raise ValueError(
                f"{file} and the package directory {dotted.rsplit('.', 1)[-1]}/ both define module {dotted}"
            )


def _owned(name: str) -> list[str]:
    return [key for key in sys.modules if key == name or key.startswith(f"{name}.")]


def _finders(name: str) -> list[_PackageFinder]:
    return [finder for finder in sys.meta_path if isinstance(finder, _PackageFinder) and finder.name == name]


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


def _module_order(dotted: str) -> tuple[str, ...]:
    return tuple(dotted.split(".")) if dotted else ()


def _load_package[T](
    package: PluginPackage, base: type[T], namespace: str, validate: Callable[[T], None] | None
) -> list[LoadedPlugin[T]]:
    name = module_name(package.key, namespace)
    previous_modules = {key: sys.modules.pop(key) for key in _owned(name)}
    previous_finders = _finders(name)
    for finder in previous_finders:
        sys.meta_path.remove(finder)
    finder = _PackageFinder(name, package.modules, package.sources)
    sys.meta_path.insert(0, finder)
    try:
        check_plugin_modules(package.modules)
        modules = [
            importlib.import_module(f"{name}.{dotted}" if dotted else name)
            for dotted in sorted({"", *package.modules}, key=_module_order)
        ]
        seen: set[type[T]] = set()
        loaded: list[LoadedPlugin[T]] = []
        for module in modules:
            for cls in _defined_subclasses(module, base):
                if cls in seen:
                    continue
                seen.add(cls)
                loaded.append(LoadedPlugin(Path(module.__file__ or package.location), cls(), package))
        if validate is not None:
            for plugin in loaded:
                validate(plugin.instance)
    except BaseException:
        for key in _owned(name):
            sys.modules.pop(key, None)
        if finder in sys.meta_path:
            sys.meta_path.remove(finder)
        sys.modules.update(previous_modules)
        sys.meta_path[0:0] = previous_finders
        raise
    return loaded


def load_subclasses[T](
    packages: Iterable[PluginPackage],
    base: type[T],
    *,
    namespace: str,
    validate: Callable[[T], None] | None = None,
) -> PluginLoad[T]:
    """Instantiate every concrete ``base`` subclass defined in each plugin package.

    ``namespace`` prefixes the package module names
    (``<namespace>_<sha256 prefix of the key>``) and must be a valid
    identifier. ``validate`` is called on every instance of a package; raising
    rejects the whole package. Packages are loaded in the given order; two
    packages with the same ``key`` never share module names: the second is a
    failure. Callers that scan a directory use ``iter_plugin_packages``.
    """
    if not namespace.isidentifier():
        raise ValueError(f"plugin namespace must be an identifier: {namespace!r}")
    plugins: list[LoadedPlugin[T]] = []
    errors: list[PluginFailure] = []
    keys: set[str] = set()
    for package in packages:
        if package.key in keys:
            errors.append(PluginFailure(package.location, f"duplicate plugin package {package.key}"))
            continue
        keys.add(package.key)
        try:
            plugins.extend(_load_package(package, base, namespace, validate))
        except (Exception, SystemExit) as exc:
            errors.append(PluginFailure(package.location, str(exc) or type(exc).__name__))
    return PluginLoad(tuple(plugins), tuple(errors))
