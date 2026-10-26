"""The handbook script (`scripts/handbook.py`, CAP-DLV-release-handbook) on a Git repository with a small Living Spec.

Each test builds the repository, writes a complete handbook through the script and changes one thing.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tomllib
from pathlib import Path
from types import ModuleType

import pytest
from click.testing import CliRunner, Result

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / "scripts/handbook.py"
REPOSITORY = "owner/devkit"
DATE = "2026-10-26"


def load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("handbook_script", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses resolve their module by name
    spec.loader.exec_module(module)
    return module


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def write(root: Path, files: dict[str, str]) -> None:
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def commit(root: Path, message: str = "change") -> str:
    git(root, "add", "-A", "docs", "VERSION")
    git(root, "commit", "-q", "-m", message)
    return git(root, "rev-parse", "HEAD").strip()


def doc(identifier: str, title: str, body: str = "Body.", **fields: str) -> str:
    extra = "".join(f"{key}: {value}\n" for key, value in fields.items())
    return f"---\nid: {identifier}\ntitle: {title}\nsummary: The {title.lower()}.\n{extra}---\n\n# {title}\n\n{body}\n"


GLOSSARY = """# Glossary

## 1. Distribution

| Term | Definition | Owner | Avoid | Code identifiers |
| :--- | :--- | :--- | :--- | :--- |
| **Bundle** | A unit of agent assets. | `CAP-DIST-bundles` |  | `bundle.toml` |
"""

LIVING_SPEC = {
    "VERSION": "0.2.0\n",
    "docs/usecases/delivery/UC-ship-a-change.md": doc("UC-ship-a-change", "Ship a change", status="active"),
    "docs/capabilities/distribution/CAP-DIST-bundles.md": doc("CAP-DIST-bundles", "Bundles", status="active"),
    "docs/decisions/2026-10/20261026-first.md": doc("ADR-first", "First decision", status="accepted"),
    "docs/glossary.md": GLOSSARY,
}

EN_README = """---
sources:
  UC-ship-a-change: ''
  CAP-DIST-bundles: ''
---
# devkit handbook

devkit distributes agent assets; run `devkit sync` after selecting bundles.

## Pages

<!-- handbook:generated toc -->
<!-- /handbook:generated -->

## Journeys

<!-- handbook:generated usecases -->
<!-- /handbook:generated -->
"""

KO_README = """# devkit 핸드북

devkit은 에이전트 자산을 배포합니다. 번들을 고른 뒤 `devkit sync`를 실행합니다.

## 페이지

<!-- handbook:generated toc -->
<!-- /handbook:generated -->

## 여정

