"""Read the ``spec`` bundle's source documents as an installed environment renders them.

Guidance tests pin wording, not line layout: phrase assertions run against ``text()``, which collapses every
whitespace run, and ``raw()`` stays for structure (frontmatter, headings, table rows, links, byte budgets).
"""

from __future__ import annotations

from pathlib import Path

from devkit_dist.features.distribution.services.bundles.templates import render_template

DOCS = Path(__file__).resolve().parents[4] / "devkit-docs/src/devkit_docs/bundles/docs/bundle"

BUNDLE = Path(__file__).resolve().parents[3] / "src/devkit_spec/bundles/spec/bundle"


def raw(path: str | Path, environment: str = "local") -> str:
    """The document's rendered text; a bundle-relative path or a missing file falls back to its ``.jinja`` source."""
    if isinstance(path, str):
        shared = path.startswith(("instructions/", "seed/")) or (
            path.startswith("templates/") and path != "templates/proposal.md"
        )
        source = (DOCS if shared else BUNDLE) / path
    else:
        source = path
    if not source.exists():
        source = source.with_name(source.name + ".jinja")
    data = source.read_bytes()
    if source.name.endswith(".jinja"):
        data = render_template(data, {}, str(source), environment=environment)
    return data.decode("utf-8")


def flat(value: str) -> str:
    """``value`` with every whitespace run collapsed to one space, so a rewrapped phrase still matches."""
    return " ".join(value.split())


def text(path: str | Path, environment: str = "local") -> str:
    """The document's rendered text with whitespace collapsed by ``flat``."""
    return flat(raw(path, environment))
