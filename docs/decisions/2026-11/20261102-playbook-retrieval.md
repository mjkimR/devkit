---
id: ADR-playbook-retrieval
title: External scheduling and exact playbook retrieval by ID or alias
summary: "For callers that know a playbook, we retrieve synchronized procedures by exact ID or declared alias without fallback or execution authority, leaving scheduling and execution external and aliases as identifiers, to keep devkit focused on delivery, accepting a breaking playbook format change."
status: accepted
created_at: 2026-11-02
aliases:
  - ADR-external-playbook-execution
  - ADR-playbook-aliases-as-identifiers
---

# [ADR-playbook-retrieval] External scheduling and exact playbook retrieval by ID or alias

- **Status**: Accepted
- **Date**: 2026-11-02
- **Involved Components/Capabilities**: `CAP-DIST-context-and-playbooks`, `ARCH-08-2-resource-taxonomy`,
  `CAP-SRCH-document-search`

---

## 1. Context & Problem Statement

`MS-maintenance-operations` requires callers that already know a playbook ID to retrieve a task without discovery.
`ARCH-08-2-resource-taxonomy` describes explicit skill invocation or rule remediation as the entry conditions.
Scheduled invocation needs an explicit boundary that preserves task-specific authority.

A playbook's optional `aliases` frontmatter array held English search keywords that `devkit playbook search` indexed
beside `name` and `description` (`CAP-DIST-context-and-playbooks`), while Living Spec documents use an `aliases` field
with another meaning: previous or alternate identifiers (`ADR-document-id-aliases`). One field name with two meanings
in one toolkit misleads authors and agents. The playbooks in the devkit-spec, devkit-agt, devkit-catalog and
devkit-starter bundles used the keyword form.

---

## 2. Decision Drivers

- Keep devkit focused on asset delivery, reuse synchronization and override integrity. (ADR-external-playbook-execution)
- Retain explicit invocation, and avoid inferring execution permission from successful retrieval or a recurring
  trigger. (ADR-external-playbook-execution)
- One meaning for `aliases` across devkit: an identifier, never a keyword. (ADR-playbook-aliases-as-identifiers)
- Search quality must not depend on a keyword list: hybrid ranking over `name` and `description` already carries the
  meaning, and the description can absorb any phrase worth keeping. (ADR-playbook-aliases-as-identifiers)
- No external consumers exist, so the format changes in place without a migration path or a deprecated reader.
  (ADR-playbook-aliases-as-identifiers)
- Retrieval by exact identity with no fallback selection, and naming the exact playbook as explicit invocation, hold;
  an alias must fit that rule rather than reverse it. (ADR-playbook-aliases-as-identifiers)

---

## 3. Considered Options

- **Add a devkit scheduler and execution runtime** (rejected in `ADR-external-playbook-execution`): it adds persistent
  operational state, provider policy, retries and approval ownership outside the agreed task.
- **Require external runners to search or read an assumed managed path** (rejected in
  `ADR-external-playbook-execution`): search is unnecessary and paths bypass effective override and synchronization
  checks.
- **Provide exact receipt-backed retrieval, with scheduling and execution external** (selected in
  `ADR-external-playbook-execution`): the proposal defines the bounded result and errors; existing readers retain
  integrity and overrides.
- **Keep keyword aliases** and give document identifiers another field name (rejected in
  `ADR-playbook-aliases-as-identifiers`): two concepts stay, one is renamed.
- **Rename the playbook keyword field** (for example `keywords`) (rejected in `ADR-playbook-aliases-as-identifiers`):
  keeps the keyword mechanism under a new name.
- **Unify under the identifier meaning** (selected in `ADR-playbook-aliases-as-identifiers`, decided by the user): the
  keyword mechanism is removed.

---

## 4. Decision Outcome

We adopt exact receipt-backed retrieval with external scheduling and execution, and playbook aliases as identifiers.

### Retrieval and execution boundary
- Devkit provides `playbook get <bundle>/<playbook>` as a non-executing synchronized instruction retrieval contract.
  (ADR-external-playbook-execution)
