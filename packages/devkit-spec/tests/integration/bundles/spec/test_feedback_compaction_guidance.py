"""The `feedback-compaction` playbook compacts closed feedback into per-area records with aliases
(SPEC-feedback-dedup-and-compaction, ``ADR-closed-feedback-compacts-into-per-area-records-with-aliases``).

Wording tests pin the invocation, scope, record shape and completion conditions; the record-shape test fills the
playbook's own template and checks that the document index and the document rules accept it and resolve a retired ID.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import devkit_docs
import pytest
from devkit_agt.features.rules.services.testing import check, load_rule
from devkit_docs.features.documents import DocumentIndex
from distsupport.guidance import assert_rule
from spec_support.bundle_text import BUNDLE, raw, text
from spec_support.types import Write

PLAYBOOK = "playbooks/feedback-compaction/SKILL.md"
RULES = Path(devkit_docs.__file__).parent / "bundles/docs/bundle/rules"
REPOSITORY_ID = re.compile(r"\b(?:ADR|PADR|CAP|UC|UX|ARCH|SPEC|PROP|MS|MAT|FB)-[A-Za-z0-9][\w-]*")


def _section(heading: str) -> str:
    """The playbook section under ``heading``; the record template's own H2 does not end it."""
    body = raw(PLAYBOOK)
    start = body.index(heading)
    following = [body.find(f"\n## {name}", start + 1) for name in ("Step ", "Completion conditions")]
    return body[start : min([end for end in following if end != -1], default=len(body))]


def _template() -> str:
    match = re.search(r"```markdown\n(.*?)```", raw(PLAYBOOK), re.DOTALL)
    assert match, "the playbook carries the record template in a fenced markdown block"
    return match.group(1)


# AC-04
def test_the_playbook_is_a_core_asset_of_the_spec_bundle() -> None:
    manifest = tomllib.loads(raw("bundle.toml"))
    assets = {asset["id"]: asset for asset in manifest["assets"]}
    assert assets["feedback-compaction"] == {
        "id": "feedback-compaction",
        "kind": "playbook",
        "source": "playbooks/feedback-compaction",
    }
    assert "feedback-compaction" in manifest["presets"]["core"]["assets"]
    assert (BUNDLE / PLAYBOOK).is_file()


# AC-05
def test_invocation_authorizes_deletions_at_session_depth_and_keeps_outcomes() -> None:
    body = raw(PLAYBOOK)
    assert_rule(body, "only when", "invoked or confirmed", "authorizes", "feedback deletions")
    assert_rule(body, "`session` depth", "clean working tree", "base commit", "`git rev-parse head`")
    assert_rule(body, "never changes an outcome", "never reopens an item")


# AC-06
def test_collection_selects_terminal_feedback_under_specs_and_reports_exclusions() -> None:
    step = _section("## Step 1: Collect")
    assert_rule(step, "under `specs/`", "`resolved`, `promoted`, `dismissed` or `forwarded`", "leave", "reason")
    for item in (
        ("an `open` item",),
        ("spec bundle whose `spec.md` is not `completed`", "proposal"),
        (
            "current document outside this run's deletions",
            "`uv run devkit docs refs <id> --direction in`",
            "work history",
        ),
        (
            "unmerged local branch",
            "`git diff $(git merge-base head <branch>) <branch>`",
            "`git branch --no-merged head",
        ),
        ("fails `uv run devkit rules check <file>`", "unknown status"),
    ):
        assert_rule(step, *item)
    assert_rule(step, "`docs/materials/`", "stays as written")
    assert_rule(step, "existing resolved `fb-compacted-...` records", "other statuses stay in place")


# AC-07
def test_grouping_and_the_record_shape() -> None:
    group = _section("## Step 2: Group")
    assert_rule(group, "capability area", "`docs/capabilities/<area>/`", "`other`", "misgrouped entry is accepted")
    assert_rule(group, "one group per area and status")
    assert_rule(group, "resolved items for deletion without a record or alias", "every alias")
    assert_rule(group, "group map", "before writing")
    write = _section("## Step 3: Write or extend")
    assert_rule(group, "misgrouped entry", "move the entry and its alias", "delete no file")
    assert_rule(
        write,
        "`fb-compacted-<area>-<status>`",
        "package namespace",
        "`<namespace>-<area>`",
        "id, title and file name alike",
        "`fb-compacted-<namespace>-<area>-<status>`",
    )
    assert_rule(write, "append the new entries and aliases", "in place")
    assert_rule(write, "never create or extend a resolved compact record")
    assert "`specs/<YYYY-MM>/feedback/<YYYYMMDD>-compacted-<area>-<status>.md`" in text(PLAYBOOK)
    assert_rule(write, "only these seven fields", "every retired id", "every alias a member declared")
    assert_rule(
        write, "no observation field", "`scope`", "`kind`", "`category`", "`origin`", "`severity`", "`recurring`"
    )
    assert_rule(write, "one entry per retired id", "h2", "three lines")
    template = _template()
    frontmatter = template.split("---\n")[1]
    keys = [line.split(":")[0] for line in frontmatter.splitlines() if line and not line.startswith(" ")]
    assert keys == ["id", "title", "summary", "target", "status", "created_at", "aliases"]
    assert [line.split(":")[0] for line in template.splitlines() if line.startswith("- **")] == [
        "- **Symptom**",
        "- **Response**",
        "- **Reason**",
    ]


