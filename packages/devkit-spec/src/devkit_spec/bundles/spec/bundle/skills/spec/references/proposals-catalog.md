# Proposals

Proposals mature features, spikes and architectural improvements, each as a bundle directory `PROP-{slug}/`.

## 1. Lifecycle

- **Draft & Review (`draft` / `reviewing`)**: in Backlog, scaffold with `devkit spec proposal new <slug>` (`--task-kind bugfix` for a defect) and state the core hypothesis and spike questions in `proposal.md`. Planning runs on `plan-<slug>` ([planning](planning.md)). Preliminary decisions go in `decisions/PADR-{slug}.md`, research in `materials/`.
- **Graduation (`accepted`)**: `plan-accept`, recorded with `devkit spec proposal accept` after Planning or directly for an eligible draft in Backlog, sets `status: accepted`. Accept and handoff may share one request or happen separately. `devkit spec proposal handoff <slug>` then starts Development: it creates the spec at `specs/{YYYY-MM}/{YYYYMMDD}-{slug}/` bound to `sdd-spec-<task_kind>`, carries the `plan-intent` and `plan-accept` records, promotes PADRs into `docs/decisions/`, moves `materials/` and any other bundle file (such as a `notes.md`) into `docs/materials/`, copies `target-docs.md` (if present) to the spec directory, rewrites Markdown links and ID references into the bundle, and removes the bundle directory. Follow up the reported unresolved links (`spec-next` skill).
- **Rejection (`rejected`)**: changes the status only, then a later hygiene cleanup (the `sdd-proposal` workflow's Gate rules).
- Git history keeps historical context; keep no `archive/` directories.

## 2. Bundle layout and frontmatter

```text
docs/proposals/PROP-{slug}/
├── proposal.md            # (Required) background, hypothesis, spike questions, non-goals
├── target-docs.md         # (Recommended) target Living Spec changes upon acceptance
├── decisions/             # (Optional) preliminary decision records (PADR-{slug}.md ...)
└── materials/             # (Optional) on-demand research, benchmarks, external surveys
```

- **`proposal.md` frontmatter**: written by `devkit spec proposal new`; the template
  (`.devkit/managed/spec/templates/proposal.md`) annotates the fields. `planning_effort` / `dev_effort` are
  non-authoritative hints ([effort](effort.md)); `handoff` returns `dev_effort`, and the applied effort is recorded only
  on `worker-NN.yaml` envelopes, never copied to `spec.md`.
- **`materials/` Markdown**: file `{YYYYMMDD}-{slug}.md`, `id: MAT-<slug>`, `created_at`, H1 `# [MAT-<slug>] <title>`; recommended, not checked (`RULE-spec-format` skips `materials/`). Non-Markdown files need no metadata. After handoff the files move to `docs/materials/`. Research retained outside the proposal (an indexed material under `docs/materials/`) is cited by its `MAT-<slug>` ID in a code span and never copied into `materials/`.
- **`target-docs.md`**: what `docs/` will look like once accepted (`proposal.md` holds the why): capability ledger, use cases, architecture and decisions, conventions and governance, before/after comparisons. Recommended for `size: M/L` or expected Living Spec structural changes.
- **`size: XL`**: decompose it before `plan-intent` ([XL size gate](backlog.md#the-xl-size-gate)).

## 3. CLI

Keep no proposal tables in README files; the CLI reads frontmatter:

```bash
devkit spec proposal new <slug>                        # scaffold a proposal bundle
devkit spec proposal new <slug> --milestone MS-<slug>  # with an existing milestone (an MS ID, not free text)
devkit spec proposal new <slug> --with-target-docs     # with target-docs.md
devkit spec proposal new <slug> --task-kind bugfix     # a defect: the spec follows sdd-spec-bugfix
devkit spec proposal new <slug> --planning-effort low --dev-effort high  # explicit effort hints
devkit spec proposal new <slug> --needs-decompose      # split in Backlog before Planning
devkit spec proposal padr <slug> <title> --summary <text>  # PADR; the promoted ADR keeps the summary
devkit docs list proposal                              # list proposals
devkit spec proposal handoff <slug>                    # graduate (scaffold spec, remove bundle)
```
