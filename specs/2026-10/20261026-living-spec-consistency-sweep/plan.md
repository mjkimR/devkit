---
id: PLAN-living-spec-consistency-sweep
spec: SPEC-living-spec-consistency-sweep
---

# Technical Plan: `SPEC-living-spec-consistency-sweep` Living Spec consistency sweep

## 1. Constitution & Invariant Review

None. No architectural `MUST` changes and no ADR is edited: every fix rewrites a citing document to the shipped
behavior, or a help or guidance text to the shipped behavior. `ADR-host-cli-lifecycle-authority` supersedes
`ADR-local-and-pull-request-integration`; the citing sentence in `CAP-INT-mcp-services` changes, the ADRs do not.

## 2. Architecture Overview & Impact

| Item | Source of truth | Change |
| --- | --- | --- |
| 1 | `devkit_agt.features.workflow` (`POLICIES`, `GatePolicyError`), `devkit_spec.features.policy.services.config.check_approvals` | `CAP-DLV-project-policy` §4.1 `GATE_POLICY` values; `CAP-DLV-delivery-workflows` §4.3 codes per command family |
| 2 | `devkit spec proposal accept --help`, `delivery/cli/proposals.py` | `CAP-DLV-proposal-incubation` rule 14: the no-commit sentence applies without `--mode` |
| 3 | `shared/mcp.py` (no report tool), `native_handoff.py` (`execute_native` unregistered) | proposal-incubation summary; UC summary, success guarantee, extension 7a; `CAP-INT-mcp-services` runtime sentence |
| 4 | `devkit workflow show` (no stage with `proposal-handoff`) | `CAP-DLV-delivery-workflows` §4.3 row; project policy rule 4 |
| 5 | `devkit_spec` embeds the engine (`Workspace.evaluate_unit`) | `CAP-DLV-workflow-orchestration` §2, §3 and §5; `CAP-WT-task-worktrees` §7 |
| 6 | `devkit workflow show` stage IDs | `CAP-DLV-workflow-orchestration` §1 |
| 7 | `ADR-host-cli-lifecycle-authority` | `CAP-INT-mcp-services` opening |
| 8 | `shared/mcp.py` | `CAP-MCP-runtime-registration` shared artifact services |
| 9 | `registrations.py` `DESTINATIONS`, `devkit mcp setup --help` | `CAP-HOST-lifecycle-observation` summary and MCP section; `reference/host.md` |
| 10 | - | `CAP-HOST-lifecycle-observation` section 8 becomes 6 |
| 11 | `CAP-INT-mcp-services` (lifecycle tools not registered) | `CAP-VIEW-repository-viewer` §3 |
| 12 | `worktree/cli.py` (`status --stale`) | module docstring; `CAP-WT-task-worktrees` §7 |
| 13 | `Kind` enum (`milestone`), `click.Choice` of `list` | `CAP-DOCS-document-lookup` 3.4 item 1; `list` docstring |
| 14 | `generated/cli.py` `list_cmd` | `CAP-GEN-tracked-artifacts` §1 |
| 15 | - | `CAP-DIST-sync-and-transactions` §1 and Locked Synchronization paragraph order |
| 16 | `distribution/cli/selection.py` | `CAP-MCP-runtime-registration` command contract; pointer in the sync capability |
| 17 | `rules/repositories/config.py` `_phase_overrides` (real CLI output) | `CAP-ADV-agent-advisory-protocol` example |
| 18 | `rules/cli/commands.py` (`hidden=True`, commit `59402001`) | `CAP-GOV-rules-engine` §3; `reference/rules.md` |
| 19 | consolidated ADR aliases | `ARCH-01-introduction-and-goals`, `ARCH-05-1-containers`, `CAP-VIEW-repository-viewer`, `CAP-DIST-content-packages`, `CAP-DLV-project-policy` |
| 20 | `ARCH-04-1-ecosystem-boundaries` actor table | `docs/glossary.md` §4 **Host** row |
| 21 | `find_project_root` | `distribution/cli/output.py` `WORKSPACE` uses the shared `WORKSPACE_HELP` |
| 22 | `ADR-apply-behavior-preserving-batches-as-direct-mode-refactors` §4 | `spec` skill `references/classification.md` §1, then `devkit sync` |

Choices made inside the agreed intent:

- Item 18: keep `phases` and `test` hidden and document it, because the hiding commit applied the same pattern the
  workflow CLI documents as deliberate; unhiding is a CLI surface decision the intent leaves to the code's history.
- Item 21: reuse the shared `WORKSPACE_HELP` instead of rewriting a distribution-specific text, as the feedback
  proposes, so one text describes the option.
- Item 14: document `list` inside §1, beside the registry it reads, so the later sections keep their numbers.
- Item 10: renumber the trailing section to 6; no document cites the section number.

## 3. Error Handling & Edge Cases

- A finding that the code contradicts in a way the documents cannot settle (a behavior defect or a design question) is
  recorded as feedback in this Unit's `feedback/`, never decided here.
- Observations outside the 22 items, met while editing, are recorded as feedback, not fixed.

## 4. Verification & Test Plan

- Help-text items: `uv run devkit worktree status --help`, `uv run devkit spec list --help`,
  `uv run devkit sync --help`, `uv run devkit playbook search --help`.
- `just lint devkit`, `just lint devkit-spec`, `just lint devkit-dist`, and `just check` for each.
- `just test-affected` for the docstring, help and bundle edits.
- `uv run devkit sync` after the bundle edit, then `uv run devkit sync --check`.
- `just rules-check` and `uv run devkit rules check --ci --base 46229c7b`.
- Reading checks: `rg` for the stale strings of each item (`specrig` in capabilities, `rules.phases`,
  `sweep-plan`, `remains authoritative`, the duplicated citations) returns no current-state hit.
