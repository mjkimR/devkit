# Findings from the first handbook refresh

Reported by the writers of the v0.1.4 handbook while reading the Living Spec at 3da97383. Each item names where the
documents disagree; the shipped code and CLI decide which side is current.

## Delivery

1. Gate policy values: `CAP-DLV-workflow-orchestration` §3 and `CAP-DLV-project-policy` §4.1 (`GATE_POLICY` values)
   list `ask`, `auto` or `off`; `CAP-DLV-project-policy` rule 4 and `CAP-DLV-delivery-workflows` §4.3 accept only
   `ask` or `auto`. The error code also differs: `UC-route-development-intent` extension 2a and scenario 3 and
   `CAP-DLV-project-policy` say `SPEC_CONFIG_INVALID`; `CAP-DLV-delivery-workflows` §4.3 says workflow commands stop
   with `WORKFLOW_GATE_POLICY` and `devkit spec policy` "reports the same rule".
2. `CAP-DLV-proposal-incubation` rule 14 says `accept` never commits, merges or hands off; its later "Host-authorized
   proposal lifecycle CLI" section has `accept --mode accept_only|accept_and_handoff` committing the acceptance,
   merging the Planning branch and optionally handing off.
3. `CAP-DLV-proposal-incubation` rule 15 says acceptance needs no shared artifact report, while its summary says it
   "publish[es] source-bound Planning reviews before acceptance". `UC-incubate-and-hand-off-a-proposal` summary and
   success guarantee say one source-bound review is "published"; its extension 7a describes a native MCP handoff form,
   while `CAP-INT-mcp-services` and `CAP-MCP-runtime-registration` say lifecycle operations run only through
   Host-authorized CLI commands.
4. `proposal-handoff` is a gate in `CAP-DLV-delivery-workflows` §4.3 and in project policy, but no workflow stage
   declares it.
5. `CAP-DLV-workflow-orchestration` keeps a "Relationship to specrig" section and uses specrig as its layout example
   (an old name).
6. Stage names: `CAP-DLV-workflow-orchestration` lists "intent, specify, build, review, reconcile, integrate"; the
   glossary `Stage` entry lists `intent`, `specify`, `build-verify`, `handoff`. Neither may match the shipped workflow
   definitions (`uv run devkit workflow show <id>`).

## Integration, MCP, host

7. `CAP-INT-mcp-services` says `ADR-local-and-pull-request-integration` "remains authoritative for merge construction
   and route guards", but that ADR is `superseded`.
8. Shared artifact MCP tools: `CAP-MCP-runtime-registration` lists put and apply-sweep as bounded writes and get, list
   and sweep-plan as read-only; `CAP-COLL-shared-artifacts` and
   `packages/devkit-dist/src/devkit_dist/features/shared/mcp.py` expose only put, get and list.
9. MCP registration hosts: `CAP-HOST-lifecycle-observation` summary and §8 name only Codex and Claude Code;
   `CAP-MCP-runtime-registration` and `registrations.py` also handle Antigravity (`.agents/mcp_config.json`);
   `devkit mcp setup` in `docs/development/reference/host.md` takes only `--host codex|claude`.
10. `CAP-HOST-lifecycle-observation` numbers its sections 1-5, then 8.
11. `CAP-VIEW-repository-viewer` §3 says the viewer has no connection to "the integration MCP tools", which
    `CAP-INT-mcp-services` says are no longer registered.

## Worktrees, documents, generated, distribution

12. `CAP-WT-task-worktrees` §7 lists `cli.py` as `devkit worktree start|finish|status|stale`; §6 and the code use
    `devkit worktree status --stale` with no `stale` subcommand; the `cli.py` docstring also says `stale`.
13. `CAP-DOCS-document-lookup` rule 3.4.1 lists the `devkit spec list` KIND values without `milestone`, while its own
    example runs `devkit spec list milestone --history` and `CAP-DOCS-document-model` defines the `MS` kind; the CLI
    help KIND list also omits it.
14. `CAP-GEN-tracked-artifacts` never mentions `devkit generated list`, which the CLI provides.
15. `CAP-DIST-sync-and-transactions` §1 and "Locked Synchronization" open with host-hook sentences before the receipt
    is introduced.
16. `devkit sync --registrations-only` exists but no capability documents it (likely MCP-owned).

## Governance and advisory

17. `CAP-ADV-agent-advisory-protocol`'s example error uses fix `Set [rules.phases] RULE-x = "linter"`, but the
    documented table is `[rules.phase_overrides]` and accepts only `"hygiene"`.
18. `devkit rules --help` hides the `phases` and `test` subcommands that the governance capabilities document.

## Duplicate or self citations, glossary

19. `ARCH-01-introduction-and-goals` cites `ADR-roadmap-and-milestones` twice in a row; `ARCH-05-1-containers` does
    the same with `ADR-package-split-and-namespaces` and `ADR-viewer`; `CAP-VIEW-repository-viewer` with
    `ADR-roadmap-and-milestones`; `CAP-DIST-content-packages` §5 with `ADR-response-style`;
    `CAP-DLV-project-policy` §1 cites `ADR-worktrees-branches-and-scope` as "refined by" itself. Each likely replaced
    a superseded ID; restore the intended pair or drop the duplicate.
20. The glossary has no `Host` entry although worktree, integration and project-policy contracts use it throughout.

## Open feedback in the same area

21. `FB-workspace-root-help-resolution-order` (specs/2026-10/20261026-review-refactor/feedback/): the `-w` help of the
    distribution commands describes root resolution in the wrong order.
22. `FB-classification-maintenance-playbook-case` (same directory): the spec bundle's classification criteria have no
    case for a maintenance playbook run, which `ADR-apply-behavior-preserving-batches-as-direct-mode-refactors` now
    refines.
