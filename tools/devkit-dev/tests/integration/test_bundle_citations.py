"""Shipped bundle text cites no document ID of this repository.

Bundles ship to projects without this repository's ``docs/``, so a backticked ID that resolves only here dangles
there (the ``authoring`` bundle's ``agent-asset-writing`` instruction, Self-Containment). Placeholders and examples
resolve to nothing; documents a shipped bundle seeds exist in the consuming project. The repository-only
``devkit-dev`` bundle under ``tools/`` is exempt.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

# Static imports of every shipping module: a change to their sources selects this test in `just test-affected`.
import devkit_agt.bundles
import devkit_catalog
import devkit_dist.bundles
import devkit_docs.bundles
import devkit_spec.bundles
import devkit_starter
from devkit_docs.features.documents.models.ids import ID_SOURCE
from devkit_docs.features.documents.repositories.index import DocumentIndex

ROOT = Path(__file__).resolve().parents[4]
SHIPPING = (
    devkit_agt.bundles,
    devkit_catalog,
    devkit_dist.bundles,
    devkit_docs.bundles,
    devkit_spec.bundles,
    devkit_starter,
)
SPAN = re.compile(r"`([^`\n]+)`")
CITED_ID = re.compile(rf"(?<![\w<-])({ID_SOURCE})")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---", re.DOTALL)
DECLARED_ID = re.compile(r"^id:\s*['\"]?([^\s'\"]+)", re.MULTILINE)


def shipped_bundles() -> list[Path]:
    """The bundle directories (``bundle.toml`` parents) under the shipping modules."""
    found: set[Path] = set()
    for module in SHIPPING:
        assert module.__file__ is not None
        found.update(manifest.parent for manifest in Path(module.__file__).parent.rglob("bundle.toml"))
    return sorted(found)


def seeded_ids(bundles: list[Path]) -> set[str]:
    """The IDs of the documents the bundles seed into a consuming project."""
    ids: set[str] = set()
    for bundle in bundles:
        manifest = tomllib.loads((bundle / "bundle.toml").read_text(encoding="utf-8"))
        for asset in manifest.get("assets", []):
            if asset.get("kind") != "document" or not asset.get("seeded"):
                continue
            source = bundle / asset["source"]
            for path in [source] if source.is_file() else sorted(source.rglob("*.md")):
                frontmatter = FRONTMATTER.match(path.read_text(encoding="utf-8"))
                if frontmatter and (declared := DECLARED_ID.search(frontmatter.group(1))):
                    ids.add(declared.group(1))
    return ids


def repository_ids(root: Path) -> set[str]:
    """Every document ID and alias of ``root``'s ``docs/`` and ``specs/``; the parse memo is read, never written."""
    files = sorted(path for directory in ("docs", "specs") for path in (root / directory).rglob("*.md"))
    index = DocumentIndex.load(root, files=files)
    return set(index.by_id) | set(index.by_alias)


def citations(bundle: Path, forbidden: set[str], root: Path) -> list[str]:
    """``<path>:<line>: <ID>`` for each backticked forbidden ID in the bundle's text files."""
    findings: list[str] = []
    for path in sorted(bundle.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(text.splitlines(), 1):
            for span in SPAN.finditer(line):
                for match in CITED_ID.finditer(span.group(1)):
                    if match.group(1) in forbidden:
                        findings.append(f"{path.relative_to(root).as_posix()}:{number}: {match.group(1)}")
    return findings


def test_shipped_bundles_cite_no_repository_document_id() -> None:  # AC-01
    bundles = shipped_bundles()
    forbidden = repository_ids(ROOT) - seeded_ids(bundles)
    findings = [finding for bundle in bundles for finding in citations(bundle, forbidden, ROOT)]
    assert not findings, "\n".join(findings)


def test_every_shipped_bundle_is_scanned() -> None:  # AC-03
    expected = {manifest.parent for manifest in ROOT.glob("packages/*/src/**/bundle.toml")}
    assert set(shipped_bundles()) == expected
    assert not [bundle for bundle in shipped_bundles() if "tools" in bundle.relative_to(ROOT).parts]


def test_a_resolving_citation_is_reported_and_placeholders_pass(tmp_path: Path) -> None:  # AC-02
    bundle = tmp_path / "bundle"
    (bundle / "seed" / "docs").mkdir(parents=True)
    (bundle / "bundle.toml").write_text(
        'schema = 1\nname = "x"\n\n[[assets]]\nid = "seed"\nkind = "document"\nseeded = true\nsource = "seed/docs"\n'
    )
    (bundle / "seed" / "docs" / "ARCH-01-goals.md").write_text("---\nid: ARCH-01-goals\n---\n")
    (bundle / "guide.md").write_text(
        "Placeholders `ADR-<slug>`, `CAP-<AREA>-<slug>` and `RULE-example`.\n"
        "Examples `ADR-example`, `UC-010` and `MS-release-1-0`.\n"
        "The seeded `ARCH-01-goals`.\n"
        "Plain CAP-DIST-real is not a citation.\n"
        "See `devkit docs resolve CAP-DIST-real` for the contract.\n"
    )
    forbidden = {"CAP-DIST-real", "ARCH-01-goals"} - seeded_ids([bundle])
    assert citations(bundle, forbidden, tmp_path) == ["bundle/guide.md:5: CAP-DIST-real"]