# AC-08
@pytest.mark.parametrize("area", ["delivery", "pkg-delivery"], ids=["global", "package-namespace"])
def test_the_filled_template_is_a_feedback_record_whose_aliases_resolve(
    workspace: Path, write: Write, area: str
) -> None:
    record = (
        _template()
        .replace("<area>", area)
        .replace("<Area>", "Delivery")
        .replace("<status>", "dismissed")
        .replace("<One English sentence naming the area's recurring symptoms; the search ranks it.>", "Sweeps.")
        .replace("<YYYY-MM-DD of the first run>", "2026-10-30")
        .replace("FB-<retired-name>", "FB-retired-sweep-miss")
        .replace("<the original title's words>", "A sweep missed a reworded duplicate")
        .replace("<the outcome with its spec, proposal, rule, ADR or report destination>", "Fixed in a spec")
        .replace("<one line: why this outcome>", "The lookup now searches every status")
    )
    assert "<" not in record
    write(f"specs/2026-10/feedback/20261030-compacted-{area}-dismissed.md", record)
    history = "specs/2026-09/20260901-sweep/spec.md"
    write(
        history,
        "---\nid: SPEC-sweep\ntitle: Sweep\nsummary: Sweep.\nstatus: completed\ncreated: 2026-09-01\n---\n"
        "# [SPEC-sweep] Sweep\n\n## Source feedback\n\n- `FB-retired-sweep-miss`\n",
    )
    index = DocumentIndex.load(workspace)
    found = index.resolve("FB-retired-sweep-miss")
    assert (found.id, found.kind.value, found.status) == (f"FB-compacted-{area}-dismissed", "feedback", "dismissed")
    for rule in ("id_convention", "spec_format", "document_reference"):
        assert check(load_rule(RULES / rule / "rule.py"), workspace) == [], rule
    # Completed spec history is checked only as an explicit target: its retired ID must resolve through the alias.
    assert check(load_rule(RULES / "document_reference" / "rule.py"), workspace, targets=[history]) == []


# AC-09
def test_apply_verify_and_completion_conditions() -> None:
    step = _section("## Step 4: Apply and verify")
    assert_rule(step, "`git rm` eligible resolved files", "existing resolved compact records", "`uv run devkit rules fix`")
    assert_rule(step, "status check", "at the base", "equals the `status` of the record that aliases it")
    assert_rule(step, "fidelity review", "disposition", "`reconcile.md`")
    done = _section("## Completion conditions")
    assert_rule(done, "`uv run devkit rules check` exits `0`")
    assert_rule(done, "`uv run devkit docs resolve <id>`", "`alias=<id>`", "every deleted non-resolved feedback id", "resolved ids need no alias")
    assert_rule(done, "status check and the fidelity review pass")
    assert_rule(done, "one commit", "records, deletions and rewrites", "group map", "left out", "adr candidates")


# AC-10
def test_adr_candidates_are_listed_for_the_user_only() -> None:
    step = _section("## Step 5: ADR candidates")
    assert_rule(step, "lasting policy", "repeated across entries", "general rule of behavior", "no accepted adr")
    assert_rule(step, "entry ids", "one-line candidate decision", "user's decision")
    assert_rule(step, "write no adr and no feedback")


# AC-11
def test_neighbouring_guidance_points_to_the_compact_form() -> None:
    assert_rule(
        raw("skills/spec/references/source-feedback.md"),
        "terminal source",
        "compact record",
        "alias",
        "`feedback-compaction`",
        "stays as written",
    )
    assert_rule(
        raw("skills/spec/references/playbooks.md"),
        "`spec/feedback-compaction`",
        "authorizes its deletions",
        "`session` depth",
    )
    assert_rule(raw("playbooks/feedback-hygiene/SKILL.md"), "terminal feedback", "`feedback-compaction` playbook")


# AC-12
def test_the_playbook_cites_no_repository_document() -> None:
    cited = set(REPOSITORY_ID.findall(raw(PLAYBOOK)))
    assert cited == {"FB-compacted-"}, cited
