---
id: PROP-uiux-improve-impeccable-routing
title: Impeccable question and load routing for app-uiux-improve
summary: "Proposes capability-gated Impeccable question relay with every answer confirmed by the user, host-only skill loading and user-session fallback. Native plugin-load checks remain unmet on Claude Code and Codex."
status: accepted                     # draft | reviewing | accepted | rejected
created_at: 2026-11-13
target_area: capabilities/delivery/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
depends_on: [PROP-uiux-improve-run-model]
boundaries:
  owns:
    - docs/capabilities/delivery/CAP-DLV-uiux-improvement.md
    - docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md
    - docs/decisions/
    - packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/
    - packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py
  excludes:
    - packages/devkit-dist/
    - packages/devkit-spec/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
decomposed_from: PROP-uiux-improve-pilot-fit
workflow: sdd-proposal
---

# [PROP-uiux-improve-impeccable-routing] Impeccable question and load routing for app-uiux-improve

## 1. Background & Hypothesis

`CAP-DLV-uiux-improvement` rule 16 and `ADR-impeccable-session-authority` route Impeccable's interactive commands
(new work, `init`, `shape`, `critique`) to a session the user operates, because "no actor answers on the user's
behalf", and let a fresh child run only refinement commands loaded through the host's skill mechanism, returning a
load failure as a blocker. Findings A1 and A2 in `MAT-uiux-improve-pilot` test both clauses. Split from
~~`PROP-uiux-improve-pilot-fit`~~ (drafted in `6902170e9`, deleted in this split) with
`PROP-uiux-improve-bundle-hygiene` and `PROP-uiux-improve-run-model`. The user set the delivery order: after
`PROP-uiux-improve-run-model` (`depends_on`) and before `PROP-uiux-improve-bundle-hygiene`, which depends on this one.

- A1, question round. The pilot split `init` in a child. Phase 1 scanned and drafted the question round without
  writes. The coordinator pre-filled answers from the consumer's OOUX documents and asked the user only the gaps.
  Phase 2 resumed the same child to write. As run, the coordinator answered the pre-filled questions for the user,
  which the ADR forbids; it would comply only if the user confirmed every pre-filled answer, not only the gaps.
- A2, load route. A fresh Claude Code child did not list the plugin-installed Impeccable, and the child read
  `SKILL.md` and `reference/*.md` from the plugin cache instead (twice in the first pilot, once more in a second run).
  Correction to the earlier reading: the Claude Code documentation says subagents can discover and invoke plugin
  skills through the Skill tool wherever the plugin is enabled. In the consumer, the plugin was enabled for a
  different project only, and the coordinator session did not list it either. The failure was most likely
  enablement scope, not a host limit on children; this is not yet tested live. The cache read is an undocumented
  workaround: it skips the Skill tool, progressive loading and the enablement policy, and depends on the cache
  layout. Codex documentation says skills inherit from the parent but does not cover plugin skills in subagents.

Hypothesis: a relayed route where the user confirms every answer keeps the user deciding every answer while saving
the separate user-operated session, and a properly enabled plugin removes the need for any file-read fallback.

## 2. Technical Spike Findings and Planning Decisions

Planning at `high` compared the current user-operated session, a capability-gated relay and unconditional relay
with cache loading. `MAT-impeccable-routing-planning` records the evidence, inbound references and live-check limits.
`PADR-impeccable-question-relay` drafts the recommended direction; it is not acceptance authority.

- **Q1 — Question ownership**: recommend a read-only question phase followed by explicit user confirmation of every
  answer and continuation of the same child. An OOUX-derived pre-fill is a suggestion with its source, never an
  answer on the user's behalf. Missing answers and additional upstream questions stop writes.
- **Q2 — Load and host evidence**: keep the host's skill mechanism as the only loading route. Current-project plugin
  enablement is the first diagnostic when a child cannot see the skill. Both requested native Impeccable load checks
  remain unmet: this session exposes neither an Impeccable invocation nor a Claude Code runtime. A Codex same-child
  continuation probe passed, but it tested no plugin loading or interactive Impeccable command.
- **Q3 — Supersession**: replace only the interactive-command routing restriction in `ADR-impeccable-session-authority`.
  Its host-only load mechanism, user ownership of answers, context-file direction, edit boundary and coordinator
  acceptance remain. `PROP-uiux-improve-run-model` separately owns consumer workflow authority; Development reads
  its landed result rather than assuming its draft was accepted.

**Evidence decision (`by: user`)**: empirical validation is best-effort for this personal project and does not
hold Planning. Retain both host plugin-load and interactive live checks as unverified; usage and concrete feedback
will inform later repair. This settles the draft's original two-host-before-decision requirement without certifying
either host. The Host selects capability-gated relay within that direction. Runtime capability checks and
user-session fallback remain in force.

## 3. Proposed Design & Impact

### Options

| Option | Benefit | Cost and risk | Recommendation |
| --- | --- | --- | --- |
| Keep all interactive work in a user-operated session | Existing supported fallback; no new relay contract | Manual handoff and report even where continuation works | Use whenever a relay prerequisite fails |
| Capability-gated relay with every answer user-confirmed | Keeps one coordinated request and preserves answer ownership | Native loading, continuation and command capabilities need per-run evidence; Impeccable live behavior is unverified | Selected under the user's best-effort evidence direction |
| Relay all commands and read the plugin cache on load failure | Avoids host enablement troubleshooting | No supported cache contract; bypasses enablement and can misstate nested-agent coverage | Rejected as a sanctioned route |

### Proposed relay contract

1. The user selects Impeccable for this request as today. The coordinator preserves the self-contained brief,
   recorded base, edit list, context-file permissions and exclusive product-writer interval. The preceding
   run-model's landed authority terms apply unchanged.
