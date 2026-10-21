---
id: MAT-cloud-rendering-audit
title: Cloud rendering evidence and surface audit
summary: "Source evidence and required audit dispositions for execution-aware cloud agent rendering."
created_at: 2026-10-21
---

# [MAT-cloud-rendering-audit] Cloud rendering evidence and surface audit

Evidence is from the Planning worktree at initial commit ec92741d49c633a389eb624cc87a232534fca478.
This is a static audit, not implemented behavior or an exhaustive proof of cloud output.

## Rendering evidence

| Source location | Finding and Development consequence |
| --- | --- |
| `packages/devkit-dist/src/devkit/distribution/installation/sync.py:330,959,1003,1061` | Inventory lacks execution input and persistence occurs later; resolve once before both inventories |
| `packages/devkit-dist/src/devkit/distribution/bundles/templates.py:15,25,66` | Kinds exclude subagent, renderer exposes vars only; add a bounded reserved execution mapping |
| `packages/devkit-dist/src/devkit/distribution/bundles/manifest.py:113,263` | Constitution discovery is AGENTS.md only; subagent source parsed before rendering; explicitly discover AGENTS.md.jinja and reject coexistence |
| `packages/devkit-dist/src/devkit/distribution/installation/inventory.py:155,314,335` | Constitution copied raw; native variants have host-specific formats; render common contract before validation and retain variant constraints |
| `packages/devkit-dist/src/devkit/distribution/installation/local_render.py:24,71,96,180` | Personal-kind limits and digest/receipt validation need preserved semantics and selected render-mode binding |
| `packages/devkit-dist/src/devkit/core/receipt.py:62,145,182,298` | Closed schema, no generic metadata field; add a typed execution_environment field rather than overload tool identity |
| `packages/devkit-dist/src/devkit/distribution/installation/sync.py:1024` | Locked sync already checks canonical/tracked effects; maintain refusal |
| `packages/devkit-dist/src/devkit/core/local_config.py:152` | Runtime environment resolver remains independent and workspace-bound |

## Reachable source surfaces

Paths below are relative to `packages/devkit-spec/src/devkit_spec/bundle/` unless stated otherwise.

| Surface | Known source | Disposition |
| --- | --- | --- |
| Constitution | `AGENTS.md:57` | Convert to explicit template, retain common authority boundaries in both modes |
| Worker contracts | `subagents/planning-worker.md:72`, `subagents/development-worker.md:77` | Template host-neutral contract, remove transport-specific references from cloud while retaining Host ownership |
| Integration skill metadata/body | `skills/spec-integrate/SKILL.md:3,78` | Template metadata and body; cloud only supported inspection and separately authorized route, never invented auto mutation |
| Orchestration and proposal review | `skills/spec-orchestrate/SKILL.md:35`, `skills/spec-review-proposal/SKILL.md:11` | Local connection checks remain local; cloud provides applicable CLI/Host path |
| Planning references | `skills/spec/references/backlog.md:35,109` | Template the reference and keep rendered links resolvable |
| Completion references | `skills/spec/references/completion.md:12,18,69`, `git-policy.md:11`, `worktree.md:10,28` | Cover positive and negative MCP routing wording with mode-specific transport wording |
| Additional references | `skills/spec-delegate/references/hosts.md`, `skills/spec-next/references/workflow-signals.md` | Classify operational mentions and template only where required |
| Workflow prose | `workflows/sdd-session-feature.md`, `workflows/sdd-spec-feature.md` | Transport-neutral prose; no Jinja or executable gate changes |
| Distribution consumption | `packages/devkit-dist/src/devkit/distribution/guide/bundle/instructions/consumption.md:13,92` | Configuration key reference can remain descriptive; conditional operational setup must be cloud-safe |
| Source install guides | `guides/INSTALL_GUIDE.md:100`, `guides/install/new-repository.md:84`, `guides/install/existing-repository.md:112`, `guides/install/mcp.md:1` | Clearly separate local optional onboarding from cloud setup; outside rendered corpus |
| Other selected maintained bundle assets and variants | Inventory-driven enumeration in Development | No whole-kind exclusions; fail test for unclassified reachable operational guidance |

The initial search found no MCP matches under the harness/authoring bundle guide paths. This does not substitute
for the Development inventory audit. Custom overrides and third-party content require their owners to author
appropriate templates; they are outside the content guarantee. All selected maintained operational output is
checked, including raw managed references and native projections, not only SKILL.md entry files.

## Verification entrypoints

Extend `packages/devkit-dist/tests/distribution/test_templates.py`, `test_local_config.py` and
`test_subagent_contracts.py`, core receipt tests and spec bundle content tests. Include projectless planning,
packaging, no-selected-agent validation, raw overrides and receipt/context consumers. Run the proposal's acceptance
matrix under local and cloud modes, combined with language preferences. No runtime tests were executed in Planning.
