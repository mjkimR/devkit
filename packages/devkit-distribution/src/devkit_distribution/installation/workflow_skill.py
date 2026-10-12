from __future__ import annotations

NAME = "devkit-workflow"
MANAGED_ROOT = f".devkit/managed/_devkit/skills/{NAME}"

BODY = """# Delivery workflow: find the current stage and follow it

Use this skill when the user asks to start, continue, or check a piece of work
that follows a delivery workflow, or when another skill names a workflow stage.
The `agent-workflow` CLI (package `agent-workflow-engine`) computes the stage;
never derive it from files yourself.

1. Find the work unit. Run `uv run agent-workflow list` from the consumer
   project. If the user's task has no unit yet, create one with
   `uv run agent-workflow new <slug>` (add `--workflow <id>` when more than one
   workflow definition is installed; `uv run agent-workflow validate` lists them).
2. Diagnose the stage. Run `uv run agent-workflow next --unit <dir>` and read the
   tagged lines. `[STAGE]` is the current stage, `[UNMET]` and `[CHECK]` say
   what still blocks it, `[NEXT_SKILL]` names the skill that performs it, and
   `[RETURNS]` lists the stages this one may return to and why. `[STAGE: -
   complete=true]` means the unit is finished.
3. Act on the signals. Open the skill named by `[NEXT_SKILL]` and perform the
   stage, producing the artifacts the definition names. `[DELEGATE]` asks for a
   subagent with that role and isolation; delegate when the host supports it,
   otherwise perform the stage yourself and say so. Write review and report
   envelopes with `uv run agent-workflow envelope new --unit <dir> --kind <kind>`
   and fill them in; never overwrite an existing envelope.
4. Respect gates. `[GATE: <name> policy=ask]` with `[WAITING: human ...]` means
   a person must approve. Present the result and ask; only after the user's
   explicit approval rerun `next` with `--given <name>`. `policy=auto` was
   delegated by project policy: report that basis in your summary. Never pass
   `--given` for an approval you did not receive.
5. Stop on errors. An `[ERROR] (CODE)` block on stderr carries an `[ACTION]`
   directive; follow it. `WORKFLOW_DRIFT` means the definition changed under
   this unit: review the change with the user before running the `bind`
   command the `[FIX]` line names.
6. After each stage, rerun `next` to confirm progress before reporting. Report
   the stage you reached and anything the output listed as unmet.
7. Hand off when the workflow is complete. `[STAGE: - complete=true]` followed
   by `[HANDOFF: policy=ask ...]` lists the workflows this unit may continue
   with; `[CANDIDATE]` lines say which are eligible and recommended. Present
   them to the user, and only after their choice run
   `uv run agent-workflow handoff --unit <dir> --workflow <id>`. Under
   `policy=auto` with a `chosen=` value, run `uv run agent-workflow handoff
   --unit <dir>` and report which candidate was chosen and why. Then continue
   with `next`. No `[HANDOFF]` line means the unit is finished.
"""


def skill_files(agent: str | None = None) -> dict[str, bytes]:
    frontmatter = (
        "---\nname: devkit-workflow\n"
        "description: Diagnose and advance the delivery workflow stage of a work unit with the agent-workflow CLI.\n"
    )
    files = {"SKILL.md": (frontmatter + "---\n\n" + BODY).encode()}
    if agent in {None, "codex"}:
        files["agents/openai.yaml"] = b"policy:\n  allow_implicit_invocation: true\n"
    return files
