"""devkit_spec.features.entrypoints: code entrypoints of capabilities and use cases, and their derivation from spec
bundles.

``paths`` holds the path contract (``RULE-code-entrypoints`` checks it), ``bundle`` reads a spec bundle's
declarations, ``derive`` joins them into document-code pairs and ``apply`` writes chosen pairs into frontmatter.
Libraries never print: ``devkit spec entrypoints derive`` renders the results. Contract: ``CAP-TRACE-code-entrypoints`` (``docs/capabilities/traceability/``).
"""

from devkit_spec.features.entrypoints.models.derive import Pair, Reason, SkipKind, Skipped, State
from devkit_spec.features.entrypoints.repositories.bundle import (
    Bundle,
    Target,
    TaskBoundary,
    load_bundle,
    parse_boundaries,
)
from devkit_spec.features.entrypoints.services.derive import (
    aggregate,
    classify_boundary,
    declared_entrypoints,
    derive,
    exclude,
    feedback_file,
    fold_by_directory_selectors,
    select,
)
from devkit_spec.features.entrypoints.services.paths import covers, entrypoint_bearing, exists, normalize, overlaps
from devkit_spec.features.entrypoints.usecases.apply import Applied, ApplyResult, apply, collapse, set_entrypoints

__all__ = [
    "Applied",
    "ApplyResult",
    "Bundle",
    "Pair",
    "Reason",
    "SkipKind",
    "Skipped",
    "State",
    "Target",
    "TaskBoundary",
    "aggregate",
    "apply",
    "classify_boundary",
    "collapse",
    "covers",
    "declared_entrypoints",
    "derive",
    "entrypoint_bearing",
    "exclude",
    "exists",
    "feedback_file",
    "fold_by_directory_selectors",
    "load_bundle",
    "normalize",
    "overlaps",
    "parse_boundaries",
    "select",
    "set_entrypoints",
]
