# Proposals

A Planning space to propose and mature new features, technical spikes, or architectural improvements. Every proposal is managed as an isolated bundle directory (`PROP-{slug}/`).

---

## 1. Lifecycle Principles

- **Draft & Review (`draft` / `reviewing`)**: Scaffold the bundle using `devkit spec proposal new <slug>` and define the core hypothesis and spike questions in `proposal.md`.
- **Graduation (`accepted`)**: When accepted, handoff creates execution specifications under `specs/` and promotes preliminary decisions to `docs/decisions/`.
- **Rejection (`rejected`)**: Marked rejected with rationale, then cleaned up during hygiene sweeps.

## 2. Bundle Layout

```text
docs/proposals/PROP-{slug}/
├── proposal.md            # (Required) Core proposal: background, hypothesis, spike questions
├── target-docs.md         # (Recommended) Blueprint of target Living Spec changes
├── decisions/             # (Optional) Preliminary decision records (PADR-{slug}.md)
└── materials/             # (Optional) Spikes, benchmarks, surveys
```

Assign an existing repository milestone with `--milestone MS-<slug>`; the field is an MS ID, not free text.
