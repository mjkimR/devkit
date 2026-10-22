"""Shared artifact guidance preserves the explicit connection precondition."""

from pathlib import Path


def test_local_orchestration_requires_project_connection():
    bundle = Path(__file__).resolve().parents[4] / "src/devkit_spec/bundles/spec/bundle/skills"
    text = _rendered(bundle / "spec-orchestrate/SKILL.md")
    assert "shared_put" in text and "shared_sweep_apply" in text
    assert "stop that operation; do not fall back to CLI unless the user chooses an authorized CLI route" in text


def _rendered(path: Path) -> str:
    from devkit_dist.features.distribution.services.bundles.templates import render_template

    if path.name.endswith(".md.jinja"):
        return render_template(path.read_bytes(), {}, str(path), environment="local").decode()
    if path.exists():
        return path.read_text(encoding="utf-8")
    source = path.with_name(path.name + ".jinja")
    return render_template(source.read_bytes(), {}, str(source), environment="local").decode()
