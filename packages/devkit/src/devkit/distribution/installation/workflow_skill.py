from __future__ import annotations

from devkit.distribution.bundles.invocation import CODEX_FILE, codex_policy

NAME = "devkit-workflow"
MANAGED_ROOT = f".devkit/managed/_devkit/skills/{NAME}"

BODY = """# Delivery workflow: find the current stage and follow it

Use this skill when the user asks to start, continue, or check a piece of work
that follows a delivery workflow, or when another skill names a workflow stage.
The `devkit workflow` CLI (package `devkit.workflow`) computes the stage;
never derive it from files yourself.

1. Find the work unit. Run `uv run devkit workflow list` from the consumer
   project. If the user's task has no unit yet, create one with
   `uv run devkit workflow new <slug>` (add `--workflow <id>` when more than one
   workflow definition is installed; `uv run devkit workflow validate` lists them).
2. Diagnose the stage. Run `uv run devkit workflow next --unit <dir>` and read the
   tagged lines. `[STAGE]` is the current stage, `[UNMET]` and `[CHECK]` say
   what still blocks it, `[NEXT_SKILL]` names the skill that performs it, and
   `[RETURNS]` lists the stages this one may return to and why. `[STAGE: -
   complete=true]` means the unit is finished. Free-text values in tagged lines
   (details, reasons, notes) are JSON-quoted strings. `[BOUND_ELSEWHERE]` means
   the unit was evaluated against a workflow other than its binding, so no
   drift check ran.
   To take one of the `[RETURNS]` paths, run `uv run devkit workflow return
   --unit <dir> --to <stage>`; approvals for that stage and later ones are asked
   again. `[STALE_APPROVAL]` means the unit is back at an earlier stage and
   approvals of later stages still count; `next` never writes files. If the
   redone work needs fresh approval, run the command in its `void_with` field
   (`uv run devkit workflow return --unit <dir> --to <stage>`); ask the user when
   unsure.
3. Act on the signals. Open the skill named by `[NEXT_SKILL]` and perform the
   stage, producing the artifacts the definition names. `[DELEGATE]` asks for a
   subagent with that role and isolation; delegate when the host supports it,
   otherwise perform the stage yourself and say so. Write review and report
   envelopes with `uv run devkit workflow envelope review --unit <dir>` (and
   `reverify`, `worker`, `answer`, `resolution`; any other kind with
   `envelope new --unit <dir> --kind <kind>`), passing the result as flags
   (`--status`, `--summary`, `--check <name>=PASS|FAIL|SKIP`, `--findings-file`,
   and for a reverify `--from latest` with `--resolve`/`--waive`) rather than
   editing YAML by hand; without them it writes a skeleton to fill in. Validate with `uv run devkit workflow envelope check --unit <dir>`;
   never overwrite an existing envelope. A run that cannot go on records the
   cause in a `worker` envelope with `--problem`, `--tried` and `--recovery`
   (`failed` or `needs_input`); whoever actually fixes it writes a `resolution`
   with `--resolves <file>` and the fix in the same commit.
4. Respect gates. `[GATE: <name> policy=ask satisfied=no ...]` with
   `[WAITING: human gate:<name>]` means a person must approve; it appears only
   once the stage's other exit checks hold. The matching
   `[REQUEST: id=gate:<name> ...]` line is the question. Present the result and
   ask. Only after the user's explicit answer record it with
   `uv run devkit workflow answer --unit <dir> --request gate:<name> --action
   accept` (or `--action decline --note "<reason>"`), then rerun `next`. A host
   with its own approval UI writes the same record; never record an answer you
   did not receive. When the request ends with `answer=given`, the workflow
   keeps no record for that gate: after the user's explicit approval write
   nothing and pass `--given <name>` to this and every later `next`; on an
   objection take a `[RETURNS]` path instead. Name the user's approval as the
   basis in your report. `[GATE_PASSED: <gate> ... source=...]` lists every
   gate already passed with its basis: `source=policy` means project policy
   (`auto`) passed it; report that basis in your summary.
   `[BLOCKED]` (an unresolved problem) or `[PENDING_QUESTION]` holds the gates
   from the stage that raised it on, whatever their policy. A `[REQUEST: id=question:... answer=envelope]`
   line is a question: ask it, and record the user's answer with
   `uv run devkit workflow envelope answer --unit <dir>
   --answers-to <worker-NN.yaml> --answers-file <file>`, one rewritten
   `decision` per question, never `workflow answer`.
5. Stop on errors. An `[ERROR] (CODE)` block on stderr carries an `[ACTION]`
   directive; follow it. `WORKFLOW_DRIFT` means the definition changed under
   this unit: review the change with the user before running the `bind`
   command the `[FIX]` line names.
6. After each stage, rerun `next` to confirm progress before reporting. Report
   the stage you reached and anything the output listed as unmet.
7. Hand off when the workflow is complete. `[STAGE: - complete=true]` followed
   by `[HANDOFF: policy=ask ...]` lists the workflows this unit may continue
   with; `[CANDIDATE]` lines say which are eligible and recommended. Present
   them to the user (the `[REQUEST: id=handoff ...]` line is the question), and
   only after their choice record it with `uv run devkit workflow answer --unit
   <dir> --request handoff --action accept --value <id>` and run
   `uv run devkit workflow handoff --unit <dir>`. `handoff --workflow <id>`
   records the choice the same way `answer` does; use it only after the user's
   choice. Under `policy=auto` with a `chosen=` value, run `handoff` directly
   and report which candidate was chosen and why. Then continue with `next`.
   Approvals and choices from a finished segment never carry over to the next
   workflow. No `[HANDOFF]` line means the unit is finished.
"""


def skill_files(agent: str | None = None) -> dict[str, bytes]:
    frontmatter = (
        "---\nname: devkit-workflow\n"
        "description: Diagnose and advance the delivery workflow stage of a work unit with the devkit workflow CLI.\n"
    )
    files = {"SKILL.md": (frontmatter + "---\n\n" + BODY).encode()}
    if agent in {None, "codex"}:
        files[CODEX_FILE] = codex_policy(True)
    return files
