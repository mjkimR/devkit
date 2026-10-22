---
id: SPEC-exact-playbook-get
title: Exact playbook retrieval for external runners
summary: Add exact bundle/playbook retrieval with effective overrides, source identity and context requirements while defining external ownership of scheduling and execution.
status: completed
created: 2026-10-21
milestone: MS-scheduled-jobs
related_capabilities: [CAP-DIST-context-and-playbooks]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-exact-playbook-get] Exact playbook retrieval for external runners

## 1. Problem Statement & Motivation

Handed off from proposal PROP-exact-playbook-get on 2026-10-21.
- **Preserved Materials**: `docs/materials/2026-10/20261021-exact-playbook-get`

### 1. Background & Hypothesis

`MS-scheduled-jobs` requires an exact-ID entrypoint for a caller that already knows which synchronized playbook
to run. Search and candidate selection are unnecessary in that case. `CAP-DIST-context-and-playbooks` remains
the consumption contract; an explicit retrieval operation can provide instructions without executing them or
introducing scheduling into devkit.

## 2. User Stories

- **US-1**: As a calling agent, I want the exact synchronized playbook and context requirements so that I can follow an explicitly requested procedure without catalog discovery.

## 3. Non-Goals

1. **Scope Excluded**: Scheduling, execution, retries, job history, provider adapters, implicit synchronization, catalog discovery and new override/render semantics.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Exact complete retrieval
- **Given** a synchronized Markdown or directory playbook.
- **When** its exact bundle/asset ID is retrieved.
- **Then** the JSON result contains complete unchanged body, effective metadata, canonical identity, absolute path, byte hash and context requirements; unsupported CLI options and missing arguments exit 2.

### [AC-02] Effective source integrity
- **Given** an ordinary override or modified/missing managed source.
- **When** retrieval reads its effective entrypoint.
- **Then** live override edits are returned, missing or modified sources fail without fallback and unrelated stale personal-render evidence retains its existing error.

### [AC-03] Deterministic errors
- **Given** malformed selectors, absent selections or invalid receipt entrypoints.
- **When** retrieval is attempted.
- **Then** the resolution/error table below defines the code, exit and action; existing transaction, unsafe-path and lock failures pass through without search or package enumeration.

### [AC-04] Complete non-executing read
- **Given** a body larger than search budgets with relative resource links.
- **When** retrieval succeeds.
- **Then** all body whitespace is preserved, resources remain unread and project content/selection/receipt remain unchanged except existing lock infrastructure.

### [AC-05] Workspace and snapshot
- **Given** unsynced selection edits and a caller in a project subdirectory or using -w.
- **When** retrieval runs.
- **Then** the receipt snapshot governs selection and the context instruction targets the same workspace with once-per-agent-context guidance, including empty context.

### [AC-06] Explicit invocation policy
- **Given** an explicit exact request or configured external schedule.
- **When** the caller follows consumption guidance.
- **Then** documentation permits that invocation while preserving unsolicited-discovery prohibitions, fresh prerequisite checks and all workflow/permission gates.

## 5. Detailed Contract and Design Evidence

### 2. Technical Spike Findings

Receipt-owned reads already provide the synchronization, override, personal-render and shared-lock semantics
needed here. There is no exact playbook retrieval service to reuse wholesale. Add a small
`installation/playbook_get.py` service using the existing reading and header primitives, without search ranking,
installed-package discovery or an alternate manifest resolver. The comparison and evidence are in
`docs/materials/2026-10/20261021-exact-playbook-get/retrieval-design.md`. `ADR-external-playbook-execution` records the responsibility boundary.

### 3. Proposed Design & Impact

#### Exact input and output contract

`devkit playbook get <bundle>/<playbook> [-w <workspace>]` accepts exactly two case-sensitive manifest slugs
matching `[a-z][a-z0-9-]*`, separated by exactly one slash. It performs no trimming, case folding, alias lookup,
path interpretation, extension removal, fuzzy match or fallback. The second component is the manifest asset ID,
not frontmatter `name`. No search bounds, search mode or truncation apply.

Like `get-context` and `playbook search`, this is a JSON-only command using the existing `_json_command` boundary:
default output is one JSON object. No `--format` option is exposed; both `--format json` and `--format text`
are unsupported Click usage errors (exit 2), as for the adjacent JSON-only commands.
Success exits 0. Libraries return data and do not print. The normative success object has these fields:

- `bundle`, `id`: the canonical manifest identity requested.
- `name`, `description`, `aliases`: validated effective playbook header metadata.
- `body`: the complete decoded UTF-8 text after the closing frontmatter delimiter line, preserving its whitespace and
  newlines; no stripping, truncation, interpolation, resource expansion or execution. Header extension keys remain
  ignored and are not returned separately.
- `source`: `{path, sha256}` where `path` is the absolute effective entrypoint and `sha256` hashes the exact bytes
  read, including frontmatter. This is a content identity, not a package-source URL or execution attestation.
  Ordinary overrides name the override path; unoverridden playbooks name the managed entrypoint. Bundle and asset
  ID stay canonical even when the override changes the header name.
- `context`: `{bundle, argv, policy}` with the same bundle, `argv: ["devkit", "get-context", "<bundle>"]`, and
  `policy: "once-per-agent-context"`. Run that argv in the same resolved workspace (or pass its `-w`) before
  following the procedure unless this bundle context is already loaded; reload after it is lost. Apply the full
  constitution and read relevant instruction bodies. Retrieval does not load context or keep execution state.

