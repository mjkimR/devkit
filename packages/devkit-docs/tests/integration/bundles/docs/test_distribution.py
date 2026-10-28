"""Independent document assets and real selection transactions."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from importlib.metadata import entry_points
from pathlib import Path

from devkit_dist.features.distribution.services.bundles import load_bundle

BUNDLE = Path(__file__).resolve().parents[4] / "src/devkit_docs/bundles/docs/bundle"
RULES = {
    "document-reference",
    "id-convention",
    "spec-format",
    "traceability-link",
    "document-summary",
    "steering-documents",
    "ux-links",
    "ux-coverage",
    "code-entrypoints",
}


def invoke(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("DEVKIT_")}
    result = subprocess.run(
        [sys.executable, "-m", "devkit_dist", *args, "-w", str(root)],
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result


def test_inventory_and_guidance_have_independent_ownership() -> None:
    bundle = load_bundle(BUNDLE)
    assert bundle.auto_select and bundle.name == "docs" and bundle.default_preset == "core"
    assert {a.id for a in bundle.assets if a.kind == "rule"} == RULES
    assert len([a for a in bundle.assets if a.kind == "instruction"]) == 8
    assert not {"docs-skeleton"} & set(bundle.select(["core"]))
    assert {p.stem for p in (BUNDLE / "templates").glob("*.md")} == {
        "capability",
        "usecase",
        "ux",
        "decision",
        "milestone",
    }
    assert next(iter(entry_points(group="devkit.bundles", name="docs"))).value == "devkit_docs.bundles.docs"
    for parent in ["instructions", "templates", "seed"]:
        for source in (BUNDLE / parent).rglob("*.md"):
            body = source.read_text()
            for marker in [
                "`/spec",
                "requires prior ADR",
                "`spec-sync`",
                "`plan-intent`",
                "devkit spec proposal",
                "spec:docs-skeleton",
                ".devkit/managed/spec/",
            ]:
                assert marker not in body, (source, marker)
    spec = BUNDLE.parents[5] / "devkit-spec/src/devkit_spec/bundles/spec/bundle"
    # Existing SDD history obligations remain explicit on the lifecycle side.
    constitution = (spec / "AGENTS.md.jinja").read_text()
    assert "a changed decision is a new ADR" in constitution
    assert "stays in place as history" in constitution


def test_selection_round_trip_and_project_owned_seed_bytes(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    invoke(tmp_path, "sync")
    assert not (tmp_path / "docs").exists()
    assert (tmp_path / ".devkit/managed/docs/templates/decision.md").exists()
    invoke(tmp_path, "add", "docs:docs-skeleton")
    seed = tmp_path / "docs/README.md"
    seed.write_text(seed.read_text() + "\nProject-owned bytes.\n")
    expected = seed.read_bytes()
    invoke(tmp_path, "remove", "spec")
    assert not (tmp_path / ".devkit/managed/spec").exists()
    assert not (tmp_path / ".agents/skills/spec/SKILL.md").exists()
    assert (tmp_path / ".devkit/managed/docs/AGENTS.md").exists()
    guidance = (tmp_path / "AGENTS.md").read_text()
    assert "get-context docs" in guidance and "Start work with `/spec" not in guidance
    invoke(tmp_path, "remove", "docs")
    invoke(tmp_path, "add", "docs")
    invoke(tmp_path, "add", "docs:docs-skeleton")
    invoke(tmp_path, "add", "spec")
    assert seed.read_bytes() == expected
    assert (tmp_path / ".agents/skills/spec/SKILL.md").exists()
    docs_context = json.loads(invoke(tmp_path, "get-context", "docs").stdout)
    spec_context = json.loads(invoke(tmp_path, "get-context", "spec").stdout)
    assert len(docs_context["documents"]) == 1
    assert spec_context["documents"] == []
