"""Guidance preserves existing envelope, commit and optional UX review contracts."""

from __future__ import annotations

import re

import yaml
from spec_support.bundle_text import raw


def test_reconcile_closure_example_uses_existing_fields_and_keeps_full_verification() -> None:
    guide = raw("skills/spec/references/review-loop.md")
    section = guide.split("### Reconcile finding closure", 1)[1].split("## 2.", 1)[0]
    assert "verify the whole reflection again" in section
    assert "`reverify --from` does not accept a reconcile-check" in section
    assert "required contract mismatch cannot be waived" in section
    assert "newly discovered finding open" in section
    assert "--kind reconcile-check --stage living-spec-draft" in section
    assert "closes reconcile-check-01" in section
    sample = section.split("<<'YAML'\n", 1)[1].split("\nYAML", 1)[0]
    findings = yaml.safe_load(sample)
    assert [item["resolution"] for item in findings] == ["resolved", "waived"]
    allowed = {"issue", "evidence", "failure_condition", "suggested_action", "severity", "resolution", "waiver"}
    for finding in findings:
        assert set(finding) <= allowed
        assert all(finding[key] for key in ("issue", "evidence", "failure_condition", "suggested_action"))
    assert findings[1]["severity"] == "P3" and findings[1]["waiver"].strip()
    assert "review-loop.md#reconcile-finding-closure" in raw("skills/spec/references/envelope.md")


def test_unexecuted_check_keeps_skip_and_exact_input_provenance() -> None:
    guide = raw("skills/spec/references/envelope.md").split("### Check provenance", 1)[1].split("## 2.", 1)[0]
    assert "`PASS` or `FAIL` only for checks the recording role executed" in guide
    assert "`SKIP` when it did not rerun" in guide
    assert "caller-supplied results as input evidence" in guide
    assert "source envelope and its exact source SHA" in guide
    assert "compare that SHA with the reviewed source" in guide
    assert "does not satisfy a required rerun" in guide
    assert re.search(r'tests=SKIP .*envelopes/green-01.yaml at [0-9a-f]{40}"', guide)


def test_feature_screens_sequence_keeps_review_evidence_with_covered_spec() -> None:
    guide = raw("skills/spec-specify/references/screens.md").split("## Feature specify commit sequence", 1)[1]
    steps = re.split(r"\n[1-5]\. ", guide)[1:]
    assert len(steps) == 5
    assert "uncommitted Screens" in steps[0]
    assert all(term in steps[1] for term in ("optional review", "last committed HEAD", "assumption", "`specify`"))
    assert steps[2].index("Fold the findings") < steps[2].index("`spec-plan`") < steps[2].index("`spec-tasks`")
    assert "RULE-task-coverage" in steps[3] and "expected to fail" in steps[3]
    assert all(term in steps[4] for term in ("`spec.md`", "`plan.md`", "`tasks.md`", "`ux-review`", "together"))
    assert "preserve the envelope's reviewed HEAD and assumption" in steps[4]
    assert "Do not commit the review record alone" in steps[4]
    assert "screens.md#feature-specify-commit-sequence" in raw("skills/spec-specify/SKILL.md")


def test_ux_implementer_closure_has_its_stage_without_adding_a_reviewer_round() -> None:
    guide = raw("skills/spec-ux-review/SKILL.md")
    assert "At most two rounds per unit for independent reviewers" in guide
    assert "optional delegation before code" in guide
    assert "--kind ux-review --stage build-verify" in guide
    assert "findings already folded into the draft" in guide
    assert "implementation verification" in guide
    assert "not another independent reviewer round" in guide
    assert "resolution: resolved" in guide and "resolution: waived" in guide and "`waiver` reason" in guide
