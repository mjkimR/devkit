"""Bundle sources: ``bundle.toml`` loading and validation, per-kind asset readers, and archive packaging."""

from devkit_dist.features.distribution.services.bundles.manifest import Asset, Bundle, load_bundle
from devkit_dist.features.distribution.services.bundles.package import BuildResult, build_bundle

__all__ = ["Asset", "BuildResult", "Bundle", "build_bundle", "load_bundle"]