- External systems own scheduling and launching; the calling agent owns procedure execution, prerequisite checks and
  progress. (ADR-external-playbook-execution)
- An explicitly configured schedule naming the exact ID is task-specific explicit invocation, as is a user's direct
  request naming it. Neither grants extra permission or approval for gated operations.
  (ADR-external-playbook-execution)
- Existing explicit discovery and failing-rule remediation remain valid. (ADR-external-playbook-execution)
- Intake discovery with confirm-first invocation: see `ADR-decision-ledger`.
- The service reads the receipt's deployed snapshot and effective bytes through existing shared-lock readers; it does
  not rediscover installed packages, synchronize implicitly, or offer fallback selection. It returns full procedure
  body, canonical bundle/asset identity, effective path and byte hash, and context-loading requirements. No
  package-source attestation is implied by that content hash. (ADR-external-playbook-execution)

### Aliases as identifiers
- A playbook's `aliases` declares previous asset IDs of that playbook in the same bundle (the `[a-z][a-z0-9-]*`
  manifest slug grammar, not frontmatter `name`), decided by the user in Planning.
  (ADR-playbook-aliases-as-identifiers)
- `devkit playbook get <bundle>/<alias>` resolves an alias: an exact asset ID always wins; otherwise the alias resolves
  only when exactly one effective playbook header of that bundle (overrides included) declares it, and the result
  reports the canonical `id` and the alias used in an `alias` field (`null` on an exact hit). An alias declared by more
  than one effective playbook is refused with `PLAYBOOK_ALIAS_AMBIGUOUS`. The effective-header alias check runs only
  after the exact match misses, so an exact ID is served without it. (ADR-playbook-aliases-as-identifiers)
- A declared alias is the playbook's own identity, not fallback selection, so a request or schedule naming an alias is
  explicit invocation of the canonical playbook that `get` reports. The "no alias lookup, no fallback" sentence of the
  `CAP-DIST-context-and-playbooks` resolution contract changes accordingly, and its invocation section states the alias
  case; no ADR file changes. (ADR-playbook-aliases-as-identifiers)
- Aliases are unique against the bundle's playbook IDs and the other playbooks' aliases, checked when the bundle
  manifest is validated, and again over effective headers at retrieval because an override can change them.
  (ADR-playbook-aliases-as-identifiers)
- `devkit playbook search` indexes only `name` and `description`; aliases are not ranked.
  (ADR-playbook-aliases-as-identifiers)
- The bundled playbooks drop their keyword lists, moving any phrase worth keeping into the description.
  (ADR-playbook-aliases-as-identifiers)

---

## 5. Consequences

- **Positive**:
  - Callers can retrieve a known playbook without search dependencies. (ADR-external-playbook-execution)
  - A renamed playbook keeps its published `<bundle>/<old-id>` selectors working.
    (ADR-playbook-aliases-as-identifiers)
- **Negative / Risks**:
  - Callers must provide an appropriately synchronized workspace, load required bundle context and preserve all
    project/host approval boundaries. Unavailable approval UI does not authorize execution. Schedule retries,
    concurrency, history and recovery stay outside devkit. (ADR-external-playbook-execution)
  - Breaking change to the playbook asset format, made in place: a keyword list that is not a valid identifier list is
    refused at bundle validation. (ADR-playbook-aliases-as-identifiers)
- **Follow-ups**:
  - The capability, resource taxonomy and consumption guidance must reflect explicit exact invocation consistently.
    (ADR-external-playbook-execution)
  - `CAP-DIST-context-and-playbooks` (resolution order, error table, invocation),
    `docs/development/reference/distribution.md`, `ARCH-08-2-resource-taxonomy`, `CAP-SRCH-document-search` (the
    metadata example), the projected playbook skill text and the bundled playbooks change with the alias decision.
    (ADR-playbook-aliases-as-identifiers)

---

## 6. Confirmation

- No live scheduler integration proves or gates the retrieval and execution boundary.
  (ADR-external-playbook-execution)