<!-- handbook:generated usecases -->
<!-- /handbook:generated -->
"""

HANDBOOK = {
    "handbook/en/README.md": EN_README,
    "handbook/ko/README.md": KO_README,
    "handbook/ko/terms.yaml": "Bundle: 번들\n",
}


def run(script: ModuleType, root: Path, *args: str) -> Result:
    return CliRunner().invoke(script.main, ["-w", str(root), *args], catch_exceptions=False)


def make_repository(root: Path) -> str:
    """A committed Living Spec with an origin remote; returns HEAD."""
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init", "-q", "-b", "main")
    git(root, "remote", "add", "origin", f"https://github.com/{REPOSITORY}.git")
    write(root, LIVING_SPEC)
    return commit(root, "living spec")


def make_handbook(script: ModuleType, root: Path) -> None:
    """A complete, verified handbook: written, generated and stamped."""
    write(root, HANDBOOK)
    assert run(script, root, "generate", "--date", DATE).exit_code == 0
    assert run(script, root, "stamp", "en/README.md").exit_code == 0
    assert run(script, root, "stamp", "ko/README.md").exit_code == 0


def lines(result: Result) -> list[str]:
    return result.stdout.splitlines()


@pytest.fixture
def script() -> ModuleType:
    return load_script()


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    root = tmp_path / "repo"
    make_repository(root)
    return root


@pytest.fixture
def handbook(script: ModuleType, repo: Path) -> Path:
    make_handbook(script, repo)
    return repo


# --- status (AC-01 to AC-04) -----------------------------------------------------------------------------------------


def test_a_complete_handbook_reports_no_finding(script, handbook):
    result = run(script, handbook, "status")
    assert result.exit_code == 0, result.stdout
    assert lines(result) == ["[HANDBOOK_STATUS: tag=v0.2.0 stale=0 translations=0 gaps=0 parity=0 terms=0]"]


def test_a_changed_source_marks_its_english_page_stale(script, handbook):
    write(handbook, {"docs/usecases/delivery/UC-ship-a-change.md": doc("UC-ship-a-change", "Ship", "Changed.")})
    commit(handbook)
    result = run(script, handbook, "status")
    assert result.exit_code == 1
    assert "[HANDBOOK_STALE: page=en/README.md sources=UC-ship-a-change]" in lines(result)
    assert "stale=1" in lines(result)[-1]


def test_stamping_a_stale_page_records_the_current_sources(script, handbook):
    write(handbook, {"docs/usecases/delivery/UC-ship-a-change.md": doc("UC-ship-a-change", "Ship", "Changed.")})
    commit(handbook)
    assert lines(run(script, handbook, "stamp", "en/README.md")) == ["[HANDBOOK_STAMPED: page=en/README.md]"]
    assert run(script, handbook, "status").exit_code == 0


def test_a_header_only_english_change_keeps_translations_fresh(script, handbook):
    write(handbook, {"VERSION": "0.3.0\n"})
    commit(handbook)
    assert run(script, handbook, "generate", "--date", "2027-01-01").exit_code == 0
    assert "v0.3.0" in (handbook / "handbook/en/README.md").read_text()
    result = run(script, handbook, "status")
    assert result.exit_code == 0, result.stdout


def test_a_narrative_english_change_marks_the_translation_stale(script, handbook):
    page = handbook / "handbook/en/README.md"
    page.write_text(page.read_text().replace("distributes agent assets", "distributes and projects agent assets"))
    result = run(script, handbook, "status")
    assert result.exit_code == 1
    assert "[HANDBOOK_TRANSLATION_STALE: page=ko/README.md source=en/README.md]" in lines(result)


def test_an_uncited_use_case_or_capability_is_a_gap(script, handbook):
    write(
        handbook,
        {
            "docs/usecases/delivery/UC-review-a-change.md": doc("UC-review-a-change", "Review", status="active"),
            "docs/capabilities/gate/CAP-GATE-old.md": doc("CAP-GATE-old", "Old", status="deprecated"),
        },
    )
    commit(handbook)
    result = run(script, handbook, "status")
    assert "[HANDBOOK_GAP: id=UC-review-a-change kind=usecase]" in lines(result)
    assert not any("CAP-GATE-old" in line for line in lines(result))


def test_missing_and_extra_translations_are_parity_mismatches(script, handbook):
    write(handbook, {"handbook/en/concepts.md": "# Concepts\n\nText.\n", "handbook/ko/extra.md": "# 추가\n"})
    result = run(script, handbook, "status")
    assert "[HANDBOOK_PARITY: page=ko/concepts.md problem=missing]" in lines(result)
    assert "[HANDBOOK_PARITY: page=ko/extra.md problem=extra]" in lines(result)
    verified = run(script, handbook, "verify")
    assert verified.exit_code == 1
    assert sum("code=HANDBOOK_PARITY" in line for line in lines(verified)) == 2


def test_a_glossary_term_without_a_rendering_is_reported(script, handbook):
    (handbook / "handbook/ko/terms.yaml").write_text("{}\n")
    result = run(script, handbook, "status")
    assert '[HANDBOOK_TERM_MISSING: lang=ko term="Bundle"]' in lines(result)


# --- verify (AC-05) --------------------------------------------------------------------------------------------------


def test_a_complete_handbook_verifies(script, handbook):
    head = git(handbook, "rev-parse", "HEAD").strip()
    result = run(script, handbook, "verify")
    assert result.exit_code == 0, result.stdout
    assert lines(result) == [f"[HANDBOOK_VERIFIED: tag=v0.2.0 commit={head} pages=8]"]


@pytest.mark.parametrize(
    ("narrative", "code"),
    [
        ("See `CAP-DIST-missing`.", "HANDBOOK_ID_UNRESOLVED"),
        ("Run `devkit no-such-command`.", "HANDBOOK_COMMAND_UNKNOWN"),
        ("Run `devkit sync --no-such-option`.", "HANDBOOK_COMMAND_UNKNOWN"),
        (f"[Gone](https://github.com/{REPOSITORY}/blob/v0.2.0/docs/gone.md)", "HANDBOOK_SOURCE_MISSING"),
        (f"[Main](https://github.com/{REPOSITORY}/blob/main/docs/glossary.md)", "HANDBOOK_LINK_REF"),
        ("Readers MUST read this.", "HANDBOOK_NORMATIVE_KEYWORD"),
        ("[Next](missing.md)", "HANDBOOK_LINK_BROKEN"),
    ],
)
def test_verification_rejects_an_inaccurate_page(script, handbook, narrative, code):
    write(handbook, {"handbook/en/concepts.md": f"# Concepts\n\n{narrative}\n", "handbook/ko/concepts.md": "# 개념\n"})
    run(script, handbook, "stamp", "ko/concepts.md")
    result = run(script, handbook, "verify")
    assert result.exit_code == 1
    findings = [line for line in lines(result) if line.startswith("[HANDBOOK_INVALID:")]
    assert [line for line in findings if "page=en/concepts.md" in line] == [
        line for line in findings if f"code={code}" in line
    ]
    assert any(f"page=en/concepts.md line=3 code={code}" in line for line in findings), findings


def test_normative_keywords_inside_code_are_allowed(script, handbook):
    write(handbook, {"handbook/en/concepts.md": "# Concepts\n\nThe word `MUST` is quoted.\n"})
    write(handbook, {"handbook/ko/concepts.md": "# 개념\n"})
    run(script, handbook, "stamp", "ko/concepts.md")
    result = run(script, handbook, "verify")
    assert result.exit_code == 0, result.stdout


def test_a_preview_accepts_links_pinned_to_the_upcoming_tag(script, handbook):
    link = f"[Glossary](https://github.com/{REPOSITORY}/blob/v0.2.0/docs/glossary.md)"
    write(handbook, {"handbook/en/concepts.md": f"# Concepts\n\n{link}\n", "handbook/ko/concepts.md": "# 개념\n"})
    run(script, handbook, "stamp", "ko/concepts.md")
    assert run(script, handbook, "generate", "--preview", "--date", DATE).exit_code == 0
    result = run(script, handbook, "verify", "--preview")
    assert result.exit_code == 0, result.stdout


def test_an_unclosed_block_stops_generation_before_any_write(script, handbook):
    page = handbook / "handbook/en/README.md"
    text = page.read_text().replace(
        "<!-- handbook:generated usecases -->\n", "<!-- handbook:generated usecases -->\nKept.\n"
    )
    text = text.rsplit("<!-- /handbook:generated -->", 1)[0] + "More narrative.\n"
    page.write_text(text)
    before = _files(handbook)
    result = CliRunner().invoke(script.main, ["-w", str(handbook), "generate", "--date", "2027-01-01"])
    assert result.exit_code == 2
    assert "HANDBOOK_BLOCK_UNCLOSED" in result.stderr
    assert _files(handbook) == before
    verified = run(script, handbook, "verify")
    assert any("code=HANDBOOK_BLOCK_UNCLOSED" in line for line in lines(verified))


def test_verification_without_a_manifest_cannot_run(script, repo):
    result = CliRunner().invoke(script.main, ["-w", str(repo), "verify"])
    assert result.exit_code == 2
    assert "HANDBOOK_MANIFEST_INVALID" in result.stderr


# --- generate (AC-06, AC-07) -----------------------------------------------------------------------------------------


def test_generation_writes_manifest_provenance_and_generated_pages(script, handbook):
    head = git(handbook, "rev-parse", "HEAD").strip()
    manifest = json.loads((handbook / "handbook/manifest.json").read_text())
    assert manifest == {
        "tag": "v0.2.0",
        "source_commit": head,
        "repository": REPOSITORY,
        "langs": ["en", "ko"],
        "generated": DATE,
    }
    readme = (handbook / "handbook/en/README.md").read_text()
    assert f"devkit `v0.2.0` at source commit `{head[:12]}`, generated {DATE}" in readme
    assert f"[`UC-ship-a-change`](https://github.com/{REPOSITORY}/blob/v0.2.0/docs/usecases/" in readme
    assert "- [Decisions](decisions.md)" in readme
    assert "(영어 원문)" in (handbook / "handbook/ko/README.md").read_text()
    decisions = (handbook / "handbook/en/decisions.md").read_text()
    assert "[`ADR-first`]" in decisions and "The first decision." in decisions
    assert "| **Bundle** | 번들 |" in (handbook / "handbook/ko/glossary.md").read_text()
    assert "first handbook snapshot" in (handbook / "handbook/en/changes.md").read_text()


def test_generation_keeps_narrative_and_is_repeatable(script, handbook):
    before = {path: path.read_text() for path in (handbook / "handbook").rglob("*") if path.is_file()}
    assert run(script, handbook, "generate", "--date", DATE).exit_code == 0
    after = {path: path.read_text() for path in (handbook / "handbook").rglob("*") if path.is_file()}
    assert after == before


def test_changes_list_new_decisions_since_the_previous_snapshot(script, handbook):
    write(
        handbook,
        {
            "VERSION": "0.3.0\n",
            "docs/decisions/2026-11/20261101-second.md": doc("ADR-second", "Second", status="accepted"),
        },
    )
    commit(handbook)
    assert run(script, handbook, "generate", "--date", DATE).exit_code == 0
    changes = (handbook / "handbook/en/changes.md").read_text()
    assert "Since the handbook snapshot `v0.2.0`" in changes
    assert "[`ADR-second`]" in changes and "[`ADR-first`]" not in changes
    assert json.loads((handbook / "handbook/manifest.json").read_text())["previous"]["tag"] == "v0.2.0"


def test_generation_refuses_uncommitted_docs_and_writes_nothing(script, repo):
    write(repo, {"handbook/en/README.md": EN_README})
    (repo / "docs/glossary.md").write_text(GLOSSARY + "\nDraft.\n")
    result = CliRunner().invoke(script.main, ["-w", str(repo), "generate"])
    assert result.exit_code == 2
    assert "HANDBOOK_DOCS_DIRTY" in result.stderr
    assert (repo / "handbook/en/README.md").read_text() == EN_README
    assert not (repo / "handbook/manifest.json").exists()


def test_a_preview_writes_only_the_preview_directory(script, handbook):
    tracked = {path: path.read_text() for path in (handbook / "handbook").rglob("*") if path.is_file()}
    result = run(script, handbook, "generate", "--preview", "--date", DATE)
    assert result.exit_code == 0
    assert "dir=dist/handbook-preview tag=unreleased" in result.stdout
    assert {path: path.read_text() for path in (handbook / "handbook").rglob("*") if path.is_file()} == tracked
    preview = (handbook / "dist/handbook-preview/en/README.md").read_text()
    assert "devkit (unreleased preview) at source commit" in preview
    assert json.loads((handbook / "dist/handbook-preview/manifest.json").read_text())["tag"] is None


def test_a_preview_without_a_tracked_handbook_creates_none(script, repo):
    assert run(script, repo, "generate", "--preview", "--date", DATE).exit_code == 0
    assert not (repo / "handbook").exists()
    assert (repo / "dist/handbook-preview/en/decisions.md").is_file()


# --- release check (AC-08) -------------------------------------------------------------------------------------------


def _commit_handbook(root: Path) -> None:
    git(root, "add", "-A", "handbook")
    git(root, "commit", "-q", "-m", "handbook")


def _files(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }


def test_a_refreshing_release_with_a_matching_docs_tree_passes(script, handbook):
    _commit_handbook(handbook)
    result = run(script, handbook, "release-check", "v0.2.0")
    assert result.exit_code == 0, result.stdout
    assert lines(result)[-1].startswith("[HANDBOOK_VERIFIED: tag=v0.2.0 ")


def test_a_refreshing_release_with_changed_docs_fails(script, handbook):
    _commit_handbook(handbook)
    write(handbook, {"docs/glossary.md": GLOSSARY + "\nLater.\n"})
    commit(handbook)
    result = run(script, handbook, "release-check", "v0.2.0")
    assert result.exit_code == 1
    assert any("code=HANDBOOK_DOCS_MISMATCH" in line for line in lines(result))


def test_a_refreshing_release_with_a_failing_check_fails(script, handbook):
    write(handbook, {"handbook/ko/extra.md": "# 추가\n"})
    _commit_handbook(handbook)
    result = run(script, handbook, "release-check", "v0.2.0")
    assert result.exit_code == 1
    assert any("code=HANDBOOK_PARITY" in line for line in lines(result))


@pytest.mark.parametrize("with_handbook", [True, False])
def test_a_release_that_did_not_refresh_skips_and_writes_nothing(script, repo, with_handbook):
    if with_handbook:
        make_handbook(script, repo)
        _commit_handbook(repo)
        write(repo, {"docs/glossary.md": GLOSSARY + "\nLater.\n"})  # would fail a refreshing release
        commit(repo)
    before = _files(repo)
    result = run(script, repo, "release-check", "v0.3.0")
    assert result.exit_code == 0
    expected = "v0.2.0" if with_handbook else "none"
    assert lines(result) == [f"[HANDBOOK_SKIPPED: tag=v0.3.0 manifest_tag={expected}]"]
    assert _files(repo) == before


def test_the_release_build_checks_the_handbook_before_building_wheels():
    release = (ROOT / "scripts/release.sh").read_text()
    check = release.index('scripts/handbook.py release-check "$tag"')
    assert check < release.index("uv build")
    assert release.index("does not match VERSION") < check


# --- repository rules (AC-09) ----------------------------------------------------------------------------------------


def test_stale_handbook_citations_are_excluded_from_the_cli_contract_rule(tmp_path):
    from devkit_agt.features.rules.services.builtins.cli_contract import CliContractRule
    from devkit_agt.features.rules.services.builtins.markdown_link.rule import MarkdownLinkRule
    from devkit_agt.features.rules.services.testing import check
    from devkit_dist.cli import cli

    config = tomllib.loads((ROOT / ".devkit/config.toml").read_text())
    settings = config["rules"]["settings"]["RULE-cli-contract"]
    page = "# Page\n\nRun `devkit renamed-command`.\n\n[Next](missing.md)\n"
    files = {"handbook/en/a.md": page, "guides/a.md": page}
    found = check(CliContractRule(root=cli), tmp_path, files, settings=settings)
    assert [violation.file for violation in found] == ["guides/a.md"]
    links = check(MarkdownLinkRule(), tmp_path)
    assert {violation.file for violation in links} == {"handbook/en/a.md", "guides/a.md"}
