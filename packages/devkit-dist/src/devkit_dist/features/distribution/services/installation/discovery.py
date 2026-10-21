from __future__ import annotations

from collections.abc import Iterable, Iterator
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from importlib import metadata, resources

from devkit.advisory import AdvisoryError, Level

from devkit_dist.features.distribution.models.errors import BundleError, PackageError
from devkit_dist.features.distribution.services.bundles import Bundle, load_bundle

GROUP = "devkit.bundles"
# Bundles registered by the first-party devkit wheels are built in: devkit-dist (``devkit``, ``advisory``,
# ``git-commits``) and devkit-agt (``authoring``, ``harness``); distribution names, never modules. Any bundle declaring
# ``auto_select``, built in or not, is selected by default (see ``config``).
BUILTIN_DISTRIBUTIONS = frozenset({"devkit-dist", "devkit-agt"})


@dataclass(frozen=True)
class InstalledBundle:
    package: str
    package_version: str
    bundle: Bundle
    # Shipped by a first-party devkit wheel (``BUILTIN_DISTRIBUTIONS``).
    builtin: bool = False

    @property
    def auto_selected(self) -> bool:
        """Selected with its default preset unless ``[presets]`` names it or opts out."""
        return self.bundle.auto_select


class Discovered(list[InstalledBundle]):
    """The usable installed bundles, sorted by name, and ``unusable``: the load error of every other one.

    An entry point's name is its bundle's name, so a package that cannot be
    loaded is still known by the bundle it registers.
    """

    def __init__(self, bundles: list[InstalledBundle], unusable: dict[str, PackageError]) -> None:
        super().__init__(bundles)
        self.unusable = unusable


def unusable_bundles(installed: list[InstalledBundle]) -> dict[str, PackageError]:
    """Bundle name -> load error of the installed bundles that could not be loaded (none for a plain list)."""
    return dict(installed.unusable) if isinstance(installed, Discovered) else {}


def unusable_notices(installed: list[InstalledBundle], selected: Iterable[str]) -> list[AdvisoryError]:
    """Raise the load error of a selected bundle; return every other one as a warning.

    A package whose bundle the project does not deploy never stops a command,
    so the project can still deselect it or run ``devkit remove`` while the
    package is upgraded or uninstalled.
    """
    unusable = unusable_bundles(installed)
    for name in sorted(set(selected) & unusable.keys()):
        raise unusable[name]
    return [error.with_level(Level.WARNING) for _, error in sorted(unusable.items())]


def _load(stack: ExitStack, entry: metadata.EntryPoint) -> InstalledBundle:
    if entry.attr is not None or entry.extras or entry.dist is None:
        raise PackageError(f"{entry.name}: bundle entry point must reference a resource module")
    package = entry.dist.metadata["Name"]
    fix = f"Upgrade or uninstall the package {package} (`uv remove {package}`)"
    try:
        root = stack.enter_context(resources.as_file(resources.files(entry.module).joinpath("bundle")))
        bundle = load_bundle(root)
    except BundleError as exc:
        raise PackageError(f"{entry.name}: installed bundle is invalid: {exc.message}", *exc.details, fix=fix) from exc
    except Exception as exc:
        # Importing the resource module runs its ``__init__``: any failure there is the package's defect, not devkit's.
        raise PackageError(
            f"{entry.name}: cannot read content resources: {type(exc).__name__}: {exc}", fix=fix
        ) from exc
    if bundle.name != entry.name:
        raise PackageError(
            f"{entry.name}: the entry point registers bundle {bundle.name}; its name must be the bundle name", fix=fix
        )
    return InstalledBundle(package, entry.dist.version, bundle, package in BUILTIN_DISTRIBUTIONS)


@contextmanager
def discover_bundles() -> Iterator[Discovered]:
    """Load every installed bundle; keep resource materializations alive for the whole operation.

    A package that cannot be loaded is recorded under ``unusable`` instead of
    stopping discovery (``unusable_notices`` decides per command); two entry
    points with one name are ambiguous and always an error.
    """
    found: list[InstalledBundle] = []
    unusable: dict[str, PackageError] = {}
    with ExitStack() as stack:
        for entry in sorted(metadata.entry_points(group=GROUP), key=lambda item: (item.name, item.value)):
            if entry.name in unusable or any(item.bundle.name == entry.name for item in found):
                raise PackageError(f"duplicate installed bundle: {entry.name}")
            try:
                found.append(_load(stack, entry))
            except PackageError as exc:
                unusable[entry.name] = exc
        yield Discovered(sorted(found, key=lambda item: item.bundle.name), unusable)
