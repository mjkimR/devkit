# Review Envelopes

**Package**: `devkit.workflow`. The file contract that delegated roles and reviews write and the envelope checks read.  
**Related**: [Workflow Definitions and Checks](definition-and-checks.md#primitives), [CLI and Output Contract](cli-and-output.md).

## 1. File Contract

Delegated roles and reviews return a YAML envelope written to `<unit>/envelopes/<kind>-<NN>.yaml`. `kind` matches `[a-z][a-z0-9-]*`; `NN` is a sequence per kind of at least two digits (`01` ... `99`, `100`, ...). The highest sequence is current and earlier files are history. Files are never overwritten; `devkit workflow envelope new` writes the next number under the same directory lock as decision records, and writes the file whole (a hidden temporary file that takes its name without replacing a file, [Answer](human-interaction.md#4-answer)), so an interrupted write leaves no partial envelope. Files named `.<name>.<12 hex digits>.tmp` are such temporary files and are never loaded.

```yaml
kind: review
stage: review
workflow: direct-delivery    # the workflow the unit was bound to when written (envelope new records it)
segment: 0                   # finished segments in the anchor's workflow_history when written
created_at: 2026-10-12T10:00:00.250000Z   # UTC; to the second is also valid
status: completed            # completed | needs_input | failed
summary: "1-3 line judgment"
findings:
  - issue: "What was found"
    evidence: "path:line"
    failure_condition: "Under which input it fails"
    suggested_action: "Recommended next step"
    resolution: open         # open | resolved | waived (default open)
    waiver: "why it is accepted"   # waived findings only
assumptions: ["what the judgment rests on"]        # optional
unverified_areas: ["what was not checked"]        # optional
checks:                      # free-form keys; a value starting with PASS satisfies envelope-check-pass
  tests: "PASS 14/14"
diff_scope: { base: "main", head: "<sha>" }
review: review-01.yaml       # reverify only: the review round it closes
```

- `kind` and `status` are required; `kind` must match the file name and `status` must be `completed`, `needs_input` or `failed`.
- A `reverify` envelope must name the `review-NN.yaml` it closes. The deciding review state is the latest review round, or the last reverify that references it. Envelopes a later `devkit workflow return` re-opened are left out first ([Returns](human-interaction.md)).
- `workflow` (a workflow id) and `segment` (a non-negative integer) scope the envelope to one [workflow segment](overview.md#the-handoff-gate), like decision records: the checks of a workflow count only envelopes whose `workflow` is that workflow and whose `segment` is the number of entries in the anchor's `workflow_history` (`0` before the first handoff). After a handoff the next workflow therefore does not see the previous segment's reviews, and a workflow re-entered later (`a` to `b` to `a`) does not see those of its earlier segment. An envelope without `workflow` counts in every segment; one with `workflow` but no `segment` counts in every segment of that workflow. A `workflow` that is not an id, or a `segment` that is not a non-negative integer, makes the envelope malformed.
- `completed` with no findings is a valid pass. `needs_input` and `failed` never satisfy a check.
- `assumptions` and `unverified_areas` are lists of strings; `checks` is a mapping; `findings` is a list of mappings with only the finding keys shown above. Other top-level keys are ignored.
- Malformed envelopes are reported as `[ENVELOPE_ERROR: file "reason"]` (in JSON, an `ENVELOPE_INVALID` entry of `errors` with its `file`) and are not loaded; evaluation continues.

## 2. Authoring

`devkit workflow envelope new --unit DIR [--anchor FILE] --kind KIND [--stage ID]` locates the unit's anchor like every unit command (`--anchor` names the anchor when the directory holds several, `ANCHOR_AMBIGUOUS`), records the bound workflow's id (or the configured default's for an unbound unit, `WORKFLOW_NOT_SELECTED` without one) and the current segment in `workflow` and `segment`, and with no other flag writes a `needs_input` skeleton for the author to fill in. It reads only the anchor's binding, never the plugin checks, and the workflow definition only when `[workflow].default` names it by a `.md` path, for its `id` (unvalidated; evaluation scopes envelopes by that id, so the path itself would never count), so a review can be recorded while the definition is invalid, or missing when the unit is bound or the default is an id. `created_at` is the current UTC time to the microsecond, or the end of the latest accepted `return` of the segment when the clock has not passed it, so a `return` followed at once by `envelope new` never voids the new envelope ([Returns](human-interaction.md#5-how-the-engine-applies-answers)). Any further flag switches to authoring, where the file is written complete so that no agent edits YAML by hand:

| Flag | Effect |
| --- | --- |
| `--status` | `completed` (default when authoring), `needs_input` or `failed`. |
| `--summary TEXT` | The judgment. |
| `--assume TEXT`, `--unverified TEXT` | Repeatable; fill `assumptions` and `unverified_areas`. |
| `--check NAME=VERDICT[ detail]` | Repeatable; `VERDICT` is `PASS`, `FAIL` or `SKIP` and may carry a detail such as `PASS 14/14`. |
| `--base REV`, `--head REV` | `diff_scope`; `--head` is what `revision-ancestor` compares and must be a hexadecimal commit id (`--head $(git rev-parse HEAD)`). |
| `--findings-file PATH` (or `-` for stdin) | A YAML list of findings with `issue` and `evidence` (required) and optionally `failure_condition`, `suggested_action`, `resolution` (default `open`) and `waiver`; other keys are refused. A `review` records findings as found, so a resolution other than `open` is refused. |
| `--from latest` (or a review/reverify file) | Carries the findings of the round being closed into a `reverify` and sets its `review`. `latest` is the deciding review state among the envelopes of the current segment. Refused for `review`; required for `reverify`. |
| `--resolve N` (repeatable) or `--resolve all` | Marks carried finding `N` (1-based) resolved; `all` resolves every open one. A number outside the carried findings is `ENVELOPE_FLAG_INVALID`. |
| `--waive N=REASON` (repeatable) | Marks carried finding `N` waived and records the reason as its `waiver`; `suggested_action` is kept. |

Findings from `--findings-file` are appended after any carried findings. The written key order is `kind, stage, workflow, segment, created_at, status, review, summary, findings, assumptions, unverified_areas, checks, diff_scope`, omitting empty optional keys. The kind must match `[a-z][a-z0-9-]*` (`ENVELOPE_KIND_INVALID`). The sequence follows the highest `<kind>-NN` file present, malformed files included. The confirmation line is `[ENVELOPE: <file> kind=K seq=NN status=S open_findings=N]`; `--format json` emits `{"file", "kind", "seq", "status", "open_findings"}`.

## 3. Checking

`devkit workflow envelope check --unit DIR` loads every file under `envelopes/`, prints one `[ENVELOPE: file kind seq status open_findings]` line per valid file and one `[ENVELOPE_ERROR: file "reason"]` per malformed one, then `[OK: N envelopes]` when nothing is malformed. Each malformed file is also reported on stderr as an `ENVELOPE_INVALID` advisory whose `[TARGET]` is the file, and the command exits `1`. `envelope check` lists every envelope whatever its segment; each JSON entry carries `workflow` and `segment` (`null` when absent). `--format json` emits `{"envelopes": [...], "errors": [...]}` as the only output, each error the `to_dict()` of the advisory (`code`, `message`, `exit_code`, `advisory` with the file as `target_files`, `file`); nothing goes to stderr.
