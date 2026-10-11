from __future__ import annotations

from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from importlib import metadata, resources

from devkit_distribution.bundles import Bundle, BundleError, load_bundle

GROUP = "devkit_distribution.bundles"


@dataclass(frozen=True)
class InstalledBundle:
    package: str
    package_version: str
    bundle: Bundle


@contextmanager
def discover_bundles() -> Iterator[list[InstalledBundle]]:
    """Keep resource materializations alive for the whole sync operation."""
    found = []
    names: set[str] = set()
    with ExitStack() as stack:
        for entry in sorted(metadata.entry_points(group=GROUP), key=lambda item: (item.name, item.value)):
            if entry.attr is not None or entry.extras or entry.dist is None:
                raise BundleError(f"{entry.name}: bundle entry point must reference a resource module")
            try:
                root = stack.enter_context(resources.as_file(resources.files(entry.module).joinpath("bundle")))
                bundle = load_bundle(root)
            except (ImportError, OSError, TypeError) as exc:
                raise BundleError(f"{entry.name}: cannot read content resources: {exc}") from exc
            if bundle.name in names:
                raise BundleError(f"duplicate installed bundle: {bundle.name}")
            names.add(bundle.name)
            found.append(InstalledBundle(entry.dist.metadata["Name"], entry.dist.version, bundle))
        yield sorted(found, key=lambda item: item.bundle.name)
