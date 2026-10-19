---
id: MAT-codex-native-worker-design
title: Codex native worker design and implementation scope
summary: "Native Codex workers reuse existing role projection and one-shot lifecycle with emulated boundaries, per-command approvals and truthful partial-failure returns."
---

# [MAT-codex-native-worker-design] Codex native worker design and implementation scope

## Evidence and recommendation

`MAT-codex-native-worker-evidence` supplies the real Development run and permission observations. This proposal's
native Planning worker has committed its first reviewing boundary through the normal gate, using explicit cwd and a
command-scoped approval. A separate approved command created the PADR scaffold. Neither grant persisted to later
commands, and neither operation established a worker-specific path sandbox.

`packages/devkit-dist/src/devkit/distribution/bundles/subagents.py` accepts `emulated`, renders its boundary warning
and permits `sandbox_mode` for Codex; `unsupported` returns no projection. Existing
`packages/devkit-dist/tests/distribution/test_subagent_contracts.py` covers those branches and sync receipts. Thus
changing worker frontmatter is enough to produce both TOML roles; the renderer and its allowlist need no change.
`packages/devkit-spec/tests/test_role_contracts.py` currently asserts worker unsupported status and will change.

| Direction | Meets demonstrated need | New mechanism | Remaining risk |
| --- | --- | --- | --- |
| Unsupported/direct | Only via Host substitution | None | Native workers remain disabled despite evidence |
| Native/emulated | Yes, with runtime capabilities and command approvals | Existing spawn and projection only | Refusal can leave partial uncommitted work; Host blocks/recoveries |
| Process worker | Could, with additional validation | Launcher, access setup, output/lifecycle protocol | Larger unproven path and settings surface |

Recommend native/emulated as `ADR-codex-native-worker-execution` defines. Access diagnostics stay optional and
small; actual operations and approvals decide success. One-shot turns already bound lifecycle, so no turn-budget
feature, broker or generic probe command is justified.

## Development map

| Boundary | Change | Verification |
| --- | --- | --- |
| `bundle/subagents/{planning-worker,development-worker}.md` | Codex emulated/workspace-write; scoped approvals and truthful failure paths | Parse both real contracts; render actual Codex TOML and inspect warning/procedure/settings; preserve other hosts |
| `bundle/skills/spec-delegate/{SKILL.md,references/hosts.md,references/payload.md,references/worker.md}` | Named-role vs generic loading, trust restrictions, explicit cwd and permissions; reject failed uncommitted returns | Contract branch assertions for named/unavailable/trust-blocked and denial/failed emergency preservation |
| `bundle/skills/spec-orchestrate/SKILL.md` | Runtime capability fallback before worker start, same lifecycle and Host acceptance | Cross-contract consistency and caller-validation assertions |
| `bundle/skills/spec/references/worker-records.md` | Explicit report when permissions prevent a record/commit; no fabricated result | Deterministic assertions distinguish gate refusal from sandbox/approval denial |
| `packages/devkit-spec/tests/` | Target role/projection and instruction behavior | Affected tests, lint and types |
| `CAP-DLV-delivery-workflows` and installation receipt | Reconcile status/mechanism/limits and sync normal projections | Rules, budget, sync/status, full tests and consumer smoke before integration |

All bundle paths above are relative to `packages/devkit-spec/src/devkit_spec/`. Development may read and rerun
existing distribution tests without changing their implementation. No installed managed files or host configuration
are edited by hand. Approval/refusal behavior is instruction semantics, so deterministic tests check the concrete
required branches; they do not claim to simulate platform enforcement.

## Planning evidence boundary

The initial worktree HEAD was `bca2bb23244100a1ca23a53033892a394d10afad`; the first gated reviewing commit became
`004971b70dd0814f44b31a44a96771aceba8e0ad` after the commit gate rewrote it. This worker is a real native generic
subagent following the managed Planning contract under explicit experimental authorization. Its nested challenger,
feedback and worker envelopes provide the remaining run records. The Host must verify the final range, final HEAD,
clean tree and unchanged base before treating the run as validated Planning evidence.


## Challenger result and verification

The fresh nested challenger returned `completed` with no findings, recorded in Git `00de24882aa27c48da614e9ef47f8555bd532bb4:docs/proposals/PROP-codex-native-workers/envelopes/challenger-01.yaml`.
Its scope was the proposal, PADR and this material before this result section was added, plus the listed existing
contracts and evidence. The worker checked unchanged HEAD/index and only its own three draft paths after the
return. No finding disposition or re-review is required. The current `envelope reverify` command accepts only
review/reverify records, not challenger records; no unsupported resolution or fabricated closure is claimed.
Later evidence and run-record edits are worker self-verification, not additional challenger coverage.

Recommended Development effort stays `medium`: source behavior is bounded to existing instruction/contracts,
with no irreversible operation or unresolved P1 finding. A scout is unnecessary because source contracts,
renderer/tests and concrete live Development/Planning execution directly settle the technical spike questions.
