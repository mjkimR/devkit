# Viewer support matrix and Scout evidence

## Inspection and provenance

Source and contract Scouts completed at f75da999fcdff9e68559a01793efe620b3f2f570. No runtime test was run.
Tracked-plus-nonignored snapshot before/after: f6901151eecf483bfe62180c8622739e903e00bf; HEAD unchanged.
Boundaries were emulated with scoped absolute reads, explicit cwd, no writes, and snapshot comparison. No outside
worktree read was reported. The source Scout's architecture description was corrected by the worker: lines101–117
are docs package definitions, while viewer browse is lines169–172 and declares only project/shared. The frontend
marker is outside the package: scripts/affected_tests.py:128–131, inspected by the worker after Scout completion.

Core values remain provisional until Host supplies a pinned artifact: design/DESIGN/designs, domain/DOMAIN/domain,
operations/OPS/operations; id/title/status/summary, draft|active|retired; same-kind aliases; related_designs,
related_domains, related_operations plus applicable CAP/UC fields; design optional entrypoints, domain/ops none.
Independent design details are formal nodes. No role supersedes field; ADR/PADR decision UI remains. Retired nodes
must follow the delivered core's default/current and explicit historical lookup policy. Paths/layout not settled.

## Three-kind-by-surface acceptance matrix

D, N, O mean design, domain, operations. All three columns are required. P means planned and not executed.
Each result must become a named passing test or walkthrough artifact in Development; inspection alone is not PASS.

| Surface and applicability | D | N | O | Mechanism/owner and exact planned proof |
| --- | --- | --- | --- | --- |
| Identity/prefix input | P | P | P | Core-delivered valid and invalid prefix/path/H1/status fixtures; frontend consumer parity test against core definitions, no new schema authority |
| Group/order/namespace list | P | P | P | api/documents.ts:266–299 bookGroup/bookGroups; documents.test.ts; KnowledgeViews.test.ts; explicit group in global and registered fixture, nested formal detail and unregistered structural control; never Overview |
| List/search/current/history | P | P | P | KnowledgeViews.svelte:193–201 and KnowledgeSidebar.svelte; test title/body/ID/alias matches, selected namespace, retired defaults and explicit deep-linked historical node |
| Canonical ID/alias/deep links | P | P | P | api/documents.ts idIndex/renderDocument plus SddViewer.svelte; documents.test.ts and SddViewer.test.ts; canonical, alias, encoded path/anchor, duplicate/missing ID; hidden-filter target reachable |
| Prose and statement references | P | P | P | api/documents.ts:240 and document/supersession.ts:27; documents.test.ts and supersession.test.ts; every core prefix positive plus malformed/fence/comment/indented/code controls, whole/partial ADR statement targets |
| Metadata and applicable relations | P | P | P | knowledge/KnowledgeViews.svelte:290–296, document/FrontmatterHeader.svelte and new shared formal relation panel/helpers under features/document/; typed scalar/list handling, malformed metadata, all core related_* fields, entrypoints only if applicable |
| Reference graph/provenance | P | P | P | features/document/ relation projection and API ID index; new focused helper/component tests in same frontend ownership; outgoing/incoming direction, field/body origin, alias canonicalization, provenance separate, duplicate/unresolved/incomplete states |
| Current/historical | P | P | P | Preserve read source/Planning labels; retired stays accessible by explicit reference, raw source and historical links; historical completed spec/material not migrated or relabelled current; test no fabricated current authority |
| Independent details/support | P | P | P | knowledge/KnowledgeViews and document renderer plus file explorer source; real migrated design/detail, domain and ops; relative Markdown examples, diagrams/Mermaid, CSV/text, image fixtures; unsupported binary, missing artifact, sanitization, back and source isolation |
| Backend tree/blob | P | P | P | features/browse/usecases/read.py:30–51 may stay generic; extend tests/integration/features/browse/test_worktree.py or focused peer in same tier: all formal global/namespace paths and artifacts served, missing/symlink/traversal refused |
| Public frontend library | P | P | P | frontend/src/lib/index.ts, api/repository.ts and wrappers; existing SddViewer/KnowledgeViews/RepositoryDataSource/RepositoryDocument exports remain compatible, generic host source needs no new callback; pack consumer exercises kinds and artifacts |
| Static and Python wheel | P | P | P | vite.config.ts output and src/devkit_viewer/static/** generated via declared viewer-assets command; frontend checks, pack export checks, generated check and wheel asset inspection prove shipped page matches source |
| Handbook source recognition | P | P | P | scripts/handbook.py:48,56,220; tools/devkit-dev/tests/integration/test_handbook_script.py: all prefixes/aliases recognized and cited source lookup/staleness verified with missing source control |
| Handbook inclusion | P | P | P | CAP-DLV-release-handbook contract: formal sources citeable; generated decisions/changes/glossary and CAP/UC coverage requirements retain current scope; no auto page or release refresh |
| Existing-kind compatibility | P | P | P | Existing CAP/UC/UX/ARCH/ADR/PADR/spec/proposal/milestone fixtures retain groups/linking/rendering; ADR/PADR summary decision-only; dashboard milestone/proposal/feedback scope unchanged |

## File ownership and boundaries

Viewer owns frontend/src/lib/api/documents.ts, features/document/supersession.ts, features/knowledge/KnowledgeViews.svelte,
KnowledgeSidebar.svelte, document components and new helper/panel tests in those directories. frontend/src/lib/index.ts,
api/repository.ts and public wrappers change only when an additive public interface is actually required. Generic
backend code need not change; backend tests are mandatory. frontend/src/app/ and frontend tooling change only for
actual shipped integration. Static/** is generated, never hand-edited. Existing scripts/viewer.sh and generated config
are verification inputs, not an invitation to change global tooling. No backend model imports are planned.

Current documentation targets are the blueprint inventory, plus existing viewer UC/UX if their shared behavior
changes. New docs are created under nearest existing parents docs/usecases/viewer and docs/ux/viewer. The exact
UX register and CAP-DLV-release-handbook owner are added to proposal boundaries. Core owns model/grammar/authoring,
canonical migration and glossary; lifecycle owns spec/adaptive content. Shared architecture/reference contracts
are serialized by Host if edits overlap. No edits to other proposals are authorized in this turn.

## Required Development validation

Run `just lint-check`, `just check`, `just test-affected` preserving full fallback, and focused handbook integration
checks. Run `just viewer install`, lint, check, test, pack and build in that order as the frontend marker names.
`uv run devkit generated check viewer-assets` verifies generated freshness. Inspect public tarball exports and wheel
static resources; test host-backed generic RepositoryDataSource and HTTP tree/blob fixture parity. Render walkthrough
must cover every kind in global/registered namespace, reference graph, formal detail, artifact formats and negative
states. Capture results by row/kind; no cell can be retired because the code happened to be generic or small.

## Scout contract impact

Current relevant bodies: CAP-VIEW-repository-viewer; ADR-repository-viewer; ADR-viewer-namespace-roadmap-discovery;
ADR-viewer-indexed-decision-supersession; ADR-documentation-ownership-and-linked-design-entries;
ADR-linked-domain-relationship-views; UC-read-decision-supersession; UX-view-decision; UX-decision-supersession;
CAP-DOCS-documentation-ownership; glossary/register. Incoming-ref inventory is materials/incoming-refs.md, with full
lookup lists and an explicit historical-body limit. No historical record is rewritten to manufacture formal proof.
