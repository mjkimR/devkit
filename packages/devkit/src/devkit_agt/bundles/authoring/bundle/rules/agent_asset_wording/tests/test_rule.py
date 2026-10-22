"""``RULE-agent-asset-wording``, loaded from this folder as devkit loads the deployed copy."""

from __future__ import annotations

import json
from pathlib import Path

from devkit_agt.features.rules.services.testing import check, evaluate, load_rule

RULE = load_rule(__file__)
SKILL = "tools/kit/src/kit/bundle/skills/demo/SKILL.md"


def _receipt(owned: list[str]) -> str:
    """A minimal installation receipt that owns ``owned`` (agent projections of bundle assets)."""
    files = {name: {"sha256": "0" * 64, "mode": 420} for name in owned}
    return json.dumps(
        {"schema": 1, "packages": [], "selection": {"agents": [], "presets": {}}, "assets": [], "files": files}
    )


def _found(tmp_path: Path, body: str, **settings: object) -> list[tuple[int, str]]:
    return [(v.line, v.message) for v in check(RULE, tmp_path, {SKILL: body}, settings=settings or None)]


def test_reports_each_occurrence_with_its_category(tmp_path: Path) -> None:
    body = "# Demo\n\nThe sync might fail.\nALWAYS run the check.\nThe API was recently renamed; it MIGHT break.\n"
    found = check(RULE, tmp_path, {SKILL: body})
    assert [(v.line, v.message) for v in found] == [
        (3, 'Hedge "might"'),
        (4, 'Emphatic capitals "ALWAYS"'),
        (5, 'Hedge "MIGHT"'),
        (5, 'Time-relative word "recently"'),
    ]
    assert {(v.file, v.phase.value, v.severity.value, v.fixable) for v in found} == {
        (SKILL, "hygiene", "warning", False)
    }
    assert found[0].remediation.startswith("State the condition")
    assert "backticks or double quotes" in found[0].remediation


def test_phrases_match_across_spaces(tmp_path: Path) -> None:
    body = "DO  NOT skip it.\nKeep it as of\nnow.\nKeep it for now.\n"
    assert _found(tmp_path, body) == [(1, 'Emphatic capitals "DO NOT"'), (4, 'Time-relative word "for now"')]


def test_mentions_in_quotes_code_comments_and_templates_pass(tmp_path: Path) -> None:
    body = "\n".join(
        [
            "---",
            "description: Write no hedges.",
            "---",
            'Write no hedges ("likely", "might") and no “CRITICAL” emphasis.',
            "Run `devkit check --recently` or ``a `NOTE` b``.",
            "<!-- this might change --> Then stop.",
            "<!-- a block",
            "that is currently open -->",
            "{{ 'might' }} {% if ALWAYS %} {# recently #}",
            "{# a multi-line",
            "Jinja comment that might wrap #}",
            "```text",
            "IMPORTANT: this might fail",
            "```",
            "~~~",
            "currently",
            "~~~",
        ]
    )
    assert _found(tmp_path, body) == []


def test_keywords_ordinary_case_and_joined_words_pass(tmp_path: Path) -> None:
    body = (
        "A writer MUST, MUST NOT, SHOULD or MAY.\n"
        "Never skip it; only always the default.\n"
        "The option was considered; mightily so.\n"
        "Report INTEGRATION_NOT_READY on a READ-ONLY tree; NOTES are fine.\n"
    )
    assert _found(tmp_path, body) == []


def test_default_scope_skips_projections_docs_and_other_suffixes(tmp_path: Path) -> None:
    files = {
        SKILL: "It might fail.\n",
        "pkg/bundle/subagents/reviewer.md": "It might fail.\n",
        "pkg/bundle/instructions/style.md.jinja": "It might fail.\n",
        ".agents/skills/demo/SKILL.md": "It might fail.\n",
        ".agents/skills/demo/scripts/run.py": "# It might fail.\n",
        "docs/guide.md": "It might fail.\n",
        # A projection the receipt owns is fixed in its bundle, never reported in the project.
        ".claude/skills/demo/SKILL.md": "It might fail.\n",
        ".devkit/installation.json": _receipt([".claude/skills/demo/SKILL.md"]),
    }
    found = check(RULE, tmp_path, files)
    assert sorted(v.file for v in found) == [
        ".agents/skills/demo/SKILL.md",
        "pkg/bundle/instructions/style.md.jinja",
        "pkg/bundle/subagents/reviewer.md",
        SKILL,
    ]


def test_paths_and_targets_narrow_or_extend_the_scope(tmp_path: Path) -> None:
    files = {SKILL: "It might fail.\n", "docs/guide.md": "It might fail.\n"}
    found = check(RULE, tmp_path, files, settings={"paths": ["docs/**"]})
    assert [v.file for v in found] == ["docs/guide.md"]
    found = check(RULE, tmp_path, targets=["tools/kit"])
    assert [v.file for v in found] == [SKILL]


def test_word_lists_are_configurable(tmp_path: Path) -> None:
    body = "It might fail.\nIt could fail.\nALWAYS check.\n"
    assert _found(tmp_path, body, hedges=["could"], emphatic=[]) == [(2, 'Hedge "could"')]


def test_path_overrides_apply_per_file(tmp_path: Path) -> None:
    other = "tools/kit/src/kit/bundle/skills/other/SKILL.md"
    files = {SKILL: "NOTE: it is fine.\n", other: "NOTE: it is fine.\n"}
    settings = {"overrides": [{"path": SKILL, "emphatic": []}]}
    assert [v.file for v in check(RULE, tmp_path, files, settings=settings)] == [other]


def test_invalid_settings_are_reported(tmp_path: Path) -> None:
    for settings in ({"hedges": [" "]}, {"time_relative": ["as of\nnow"]}, {"suffixes": ["md"]}):
        result = evaluate(RULE, tmp_path, settings=settings)
        assert [problem.code for problem in result.errors] == ["RULES_SETTINGS_INVALID"]
