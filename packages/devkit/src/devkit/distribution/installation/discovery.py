from __future__ import annotations

from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from importlib import metadata, resources

from devkit.distribution.bundles import Bundle, load_bundle
from devkit.distribution.errors import BundleError, PackageError

GROUP = "devkit.bundles"
# Bundles registered by this distribution are built in: selected by default (see ``config``).
BUILTIN_DISTRIBUTION = "devkit"


@dataclass(frozen=True)
class InstalledBundle:
    package: str
    package_version: str
    bundle: Bundle
    # Shipped by the ``devkit`` distribution itself; selected with its default preset unless opted out.
    builtin: bool = False


@contextmanager
def discover_bundles() -> Iterator[list[InstalledBundle]]:
    """Keep resource materializations alive for the whole sync operation."""
    found = []
    names: set[str] = set()
    with ExitStack() as stack:
        for entry in sorted(metadata.entry_points(group=GROUP), key=lambda item: (item.name, item.value)):
            if entry.attr is not None or entry.extras or entry.dist is None:
                raise PackageError(f"{entry.name}: bundle entry point must reference a resource module")
            try:
                root = stack.enter_context(resources.as_file(resources.files(entry.module).joinpath("bundle")))
                bundle = load_bundle(root)
            except (ImportError, OSError, TypeError) as exc:
                raise PackageError(f"{entry.name}: cannot read content resources: {exc}") from exc
            except BundleError as exc:
                raise PackageError(f"{entry.name}: installed bundle is invalid: {exc.message}", *exc.details) from exc
            if bundle.name in names:
                raise PackageError(f"duplicate installed bundle: {bundle.name}")
            names.add(bundle.name)
            package = entry.dist.metadata["Name"]
            builtin = package == BUILTIN_DISTRIBUTION
            if builtin and bundle.default_preset is None:
                raise PackageError(f"{entry.name}: a built-in bundle must declare default_preset")
            found.append(InstalledBundle(package, entry.dist.version, bundle, builtin))
        yield sorted(found, key=lambda item: item.bundle.name)
