"""The package wiring: the ``spec`` bundle and the ``devkit spec`` command group, as devkit sees them."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tomllib
from importlib.metadata import entry_points
from pathlib import Path

from click.testing import CliRunner
from devkit_dist.cli import COMMANDS
from devkit_dist.cli import cli as devkit_cli
from devkit_dist.features.distribution import load_bundle

from devkit_spec.features.documents import DocumentIndex

ROOT = Path(__file__).resolve().parents[3]
BUNDLE = ROOT / "src/devkit_spec/bundles/spec/bundle"
RULES = (
    "RULE-document-reference",
    "RULE-id-convention",
    "RULE-spec-format",
    "RULE-traceability-link",
    "RULE-task-coverage",
    "RULE-spec-lifecycle",
    "RULE-reconcile-contract",
    "RULE-code-entrypoints",
    "RULE-proposal-boundaries",
    "RULE-document-summary",
)
# The instructions holding each rule's judgment (``related``); the other rules declare none.
RELATED = {
    "RULE-document-reference": ("spec:living-spec-writing",),
    "RULE-id-convention": ("spec:living-spec-writing",),
    "RULE-traceability-link": ("spec:living-spec-writing",),
    "RULE-spec-lifecycle": ("spec:living-spec-writing",),
    "RULE-document-summary": ("spec:living-spec-writing",),
    "RULE-task-coverage": ("spec:contract-authoring",),
}
PYPROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def test_the_bundle_loads_with_the_package_version() -> None:
    bundle = load_bundle(BUNDLE)
    assert bundle.name == "spec" and bundle.auto_select and bundle.default_preset in bundle.presets
    assert bundle.version == PYPROJECT["project"]["version"]


def test_the_entry_points_are_installed() -> None:
    (bundle,) = entry_points(group="devkit.bundles", name="spec")
    (command,) = entry_points(group="devkit.commands", name="spec")
    (template,) = entry_points(group="devkit.config_template", name="spec")
    (readiness,) = entry_points(group="devkit.integration.readiness", name="spec")
    (post_finish,) = entry_points(group="devkit.post_finish", name="spec")
    assert (bundle.value, command.value, template.value, readiness.value, post_finish.value) == (
        "devkit_spec.bundles.spec",
        "devkit_spec.cli:cli",
        "devkit_spec.features.policy.services.config:template",
        "devkit_spec.features.delivery.usecases.integration",
        "devkit_spec.features.delivery.usecases.cleanup:after_finish",
    )


def test_spec_is_not_a_built_in_devkit_command() -> None:
    assert "spec" not in COMMANDS  # a built-in name would shadow the plugin


def test_devkit_mounts_the_spec_group() -> None:
    result = CliRunner().invoke(devkit_cli, ["spec", "--version"])
    assert (result.exit_code, result.output) == (0, f"[VERSION: devkit-spec {PYPROJECT['project']['version']}]\n")


def _devkit(*args: str) -> subprocess.CompletedProcess[str]:
    env = {key: value for key, value in os.environ.items() if not key.startswith("DEVKIT_")}
    return subprocess.run(
        [sys.executable, "-m", "devkit_dist", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )


def test_devkit_sync_deploys_the_default_preset_and_its_rules_run(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    result = _devkit("sync", "-w", str(tmp_path))
    assert result.returncode == 0, result.stderr
    assert (tmp_path / ".devkit/managed/spec/instructions/contract-authoring.md").is_file()
    doc = tmp_path / "docs/capabilities/core/CAP-CORE-a.md"
    doc.parent.mkdir(parents=True)
    doc.write_text("---\nid: CAP-CORE-a\nstatus: active\n---\nSee `US-missing`.\n", encoding="utf-8")
    check = _devkit("rules", "check", "-w", str(tmp_path))
    assert check.returncode == 1, check.stderr
    assert "RULE-document-reference" in check.stdout and "no document has the ID US-missing" in check.stdout
    for rule in RULES:
        explain = _devkit("rules", "explain", rule, "-w", str(tmp_path))
        assert explain.returncode == 0 and f"# [{rule}] " in explain.stdout, explain.stderr
        for ref in RELATED.get(rule, ()):
            name = ref.split(":", 1)[1]
            line = f"[RELATED: {ref} kind=instruction path=.devkit/managed/spec/instructions/{name}.md]"
            assert line in explain.stdout, explain.stdout


def test_devkit_config_template_writes_the_spec_tables(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    result = _devkit("config", "template", "-w", str(tmp_path))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["notices"] == []
    assert {"tool.spec", "tool.spec.namespaces", "tool.spec.scope"} <= set(payload["added"])
    text = (tmp_path / ".devkit/config.toml").read_text(encoding="utf-8")
    assert (
        '# [tool.spec]\n#   worktree = "auto"  # "auto" | "required";' in text and "# [[tool.spec.namespaces]]" in text
    )
    assert tomllib.loads(text) == {"schema": 1}  # every line it wrote is a comment


def test_the_docs_skeleton_is_opt_in_and_passes_the_rules(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    assert _devkit("sync", "-w", str(tmp_path)).returncode == 0
    assert not (tmp_path / "docs").exists()
    added = _devkit("add", "spec:docs-skeleton", "-w", str(tmp_path))
    assert added.returncode == 0, added.stderr
    assert (tmp_path / "docs/architecture/ARCH-01-introduction-and-goals.md").is_file()
    assert (tmp_path / "docs/glossary.yaml").is_file()
    assert "| Term | Definition | Owner | Avoid | Code identifiers |" in (tmp_path / "docs/glossary.md").read_text()
    index = DocumentIndex.load(tmp_path)
    assert not index.problems, index.problems
    for source in (BUNDLE / "seed/docs/architecture").glob("ARCH-*.md"):
        assert index.resolve(source.stem).path == f"docs/architecture/{source.name}"
    existing = tmp_path / "docs/architecture/ARCH-01-introduction-and-goals.md"
    customized = existing.read_text(encoding="utf-8") + "\nProject-owned content.\n"
    existing.write_text(customized, encoding="utf-8")
    synced = _devkit("sync", "-w", str(tmp_path))
    assert synced.returncode == 0, synced.stderr
    assert existing.read_text(encoding="utf-8") == customized
    check = _devkit("rules", "check", "-w", str(tmp_path))
    assert check.returncode == 0, check.stdout


def test_roadmap_template_and_guidance_are_packaged() -> None:
    template = (BUNDLE / "templates/milestone.md").read_text()
    assert "status: planned" in template and "depends_on: []" in template
    backlog = (BUNDLE / "skills/spec/references/backlog.md.jinja").read_text()
    selection = (BUNDLE / "skills/spec-next/references/next-work.md").read_text()
    assert "--decomposed-from" in backlog and "[milestone completion](milestone-completion.md)" in backlog
    assert "devkit spec list milestone --all-namespaces -n 0" in selection
    assert (BUNDLE / "seed/docs/roadmap/README.md").is_file()