Relative resource links in `body` resolve against the parent of `source.path`; the caller reads only needed
resources using existing permissions. No resource bytes or directory inventory are returned.

#### Resolution and errors

Validate the selector first, resolve the synchronized project and take the existing shared project lock, then
use `read_synchronized` and its runtime receipt. Match exactly one receipt asset of kind `playbook` by bundle/id.
The asset must have exactly one entrypoint, belonging to its recorded paths and the allowed managed or override
prefix of that bundle. Read it using `read_owned`; validate the header and UTF-8 before constructing the result.
No source-tree, installed-wheel, stale managed-file or alternate-playbook fallback is permitted.

All domain failures below use the existing JSON error envelope and advisory action text, no partial success body,
exit 2. Click syntax failures (missing/extra arguments or unsupported options) retain the existing usage-error
channel and exit 2; they are not promised a domain JSON envelope:

| Condition | Stable code | Required action/fix |
| --- | --- | --- |
| Malformed selector | `ARGUMENT_INVALID` | Correct `<bundle>/<playbook>`; identify `PLAYBOOK_ID` as target |
| Bundle absent from synchronized receipt | `SELECTION_INVALID` | Inspect `devkit list`; do not guess installation/selection |
| No matching playbook in a synchronized bundle (unknown, wrong kind or unselected asset) | `SELECTION_INVALID` | Inspect `devkit list` and explicit bundle/preset selection |
| No receipt, missing effective entrypoint or modified managed content | `NOT_SYNCHRONIZED` | `devkit sync` |
| Stale/missing personal render evidence | `CONFIG_LOCAL_RENDER_STALE` | `devkit sync` |
| Invalid receipt or zero/multiple/unowned/wrong-bundle entrypoints | `RECEIPT_INVALID` | Repair the receipt using the existing receipt advisory |
| Invalid effective UTF-8 or frontmatter | `BUNDLE_INVALID` | Fix the named effective source; sync when changing managed source content |

Unknown and unselected identities intentionally share `SELECTION_INVALID`: the deployed receipt cannot prove
which one applies. No new package inventory lookup is added to distinguish them. Existing transaction, lock,
unsafe-path and configuration advisories pass through unchanged. Evaluation order is argument validation,
project/receipt/runtime validation, bundle presence, exact asset match, entrypoint ownership, file read, content
validation. This preserves the existing personal-render failure scope, including unrelated stale local evidence.

The synchronized receipt is the deployment snapshot, not a live desired-state calculation: changing selection
configuration without syncing does not itself remove a still-recorded asset. Retrieval never changes selection,
receipt, managed content or overrides and never syncs. Existing shared-lock transient-file behavior and read-only
filesystem fallback remain as in context/search. Ordinary overrides are read as currently edited. Playbook templates are not supported by the current manifest
validator; this feature adds no template or personal-render playbook support. Shared runtime-receipt validation
still checks evidence for eligible other asset kinds, so their stale evidence can block the read.

#### Explicit invocation and ownership

A user naming the exact playbook for the current task, or explicitly configuring an external schedule to invoke
that exact ID, authorizes retrieval and caller interpretation within that task's granted scope. Retrieval itself
cannot verify authorization and grants none. Ordinary task wording does not authorize catalog discovery or
playbook selection. Existing explicitly invoked discovery and failing-rule remediation remain supported.
Each external run starts fresh procedure progress, checks prerequisites and obeys all project workflow gates,
permissions and user constraints. A schedule is neither persistent approval for future gated operations nor
permission to skip unavailable approval UI. External systems own cadence, launch, retries, overlap control and
execution history; devkit only supplies the synchronized task instructions and context requirements.

#### Development targets and verification

Development adds the retrieval service, result model, CLI wiring and focused tests under the existing distribution
and test directories. Update `CAP-DIST-context-and-playbooks`, `ARCH-08-2-resource-taxonomy`,
`ARCH-05-4-distribution-components`, the affected distribution quick reference, generated `devkit-playbook`
skill source and distribution guide source; promote the PADR to an ADR. Review introductory architecture and
installation guides for inconsistent invocation wording and change only affected statements. Never edit generated
managed files. No new always-loaded scheduling policy is needed; the ADR holds the decision and rationale.

Run `just lint-check dist`, `just check dist`, `just test-affected`, focused retrieval/CLI/override tests and the
dist-only check as appropriate to command wiring. Run governance checks over changed contracts and cumulative
branch changes. No live external scheduler integration is required. Planning itself validates its documentation
and envelopes; it does not implement or execute these future feature tests.

Non-goals: scheduler, daemon, job registry, schedule configuration, provider adapters, dispatch/retry/overlap logic,
playbook execution inside `get`, new maintenance assets, durable execution history, unattended approval bypasses,
new override/render semantics, catalog discovery during exact lookup and a package provenance/audit subsystem.

### 4. Lifecycle & Retirement Criteria

Feature / proposal depth. Planning and recommended Development effort remain medium: the scoped service reuses
existing integrity primitives but adds a public CLI contract and an invocation-policy ADR requiring independent
review. No unresolved business choice is required for this direction. Acceptance, Development start and milestone
status transitions remain the Host/user's responsibility.

