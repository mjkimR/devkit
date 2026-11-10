---
reconcile_id: REC-uiux-improve-ooux-impeccable
status: pending
targets:
  - file: docs/capabilities/delivery/CAP-DLV-uiux-improvement.md
    resolution: modified
  - file: docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md
    resolution: modified
  - file: docs/architecture/ARCH-05-2-components.md
    resolution: modified
  - file: docs/decisions/2026-11/20261105-uiux-improvement-workflow-boundary.md
    resolution: modified
---

# Reconcile: `SPEC-uiux-improve-ooux-impeccable`

Targets follow `PROP-uiux-improve-ooux-impeccable-target`.

## Capability

`CAP-DLV-uiux-improvement` keeps its ID. Title, summary, entrypoint and section 1 name the `app-uiux-improve` bundle,
software-interface scope, object framing and optional Impeccable delegation, citing `ADR-impeccable-session-authority`
beside `ADR-uiux-improvement-workflow-boundary`. Scope adds object framing, user-selected delegation and
user-requested setup and cleanup (In-Scope), Impeccable's contracts and non-software domains (Out-of-Scope) and
vendored external prompt text (Scope Excluded). Rule 1 names `app-uiux-improve:core`, the undeployed guide and the
renamed test; rule 3 covers accepted session changes; rule 4 adds the framing clause; rule 9 hands the session to
rules 15 to 18; rule 10 adds the unavailable-Impeccable clause; rule 13 names the renamed E2E path; rules 15 to 19 are
new. Section 4 names the new commands and registration, the session return, the guide and the restated ownership
sentence.

## Use case

`UC-improve-an-interface-and-user-flow` keeps its ID and main scenario. The entrypoint is renamed, step 3 adds the
framing, extensions 3c, 3d, 6b, 6c and 7a and scenarios 7 to 9 are added, and the postconditions keep consumer-owned
files in place.

## Architecture

`ARCH-05-2-components` names `app-uiux-improve` under `devkit_catalog/app_uiux_improve/bundle/`, Impeccable as an
optional external skill and the undeployed human usage guide.

## Decision

`ADR-uiux-improvement-workflow-boundary` Decision Outcome clause 1 names `app-uiux-improve`; the decision is
unchanged. The "Superseded in part by" pointer below its heading is the Host's post-handoff line and is not edited
here.

## Other references

`packages/devkit-catalog/README.md` and `guides/install/bundle-recommendations.md` name the new bundle and link or
describe the guide. `CAP-DLV-design-exploration` cites the capability by its kept ID and needs no change. No glossary
term is introduced or renamed. No screen is drafted, so no UX document is written.

## Entrypoints

`devkit spec entrypoints derive` proposed configuration, README, guide and test paths; none is a doorway. Both
documents keep the renamed `SKILL.md` as their only entrypoint, which the rename commit already updated.

## Deferred work and source feedback

None. The unit's Planning feedback `FB-handoff-pointer-owner-docstring-mismatch` targets `devkit-spec` handoff
docstrings outside this change and stays open for the Backlog.
