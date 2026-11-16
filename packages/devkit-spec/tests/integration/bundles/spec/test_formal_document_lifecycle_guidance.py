"""Source delivery assertions supplement the executed lifecycle scenarios, not semantic proof."""

from pathlib import Path

BUNDLE = Path(__file__).parents[4] / "src/devkit_spec/bundles/spec/bundle"


def test_existing_sdd_boundaries_require_change_specific_formal_comparison() -> None:
    paths = [
        "skills/spec-plan/SKILL.md",
        "skills/spec/references/planning.md",
        "skills/spec-review/SKILL.md",
        "skills/spec/references/completion.md.jinja",
        "skills/spec-sync/SKILL.md",
    ]
    for path in paths:
        text = (BUNDLE / path).read_text().lower()
        assert all(role in text for role in ("design", "domain", "operations")), path
        assert "source identity" in text and "unaffected" in text, path
    sync = (BUNDLE / paths[-1]).read_text()
    for term in (
        "Rename/root move",
        "Split",
        "Reclassify",
        "Retire",
        "old-ID alias",
        "one canonical owner",
        "ordinary",
        "historical prose",
        "source commit",
        "modified` target",
    ):
        assert term in sync


def test_entrypoint_guidance_consumes_eligibility_and_distinguishes_design_subject() -> None:
    text = " ".join((BUNDLE / "skills/spec-entrypoints/SKILL.md").read_text().split())
    assert "core eligibility" in text and "DOMAIN/OPS" in text and "README/artifact" in text
    assert "For CAP/UC" in text and "For DESIGN" in text and "helpers/models/schemas" in text
    assert "<eligible-document-id>" in text and "--target" in text and "--code" in text
    assert "canonical DESIGN" in (BUNDLE / "skills/spec-entrypoints/references/backfill.md").read_text()


def test_adoption_reuses_canonical_roles_and_requires_evidence() -> None:
    brown = (BUNDLE / "playbooks/brownfield-adoption/SKILL.md").read_text()
    assert "Canonical DESIGN/DOMAIN/OPS" in brown and "not legacy" in brown
    destinations = (BUNDLE / "playbooks/brownfield-adoption/references/migration.md").read_text()
    for role in ("Formal DOMAIN", "Formal DESIGN", "Formal OPS"):
        assert role in destinations
    baseline = (BUNDLE / "playbooks/sdd-baseline/SKILL.md").read_text()
    report = (BUNDLE / "playbooks/sdd-baseline/references/report-template.md").read_text()
    assert "DOMAIN, DESIGN and OPS" in baseline and "missing required documents" in baseline.lower()
    assert "changed source invalidates" in report and "gaps" in report
