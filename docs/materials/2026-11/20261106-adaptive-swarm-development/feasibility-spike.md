# Adaptive Subagent Feasibility Spike

## 1. Identity and Boundary

- Planning source SHA: `86eb5bd1b706ec586ebbdbd76ad4840ae22c00b2`.
- Inspected on: 2026-11-06; the runtime's product version was not exposed by the collaboration tools.
- Scope: repository source feasibility, temporary consumer projection, and one read-only depth-two role invocation.
- No retained catalog source, host configuration, development approach or production code was changed by the probes.
- The prototype used the workspace runtime; it was not a fresh isolated wheel installation.

## 2. Source Review

The Scout compared `CAP-DIST-agent-projections`, `CAP-DIST-manifest-spec`,
`CAP-DIST-in-repo-bundles`, the adaptive bundle and its integration/E2E tests.

| Question | Evidence | Planning conclusion |
| :--- | :--- | :--- |
| Public identity and collisions | packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/subagents.py:154; CAP-DIST-agent-projections section 1 | Prefixes name public asset IDs; they create no new namespace. Project agents use distinct IDs. |
| Common contracts and host keys | packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/subagents.py:25,84 | Existing schema accepts three archetypes with every host declared; no distribution change is needed. |
| Project model policy | packages/devkit-dist/src/devkit_dist/features/distribution/services/subagents.py:101,139; CAP-DIST-sync-and-transactions shared subagent policy | Use owning bundle:asset keys, not prefix routing. Leave source defaults inherited. |
| External role callers | packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/subagents.py:158 | Omit skill prerequisites; the caller provides the bounded role path/text and follows its own lifecycle. |
| Local role paths | authoring bundle's skill-authoring role guidance | Resolve from the invoked skill; pass the verified absolute path, not a reference-relative path. |
| No-SDD installation | packages/devkit-catalog/tests/e2e/bundles/adaptive_dev/test_installed_consumer.py:13 | Existing wheel exercise excludes devkit-spec; docs currently brings devkit-agt through packages/devkit-docs/pyproject.toml. |
| Verifier writes | spec bundle code-reviewer/development-worker probe clauses | Test/probe output needs a narrow assigned write scope even when product source and Git are read-only. |
| Partial ADR supersession | packages/devkit-spec/src/devkit_spec/features/proposals/usecases/handoff.py:777 | Existing supersedes/supersedes_clause metadata adds the prior ADR pointer; no handoff change is needed. |

No new package, feature dependency edge, distribution key or runtime scheduler was identified as necessary.

## 3. Projection and Extension Probe

The reproducible script is [projection-probe.py.txt](projection-probe.py.txt), a Python source artifact with a text
suffix to keep it separate from installed runtime and test tiers. Run it from the same source tree with a fresh
absolute output directory; it leaves its generated consumers for inspection:

```bash
uv run --no-sync python <proposal-materials>/projection-probe.py.txt \
  --workspace-root <absolute-worktree> --output-root <fresh-absolute-temporary-directory>
```

The script copied the adaptive bundle into its temporary directory, added prototype common contracts and an `agents`
preset, then called existing `load_bundle`, `update_config` and `sync_project` APIs. It did not install these prototype
agents into the active session. A second temporary bundle supplied `acme-security-reviewer`.

| Observation | Actual result | Limit |
| :--- | :--- | :--- |
| Three archetypes plus project extension, three native targets | Twelve expected native agent files present | Projection only; no host executed these files |
| Owning bundle model policy | adaptive-dev:swarm-worker selected lean; acme-team:acme-security-reviewer selected compact | Configuration output, not model quality or runtime selection |
| agents-only consumer | Only swarm-planner/worker/verifier projected; adaptive skill/pointer and current context absent | Generic distribution guidance still writes AGENTS.md |
| Duplicate public swarm-worker | BUNDLE_CONFLICT; existing Codex projection bytes unchanged | Collision rejection is not a prefix namespace |
| No spec assets or product state | No managed spec directory and no adaptive context seeded | Workspace runtime still contains SDD packages; isolated wheel proof remains Development work |
| Bundle validation and Codex plan | validate reported adaptive-dev 0.1.6 with nine assets; plan included all three new IDs | Temporary source, not retained implementation |

The first agents-only assertion incorrectly expected no root AGENTS.md. The observed file contained distribution's
generic managed guidance, so the corrected check asserts absence of the adaptive entry pointer instead.
The corrected fresh-directory run passed. This is a probe expectation correction, not a production defect.

## 4. Read-only Nested Role Probe

The Host assigned one lead with at most one child and no third child level. The actual tree was
`/root` → `/root/nesting_probe_lead` → `/root/nesting_probe_lead/interface_auditor_child`.
The child used a fresh context and read the absolute task role file
`/tmp/adaptive-swarm-planning-86eb5bd1/roles/interface-auditor.md`.
Its content is retained as [interface-auditor-role.md](interface-auditor-role.md).

- The child extracted inherit, minimal, compact, lean, standard, deep and maximal from
  `CAP-DIST-agent-projections` lines 126–135. The lead independently checked that evidence.
- A follow-up reused the same child and deliberately asked for an incompatible write without a target path.
  The child returned `needs_input` and `WRITE_DENIED`, attempted no mutation, and spawned no descendant.
- One child was created and reused; no concurrent children or third child level were observed.
- HEAD stayed at the source SHA. Before/after alternate-index trees matched
  `7e8fcf157f96016e0f44cf81182e95dd412a2972` for both read-only support assignments.
  The only pre-existing dirty path was the Host's return-to-spike decision record.

This establishes role-path delivery, one nested call, continuation and instruction-level refusal in this session.
It does not establish native permission/depth enforcement, generic thread-slot release, code-writing teams, worktree
integration, interruption handling or performance. Unchanged snapshots cannot rule out every transient mutation.

## 5. Official Host References

The following primary pages were opened on 2026-11-06, separately from the source/projection observations.

- [OpenAI Subagents — custom agent schema](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agent-file-schema):
  custom sandbox/approval fields do not override the parent session. The plan therefore treats Codex boundaries as
  emulated and does not use the declared sandbox value as evidence of confinement. The page also documents a
  global concurrent-thread setting; this plan neither changes it nor assumes it matches another runtime's accounting.
- [Claude Code — nested subagents](https://code.claude.com/docs/en/sub-agents#let-subagents-spawn-their-own-subagents):
  nested agents are documented, with effective depth/tool limits. The plan includes Agent for role leads and keeps
  nesting conditional on the actual runtime. The native Claude runtime was not exercised.

Antigravity nested execution remains unverified. Capability availability is checked at dispatch; the fallback is
flat/direct/sequential work under existing authority, never an automatic host-setting change.

## 6. Decision and Remaining Implementation Evidence

Select three prefixed archetypes, an agents-only preset, caller-owned overlays and optional role leads. Keep source
model defaults omitted. Give the verifier assigned scratch writes while preserving product/Git read-only authority.
Keep concurrent writers in separate worktrees and final integration with the Host.

The ordered implementation outline and AC mapping are in `SPEC-adaptive-swarm-development` and its carried implementation outline.
Development must retain real assets, exercise project extension and agents-only behavior from wheels without SDD,
and record representative coding, combined-failure and interruption outcomes or explicit unavailable coverage.
No measured performance or universal host-support claim is promoted from this spike.
