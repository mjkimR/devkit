# Baseline reuse and interface evidence

Inspected baseline: `828d5b45fc8c66ff4ea2eff4b77b50febf28d2aa` plus proposal-only Planning commits. No implementation or consumer experiment is claimed.

| Option | Evidence | Cost / limitation | Recommendation |
| --- | --- | --- | --- |
| Brownfield adoption unchanged | `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/brownfield-adoption/SKILL.md:8-13,65-78` installs SDD, contains debt, permits gradual migration and completes after one real SDD change. | A passing rule baseline is not verified retained-product coverage. | Keep for legacy containment; do not redefine its completion as incubation readiness. |
| Feature-only spec-sync | `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-sync/SKILL.md:8-17,25-58` starts after feature review and records targets under that Unit. | Requires an artificial historical Unit to describe pre-SDD implementation. | Reuse templates and comparison method; no retroactive Unit. |
| Maintenance drift playbook | `CAP-DLV-drift-reconciliation` sections 3–4 compare bounded implementation/docs and record evidence, decisions and gaps. | Opt-in maintenance bundle and no adoption readiness/activation contract. | Reuse method without adding an installation dependency. |
| Explicit baseline playbook in spec | Existing manifest registers brownfield-adoption as a playbook (`packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/bundle.toml:213-215`). | Adds one discoverable asset and semantic exercise coverage; preparation needs policy to leave incubation active while spec is installed. | Recommended; smallest additional entry that owns transition rather than another runtime workflow. |

The roadmap's optional transition defines retained behavior, structure, decisions and verification evidence (`MS-idea-incubation`, Optional transition and final two exit conditions). The proposed record is a normal material report with explicit scope, revision and coverage. Its report status is human evidence, not a new machine checker or policy source.

Prerequisite interfaces remain semantic. Policy Planning owns activation/inspection and suppression boundaries. Guidance Planning owns entry routing and live context; no filename is assumed here. Before Development, refresh accepted prerequisite contracts and narrow exact integration checks. These proposal drafts authorize no prerequisite implementation.

Read-only Scout left HEAD and snapshot unchanged: `80f832ad9cd7b2d2e6f81380e470f240cdff253b`, tree `91748a694dcde4cd798242e2d205612d83f9c33e`. Codex emulated boundaries use absolute worktree paths and before/after snapshots rather than a native host guarantee.
