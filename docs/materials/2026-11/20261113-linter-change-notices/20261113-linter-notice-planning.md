---
id: MAT-linter-notice-planning
title: Linter notice source inspection and verification map
summary: "Source evidence for additive rule notices, exact change evidence and an explicit host-neutral read companion, pinned to the Planning input commit."
created_at: 2026-11-13
---

# [MAT-linter-notice-planning] Linter notice source inspection and verification map

Input: `aa6c51dc3148efba121bc54c8e582a59aacd11d1`, inspected in the assigned Planning worktree.
No production behavior was changed or runtime performance measured.

| Source | Observed fact | Design implication |
| --- | --- | --- |
| `features/rules/models/contracts.py` in devkit-agt | Severity exposes error/warning/info; RuleContext has file targets and optional Snapshot, not hunk evidence. | Add a distinct severity and optional change evidence without renaming INFO. |
| `features/rules/models/snapshot.py` and `repositories/workspace/snapshot.py` | Snapshot captures tree/base/changed/deleted/files; staged uses the commit index and CI uses HEAD versus merge base. | Derive hunks from those same identities, never unstaged bytes. |
| `features/rules/services/evaluator.py` | Blocking findings are unfixed ERROR only; target scoping includes snapshot deleted paths. | Keep blocking semantics, add independent change_scope selection and deleted evidence. |
| `features/rules/models/phases.py` | Hygiene includes linter rules and promotion counts all remaining findings. | Explicitly exclude change_scope from hygiene and NOTICE from obligations. |
| `features/rules/cli/output.py` | Findings are VIOLATION sentinels and JSON violation dictionaries; summary iterates Severity. | Keep the existing finding channel; add notice count and consideration status. |
| `features/gate/usecases/gates/rules.py` | Gate emits warnings separately and refuses only blocking findings/errors. | Add notice-level delivery without warning promotion. |
| `features/workflow/usecases/lint.py` | lint-clean consumes blocking violations only. | Regression tests suffice; no workflow implementation edit needed. |
| `CAP-HOST-lifecycle-observation` | Codex-only advisory hooks carry native payloads; observer stores only event metadata. | Existing contract proves no universal file-read input or cross-host interception route. |
| `.devkit/architecture.toml` | Rules already depends on project; gate already depends on rules; dist cannot import agt. | Keep capture and session memo in rules; no host/dist dependency. |

`CAP-ADV-agent-advisory-protocol` defines NOTICE as non-error and non-strict-promoted. Rule severity stays separate
from its advisory levels and the result-level `notices` array. `CAP-GOV-rules-engine`,
`CAP-GOV-evaluation-lifecycle` and `CAP-GOV-rule-authoring` own the rule-facing extensions.

Verification is the behavioral matrix AC-N1 to AC-N10 in `SPEC-linter-change-notices`; target-docs names the future
write owners. No native host delivery, end-to-end model receipt, installed third-party plugin behavior or performance
gain is inferred from source inspection. Host projection is emulated: absolute worktree cwd, per-operation approval
and before/after committed diff snapshots substitute for native role/path enforcement.