2. Before offering relay for a command, verify that a fresh child can load Impeccable through the host's supported
   skill mechanism and that the host can resume that same child with its retained state. Report observations for
   the actual host and project; a documentation statement, inherited skill name or cache-file read is insufficient.
   If either capability is unavailable or unverified, use the user-operated session.
3. The brief's first phase permits inspection and question drafting only, with no retained-file, product, index or
   HEAD writes. The child returns the complete current question round, an identifier for each question, suggested
   answers where useful, the source path and passage for each document-derived suggestion, and any blocker.
4. The coordinator shows the complete packet to the user and obtains an explicit answer or confirmation for every
   question, including every pre-fill. A user may confirm the entire visible packet together; silence, omitted
   answers and confirmation of gaps alone grant no answer authority. The coordinator does not change confirmed
   answers. `PRODUCT.md` or `DESIGN.md` edits still require explicit user direction naming those files and the action.
5. Resume the same child with the complete confirmed packet and the same brief/base. Before writes, recheck the
   brief's source facts and observed file state. If they changed in a way that affects questions, answers or scope,
   stop, refresh the packet and obtain confirmation for the affected answers. A lost child or missing continuation
   state falls back to the user-operated session; never recreate a writing child from an assumed transcript.
6. New upstream questions return to the coordinator without writes dependent on their answers. Relay each new round
   through the same confirmation process. Partial or unexpected writes are reported against the recorded base;
   neither the coordinator nor a restarted child blindly replays the command or reverts consumer files.
7. `shape` and `critique` also require the child to have the nested-role capabilities their loaded upstream command
   requires. Host documentation alone does not prove those tools are available to this child. Missing or unverified
   nested-role support routes the command to the user-operated session; never replace upstream isolated roles with
   inline reasoning while claiming equivalent coverage. `live` remains excluded.
8. Load failure reports the current project/plugin enablement and native skill availability actually observed, the
   failed operation and the user-session fallback. Do not change enablement or install a plugin without the existing
   user-requested setup authority. Plugin cache reads stay an observed undocumented workaround, not an allowed
   load route.
9. Coordinator acceptance compares the result to the brief and recorded base under the existing rules. The relay
   adds no delivery record, prompt vendoring, runtime, plugin setup, Git authority or consumer-document edit authority.

### Target documents and source

- `CAP-DLV-uiux-improvement`: rule 16 gains the relay contract and capability fallbacks; rule 10 names observed
  enablement as load-failure diagnosis. Rules 15, 17, 18 and 19 retain their authority and ownership boundaries.
- `UC-improve-an-interface-and-user-flow`: its delegated-session extension and examples cover complete confirmation,
  unavailable continuation, native-load failure, additional questions and unavailable nested roles.
- `PADR-impeccable-question-relay` promotes to a partial superseding ADR. The old ADR stays accepted and gains the
  exact partial-supersession pointer; no unrelated clause is reworded.
- The bundle's `SKILL.md`, `references/orchestration.md` and README describe the same conditions. Keep workflow-neutral
  language and keep this bundle installable without `devkit-spec`, `devkit-docs` or harness runtime dependencies.
- Extend `test_app_uiux_improve.py` for the changed instruction contract. No new package, feature edge or test tier.

### Acceptance and verification plan

| ID | Given / When | Expected result and check |
| --- | --- | --- |
| AC-R1 | Native skill load and same-child continuation are observed, and the user selects relay | Read-only question phase, every answer confirmed, then same-child writing phase; instruction review and contract assertions |
| AC-R2 | Only gaps are answered, one pre-fill is omitted, or an extra upstream question appears | Dependent writes wait for explicit user answers; packet scenario review and contract assertions |
| AC-R3 | Native loading fails or the plugin is unavailable in the consumer project | Report observed enablement/availability, keep cache reading outside sanctioned routes, use user-session fallback; negative scenario and assertions |
| AC-R4 | Same-child continuation is unavailable, state is lost or relevant brief facts changed | No guessed resume; fallback or refreshed confirmation before writes; negative scenario review |
| AC-R5 | `shape` or `critique` requires nested roles that the child lacks | User-session fallback and limited-coverage report; no claim that inline work ran the roles |
| AC-R6 | A confirmed answer implies `PRODUCT.md` or `DESIGN.md` changes without explicit file permission | Do not authorize those writes; existing rule 19 remains; assertions and brief scenario review |
| AC-R7 | A relay returns changes or partial execution | Existing base comparison, edit-list acceptance and qualified reporting still apply; retain existing tests |
| AC-R8 | Review requests native Impeccable behavior on Claude Code and Codex | Record both live checks as unmet until performed; assertions and continuation probe are not end-to-end evidence |

Development runs the bundle integration test and required repository lint, types and affected tests. Review distinguishes
text-contract assertions and scenario review from model obedience, plugin loading and live interaction. No live
support or performance improvement is claimed from these checks. `dev_effort: medium` remains appropriate for this
instruction/contract change; Planning stays high because the direction revises an accepted authority contract.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: the Host uses the composed `devkit spec proposal accept-plan` command after review is ready. Development follows `PROP-uiux-improve-run-model` and precedes
  `PROP-uiux-improve-bundle-hygiene`. Handoff promotes the PADR and preserves the source material and unmet checks.
- On Rejection: keep `status: rejected` only after the Host carries the user's decision. Later retirement follows
  the repository procedure and preserves useful evidence.
- This Planning turn makes no acceptance, handoff or live-support claim. Both live plugin-load checks and an
  end-to-end interactive relay remain unverified and visible at plan acceptance; they do not hold Planning.
