# Proposals

A proposal matures a feature, spike or architectural improvement as a bundle directory `PROP-{slug}/`. Keep no
proposal tables in README files; `devkit docs list proposal` reads frontmatter. Git history keeps historical context;
keep no `archive/` directories.

## 1. Lifecycle

- `draft` / `reviewing`: in Backlog, scaffold with `devkit spec proposal new <slug>` (`--task-kind bugfix` for a defect) and state the core hypothesis and spike questions in `proposal.md`. Planning runs on `plan-<slug>` ([planning](planning.md)).
- `accepted`: `plan-accept`, recorded with `devkit spec proposal accept` after Planning or directly for an eligible draft in Backlog, sets `status: accepted`. Accept and handoff may share one request or happen separately.
- `devkit spec proposal handoff <slug>` starts Development: it creates the spec at `specs/{YYYY-MM}/{YYYYMMDD}-{slug}/` bound to `sdd-spec-<task_kind>`, carries the `plan-accept` record, promotes PADRs into `docs/decisions/`, moves `materials/` and any other bundle file (such as a `notes.md`) into `docs/materials/`, copies `target-docs.md` (if present) to the spec directory, rewrites Markdown links and ID references into the bundle, and removes the bundle directory. Follow up the reported unresolved links (`spec-next` skill).
- `rejected`: changes the status only, followed by a later hygiene cleanup (the `sdd-proposal` workflow's Gate rules).

## 2. Bundle layout and frontmatter

```text
docs/proposals/PROP-{slug}/
├── proposal.md            # (Required) background, hypothesis, spike questions, non-goals
├── target-docs.md         # (Recommended) target Living Spec changes upon acceptance
├── decisions/             # (Optional) preliminary decision records (PADR-{slug}.md ...)
└── materials/             # (Optional) on-demand research, benchmarks, external surveys
```

- `proposal.md` frontmatter: `devkit spec proposal new` writes it and `.devkit/managed/spec/templates/proposal.md`
  annotates the fields. `planning_effort` / `dev_effort` are non-authoritative hints ([effort](effort.md)); `handoff`
  returns `dev_effort`, and the applied effort is recorded only on `worker-NN.yaml` envelopes, never copied to `spec.md`.
- `materials/` Markdown: name it `{YYYYMMDD}-{slug}.md` with `id: MAT-<slug>`, `created_at` and H1 `# [MAT-<slug>] <title>`; recommended, not checked (`RULE-spec-format` skips `materials/`). Non-Markdown files need no metadata. Cite research retained under `docs/materials/` by its `MAT-<slug>` ID in a code span, never copied into `materials/`.
- `target-docs.md`: what `docs/` will look like once accepted (`proposal.md` holds the why): capability ledger, use cases, architecture and decisions, conventions and governance, before/after comparisons. Recommended for `size: M/L` or expected Living Spec structural changes.
- `size: XL`: decompose it before Planning ([XL size gate](backlog.md#the-xl-size-gate)).
