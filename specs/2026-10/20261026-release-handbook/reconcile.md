---
reconcile_id: REC-release-handbook
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-release-handbook.md
    resolution: modified
  - file: docs/architecture/ARCH-07-deployment.md
    resolution: modified
  - file: docs/architecture/ARCH-05-1-containers.md
    resolution: modified
  - file: docs/architecture/ARCH-05-2-components.md
    resolution: modified
---

# Reconcile: `SPEC-release-handbook`

- **`CAP-DLV-release-handbook`** (new): the handbook contract: layout, provenance and staleness, the refresh and
  verification rules, the release check, and the `just handbook` commands, sentinels and codes as
  `scripts/handbook.py` implements them. Its entrypoints are the playbook and the script.
- **`ARCH-07-deployment`**: section 1.2 adds the optional handbook refresh to release preparation and the
  release-script check (refreshing release detected from the committed manifest tag; every other release skips).
- **`ARCH-05-1-containers`**: the `devkit-dev` definition names the handbook playbook and its root script.
- **`ARCH-05-2-components`**: the `tools/devkit-dev` sentence names the handbook playbook next to its rules.

## No impact

- **Use cases**: no use case's goal changes. Releasing has no use case, and the refresh is a maintainer procedure the
  playbook describes; `related_usecases` stays empty and the capability lists none.
- **Glossary**: "handbook" is used in its ordinary sense and introduces no contract term beyond the capability, so
  `docs/glossary.md` is unchanged.
- **Writing instructions, document index, search and viewer**: unchanged by design (`SPEC-release-handbook`
  Non-Goals 4 and 6); `handbook/` lies outside the index's source directories.
- **`ADR-handbook-on-request-release-snapshot`, `ADR-localized-handbook-language-exception`**: implemented as
  accepted; no decision changes.

## Deferred work

- **First snapshot**: produced by the first user-requested refresh through the `devkit-dev/handbook` playbook during a
  release preparation (`SPEC-release-handbook` Non-Goal 1). No follow-up record is created, because the ADR leaves the
  timing to the user.
- **Deployment of the playbook into this repository**: `devkit sync` writes `.devkit/managed/devkit-dev/` and
  `.devkit/installation.json`, outside this unit's write scope; the Host runs it with the integration
  (`uv run devkit sync`), after which `devkit playbook get devkit-dev/handbook` resolves.

- **`docs/development/ci-cd.md` section 3 (Release Automation)**: should gain one sentence naming the handbook
  release check, which runs only for a refreshing release, with pointers to `ARCH-07-deployment` section 1.2 and
  `CAP-DLV-release-handbook`. The file is outside this unit's write scope; the canonical contract (`ARCH-07-deployment`)
  is reflected, so the secondary description is incomplete, not contradictory. The Host adds the sentence at
  integration or widens the scope for it.

## Feedback in this unit

- The unit addresses no source feedback. `FB-reverify-reopens-earlier-resolutions` was captured during Planning
  (target `devkit workflow envelope reverify`); this unit does not address it, so it stays open for its owner.
