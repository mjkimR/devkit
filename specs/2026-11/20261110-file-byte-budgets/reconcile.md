---
reconcile_id: REC-file-byte-budgets
status: resolved
targets:
  - file: docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-rule-authoring.md
    resolution: modified
  - file: docs/development/reference/rules.md
    resolution: modified
  - file: docs/decisions/2026-11/20261104-consolidated-record-budgets.md
    resolution: modified
  - file: docs/decisions/2026-11/20261110-byte-based-file-budgets.md
    resolution: modified
---

# Reconciliation: `SPEC-file-byte-budgets`

## Contract comparison

| Requirement | Implementation and checks | Durable reflection |
| --- | --- | --- |
| AC-01, AC-04 raw evaluated bytes | Builtin uses `len(ctx.cache.read_bytes)`; exact/UTF-8/invalid-byte/newline and real staged-versus-live regressions | `CAP-GOV-evaluation-lifecycle` section 5 File byte budget; builtin guide |
| AC-02 rule-local eligibility and precedence | Alias classifier unchanged; positive/max-precedence/lazy-header matrix preserved with byte fixtures | `CAP-GOV-evaluation-lifecycle` section 5 Rule-local consolidated record budget |
| AC-03 renamed settings and explicit migration | Typed dataclass fields/defaults, obsolete root/override keys and CLI errors tested | Both governance capabilities, rules reference and guide |
| AC-05 stable ID and advisory phase | Same rule ID/phase/severity, line-1 numeric byte diagnostic and explain fields; phase filtering tests | Evaluation lifecycle File byte budget and rules reference |
| AC-06 current policy/guidance | Project CAP/consolidated limits 65536; two source playbooks use byte keys, exact fidelity statements retained, source tests pass | `ADR-byte-based-file-budgets` and matching old-ADR partial pointer; current config/reference |

The rule remains builtin-owned and uses the existing cache/resolver API. No architecture, feature edge, package
layout or person-operated screen changes. No domain term was renamed; bytes are the existing technical unit.
The earlier ADR outcome text remains history, with only its exact partial pointer added. No required target is waived.

## Source and integrated evidence

`materials/hygiene-before.json` was captured before implementation using source 25a33dc0 and the old line config;
it contains 8 file-length warnings. `materials/hygiene-after.json` was captured at source e3717ccc with byte limits;
it contains 3 file-length warnings and no errors. Two are the original unsplit delivery CAPs in this branch;
the third is a 55,692-byte historical material. The Host separately delivered the CAP split and owns the final
combined-head hygiene result; these files do not claim its outcome.

The independent code review passed at e3717ccc; the separate reconciliation review passed at 237fa500 with no findings. Required all-tier affected tests passed 4320 at that same production
HEAD, including selected native E2E. Focused suites and builtin rule tests passed. No production change follows that
head; subsequent files hold reconciliation, measured evidence and workflow records. Native lint/types, cumulative
rules, sync and generated checks passed. The sole tracked sync output is `.devkit/installation.json`.

## Entrypoints and retained boundaries

The evaluation capability already names the builtin rule doorway. The authoring capability changes an example,
not its responsibility, so it retains its existing entrypoints. The derived config, playbook, settings-example and test paths are supporting implementation or verification,
not additional capability doorways; none is added. Existing entrypoints remain sufficient.

## Deferred work

None. Existing historical material size warnings are observations, not omitted criteria or automatic splitting
work. Host integration and final landed verification remain outside this worker turn.
