---
id: MAT-architecture-evidence
title: Shared artifact architecture evidence
summary: "Repository evidence distinguishes durable scope coordination, ephemeral artifacts, configuration ownership and MCP execution constraints."
created_at: 2026-10-21
---

# [MAT-architecture-evidence] Shared artifact architecture evidence

Evidence gathered by a nested read-only scout at medium Planning effort. No production backend, live host transport
or permission experiment was run. Role boundaries were emulated, checked against unchanged index/HEAD and the two
expected edited proposal files.

| Question | Repository evidence | Design consequence |
| --- | --- | --- |
| Authority | scope/localfs.py:334 checks token, last request and revision; :372 token-checks release | Preserve registry; report content grants no approval |
| Storage | scope/location.py:63 and :164 resolve common directory and private worktree token | Do not move records/tokens into artifact namespace |
| Read-only | core/locks.py:57 creates write-open locks; scope/localfs.py:88 has no-follow read-open locking | Implement noncreating shared read lock; no lazy sweep on reads |
| Foundation | dist/tests/distsupport/layering.py:23 limits core imports | New devkit.shared area has explicit core/advisory-only dependencies and layering tests |
| Configuration | core/local_config.py:55 allowlists tables; :115 uses explicit workspace | Validate shared table; preserve owning-workspace selection |
| MCP | core/mcp.py:20, devkit_mcp/services.py:26, server.py:72, core/mcp_context.py:68 | Add bounded_write explicitly; cloud remains read-only |
| Exclusions | host/registrations.py:260 and CAP-MCP-runtime-registration | Narrow info/exclude with common lock and all-worktree conflict checks |
| Remote | Draft requires real cross-host access but selects no provider/authentication | Ask first-delivery scope; a test adapter is not production evidence |

Paths with abbreviated prefixes are relative to their package source roots: scope is devkit-spec/devkit_spec;
core and host are devkit-dist/devkit; devkit_mcp is devkit-mcp. Exact role evidence is in envelopes/scout-01.yaml.

The scout recommended core/shared as one feasible owner. Planning selects a distinct devkit.shared area because it
owns a cohesive domain API and CLI/service wrappers, while core remains shared primitives. This is a deliberate
new layering inventory entry, not an import from a higher layer into core. Exclusion helper extraction, if needed,
belongs in core so neither shared nor core imports host registrations.

Alternative comparison and measurable acceptance fixtures are in PROP-worker-shared-state-mcp. The remote decision
is preserved in the worker questions rather than guessed from the absence of provider credentials.

## Cloud rendering feasibility evidence

Direct source inspection after the local MCP-first routing requirement:

- distribution/bundles/templates.py:39 accepts only presentation.language for default_from; :43 resolves bundle
  values and language; :95 renders only the scalar vars mapping.
- distribution/installation/sync.py:344 passes variables and language; :961-963 builds canonical/effective
  inventories before :1003 calls plan_environment. --cloud is not a prospective Jinja input.
- distribution/installation/local_render.py:69 digests bundles/presentation, :155 activates evidence on those keys,
  and :187 validates the same local-render evidence. Execution is absent from these decisions.
- `CAP-DIST-manifest-spec` permits templates only for instruction/guidance/document/skill; constitution and subagent
  source rendering are excluded. local_render.py:105 refuses guidance/seed/structure changes by local values.
- rg found MCP text in spec source subagents/planning-worker.md and development-worker.md, skills/spec-integrate/
  SKILL.md, skills/spec/references/worktree.md, completion.md and backlog.md, plus dist guide consumption.md.

This is sufficient to reject a claim that existing --cloud automatically hides MCP today. It supports a rendering
extension, but not a whole-repository no-MCP guarantee. No cloud rendering probe or real host discovery test ran.
