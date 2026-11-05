"""Generate wheel URL closures for every supported release installation variant."""

from __future__ import annotations

import re

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

from .identity import require

VARIANTS = {
    "harness": {"devkit-agt": set()},
    "distribution": {"devkit-dist": set()},
    "search": {"devkit-agt": {"search"}},
    "mcp": {"devkit-mcp": set()},
    "sdd": {"devkit-spec": set()},
    "viewer": {"devkit-viewer": set()},
    "tool": {"devkit-dist": set(), "devkit-agt": set()},
    "advisory": {"devkit-advisory": set()},
    "cli": {"devkit-cli": set()},
}


def closure(data: dict, roots: dict[str, set[str]]) -> list[str]:
    entries = {**data["packages"], **data["extras"]}
    selected = {name: set(extras) for name, extras in roots.items()}
    previous = None
    while previous != selected:
        previous = {name: set(extras) for name, extras in selected.items()}
        for name, extras in previous.items():
            require(name in entries, "missing installation artifact: " + name)
            for raw in entries[name].get("requires", []):
                req = Requirement(raw)
                dep = canonicalize_name(req.name)
                if dep not in entries:
                    continue
                # Preserve platform-conditioned runtime closure on every target platform.
                # Core Metadata's optional dependencies use standardized extra equality markers.
                optional = set(re.findall(r'extra\s*==\s*["\']([^"\']+)["\']', str(req.marker or "")))
                if optional and not (optional & extras):
                    continue
                selected.setdefault(dep, set()).update(req.extras)
    return [
        f"{name}" + (f"[{','.join(sorted(extras))}]" if extras else "") + f" @ {entries[name]['artifact']['url']}"
        for name, extras in sorted(selected.items())
    ]


def commands(data: dict) -> dict[str, str]:
    result = {}
    for variant, roots in VARIANTS.items():
        if not roots.keys() <= data["packages"].keys():
            continue
        requirements = closure(data, roots)
        if variant == "tool":
            owner = next(r for r in requirements if r.startswith("devkit-dist @"))
            result[variant] = (
                'uv tool install "' + owner + '"' + "".join(' --with "' + r + '"' for r in requirements if r != owner)
            )
        else:
            prefix = "uv add " if variant in {"advisory", "cli"} else "uv add --dev "
            result[variant] = prefix + " ".join('"' + r + '"' for r in requirements)
    return result


def notes(data: dict) -> str:
    return (
        "# Install\n\nUse the complete inventory-selected wheel set.\n\n```bash\n"
        + "\n\n".join("# " + variant + "\n" + command for variant, command in commands(data).items())
        + "\n```\n\nChecksums: `SHA256SUMS`; full provenance: `release-inventory.json`.\n"
    )
