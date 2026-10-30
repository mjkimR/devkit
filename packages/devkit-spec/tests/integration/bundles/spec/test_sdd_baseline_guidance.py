"""Mechanical baseline entry and report contracts; semantic adoption waits on prerequisite exercises."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from devkit_dist.features.distribution.services.bundles import load_bundle
from distsupport.guidance import assert_rule
from spec_support.bundle_text import BUNDLE, raw, text

ENTRY = "playbooks/sdd-baseline/SKILL.md"


def test_baseline_is_a_core_playbook_with_its_own_report_reference() -> None:
    bundle = load_bundle(BUNDLE)
    asset = next(asset for asset in bundle.assets if asset.id == "sdd-baseline")
    assert asset.kind == "playbook"
    assert "sdd-baseline" in bundle.select(["core"])
    entry = raw(ENTRY)
    references = re.findall(r"\]\((references/[^)]+)\)", entry)
    assert references == ["references/report-template.md"]
    assert all((BUNDLE / "playbooks/sdd-baseline" / reference).is_file() for reference in references)
    assert not list((BUNDLE / "playbooks/sdd-baseline").rglob("*.py"))


def test_synced_consumer_discovers_entry_and_report_without_creating_a_unit(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    env = {key: value for key, value in os.environ.items() if not key.startswith("DEVKIT_")}

    def invoke(*args: str) -> str:
        result = subprocess.run(
            [sys.executable, "-m", "devkit_dist", *args, "-w", str(tmp_path)],
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        return result.stdout

    invoke("sync")
    entry = json.loads(invoke("playbook", "get", "spec/sdd-baseline"))
    assert entry["bundle"] == "spec" and entry["id"] == "sdd-baseline"
    deployed = Path(entry["source"]["path"])
    assert deployed == tmp_path / ".devkit/managed/spec/playbooks/sdd-baseline/SKILL.md"
    assert (deployed.parent / "references/report-template.md").is_file()
    found = json.loads(invoke("playbook", "search", "adopt SDD from adaptive-dev baseline", "--mode", "lexical"))
    assert any(item["bundle"] == "spec" and item["id"] == "sdd-baseline" for item in found["results"])
    assert not (tmp_path / "specs").exists()
    assert not (tmp_path / "docs/materials").exists()
    invoke("sync", "--check")


def test_guidance_orders_evidence_before_activation_and_preserves_current_state() -> None:
    body = raw(ENTRY)
    assert body.index("## 2. Compare") < body.index("## 3. Activate")
    assert_rule(body, "use only when", "invokes or confirms", "adopt SDD")
    assert_rule(body, "keep", "effective approach", "adaptive-dev", "preparation")
    assert_rule(body, "never waive", "required retained behavior", "required evidence", "readiness")
    assert_rule(body, "recheck", "source", "dirty paths", "invalidate")
    assert_rule(body, "reuse", "explicit user decision", "same source and effects")
    assert_rule(body, "edit only", "`.devkit/config.toml`", '`[development] approach = "sdd"`')
    assert_rule(body, "provider", "absent or `project`", "configuring `spec`", "necessary activation effect")
    assert_rule(body, "provider change", "not authorized", "report the mismatch", "do not claim")
    assert_rule(body, "neither", "successful adoption", "automatic rollback")
    assert_rule(
        body, "create no", "retrospective", "proposal", "spec Unit", "workflow approval", "envelope", "ADR", "discarded"
    )
    flat_body = text(ENTRY)
    assert "uv run devkit spec new" not in flat_body
    assert "uv run devkit workflow envelope" not in flat_body
    report = raw("playbooks/sdd-baseline/references/report-template.md")
    assert "<verified/gap/excluded>" in report
    assert_rule(report, "actual", "policy/asset inspection", "after activation")
    assert_rule(report, "real", "simulated decisions")
