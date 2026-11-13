---
id: FB-integration-prune-without-proposal
title: Integration plans a proposal prune for a spec-depth Unit that never had a proposal
scope: repo
kind: friction
category: other
target: devkit integration integrate
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-11-13
---

# [FB-integration-prune-without-proposal] Integration plans a proposal prune for a spec-depth Unit that never had a proposal

Category other: cleanup-plan noise in integration output.

## 1. Friction / Question (friction, question)

- **Context**: Local integration of a consumer `dev-<slug>` branch for a `spec`-depth Unit created with
  `devkit spec new` (no proposal).
- **Expectation**: The cleanup plan names only cleanup that applies.
- **Actual**: `devkit integration integrate` planned and reported a proposal-prune step for
  `docs/proposals/PROP-<slug>/`, which never existed. The worker paused to check whether a proposal was missing.
- **Workaround (or Interpretation Chosen)**: Proceeded; the prune removed nothing.
- **Suggestion**: Plan the `proposal-prune` target only when `docs/proposals/PROP-<slug>/` exists in the base, or
  when the Unit records a handoff from a proposal.

## Diagnostic Details

- **Reproduction**: Integrate a `spec`-depth Unit branch with `devkit integration prepare` and `integrate --route
  local`; exact output not retained.
- **Expected / Actual**: Expected no prune target; actual a planned prune of a non-existent directory.
- **Versions**: devkit `569379a06`: `packages/devkit-spec/src/devkit_spec/features/delivery/usecases/cleanup.py`
  derives `expected_prune` from the branch slug alone.
- **Conditions**: consumer repository, `dev-integration` local route.
- **Workarounds Attempted**: none needed.
- **Related Assets**: `cleanup.py` (`_parse_targets`, `KIND_PROPOSAL`), `CAP-DLV-proposal-lifecycle`.

## Evidence

```text
cleanup.py: slug = _prune_slug(slug_of(context.finish.branch))
            expected_prune = (CleanupTarget(KIND_PROPOSAL, proposal_unit(slug), context.finish.source_sha),) if slug else ()
```


## Disposition

Resolved by `SPEC-conditional-proposal-prune`. Scoped integration omits proposal-prune for a spec-only slug with no committed proposal history, while source/target history retains handoff cleanup and retry identity. Verification: 17 cleanup integration tests, including merged add/delete history, exact-target tampering and partial-failure recovery; 53 delivery integration/plan-accept E2E tests and the final affected suite of 1821 passing tests; independent review finding fixed and self-reverified. The before/after probe reduced spec-only targets from 1 to 0, preserved handoff targets at 1, and retained the same identity after prune.
