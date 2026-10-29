---
sources:
  CAP-GOV-evaluation-lifecycle: 3e13fc27305e7933a1876ea9879a7423b5a771e0
  CAP-GOV-rule-authoring: 021370486fb2490d8cfe8e1e7df20da1260a990c
  CAP-GOV-rules-engine: fc9db7b9335944c5ef2c6554f65533f2149e07c6
  CAP-GOV-spec-rules: d6966cab23d742d0782429acf8acaba4bcbca90d
  UC-adopt-in-an-existing-repository: 37265d4dcac0d34967bb003908a49d0df4a036a8
  UC-keep-the-living-spec-consistent: 6aa78b77ed1eb5a1f7f8b59742048c01319abccc
  UC-resolve-stale-activity-branches: b19fb4071f1680f2fa080aab2b6f4b7a7d22741c
title: Governance rules
---

# Governance rules

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.5` at source commit `18b834c35c0c`, generated 2026-10-29. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](../journeys/adopt-in-an-existing-repository.md)
- [Adopt SDD from incubation](../journeys/adopt-sdd-from-incubation.md)
- [Drive development to integration](../journeys/drive-development-to-integration.md)
- [Find the right documents](../journeys/find-the-right-documents.md)
- [Handle delivery problems and exceptions](../journeys/handle-delivery-problems-and-exceptions.md)
- [Incubate an idea](../journeys/incubate-an-idea.md)
- [Incubate and hand off a proposal](../journeys/incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](../journeys/inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md)
- [Publish a weekly report](../journeys/publish-a-weekly-report.md)
- [Reconcile Living Spec drift](../journeys/reconcile-living-spec-drift.md)
- [Resolve stale activity branches](../journeys/resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](../journeys/review-and-refactor-accumulated-slop.md)
- [Route a development request](../journeys/route-development-intent.md)
- [Run parallel work safely](../journeys/run-parallel-work-safely.md)
- [Speed up selected slow operations](../journeys/speed-up-selected-slow-operations.md)
- [Advisories](advisory.md)
- [Agent-first CLI toolkit](cli.md)
- [Collaboration](collaboration.md)
- [Compact command output](compact.md)
- [Delivery](delivery.md)
- [Distribution](distribution.md)
- [Documents](documents.md)
- [Commit gates](gate.md)
- [Generated Files](generated.md)
- [Harness](harness.md)
- [Host](host.md)
- [Integration](integration.md)
- [MCP](mcp.md)
- [Search](search.md)
- [Traceability](traceability.md)
- [Viewer](viewer.md)
- [Worktree](worktree.md)
- [Decisions](../decisions.md)
- [Changes](../changes.md)
- [Glossary](../glossary.md)
<!-- /handbook:generated -->

devkit keeps repository invariants with deterministic rules instead of prompt instructions: a rule parses files and
reports a violation with a remediation, and the same verdict comes back whether you, your agent, the commit hook or
CI asks. `devkit rules` is the engine; the rules themselves mostly arrive in bundles. For how rules fit next to
bundles, gates and the Living Spec, see [Concepts](../concepts.md).

The engine knows no document model. Built-in rules cover only what holds in any repository (relative Markdown
links, file length, committed secrets, stray artifacts). Everything about specs, use cases or decisions ships as
`kind = "rule"` assets of the bundle that defines those documents, such as the document rules of the `docs` bundle
and the lifecycle rules of the `spec` bundle below.

## Check your work

| You want to | Run |
| --- | --- |
| Check the whole workspace | `devkit rules check` |
| Check only what you touched | `devkit rules check docs/a.md src/` |
| Include slower warnings (file length, stale branches) | `devkit rules check --phase hygiene` |
| Check exactly what the next commit contains | `devkit rules check --staged` |
| Check a branch as CI does | `devkit rules check --ci --base origin/main` |
| Preview fixes, then apply them | `devkit rules fix --dry-run`, then `devkit rules fix` |
| Understand one rule | `devkit rules explain RULE-markdown-link` |

Each finding is one `[VIOLATION: <RULE-id> severity= file= line= status= message= remediation= guide=]` line;
`status=fixable` means `devkit rules fix` repairs it, and `guide=` points at the deployed guide that `explain`
prints. Error-severity violations fail the command; `--format json` gives one object instead, and `--summary-only`
keeps only per-rule counts. The `[SUMMARY]` line counts the rules active in the run (`rules=N`); a run with none
active passes with `rules=0` and a `RULES_NONE_ACTIVE` notice, so it is never mistaken for a clean check. A rule
that deliberately does not apply prints a `[RULE_OMITTED: <id> code= reason=]` line (`omissions` in JSON) instead of
counting as a pass.

A fix run is one repair pass followed by one recheck, never a loop, so its cost is predictable. Fixers never move
files, never touch `.devkit/managed/` or `.devkit/overrides/`, and leave files that are not valid UTF-8 alone.

## What a run actually checks

- **Targets**: named files are checked as is, even when Git ignores them; directories expand to the files Git does
  not ignore. Without targets the run covers the whole workspace.
- **Target scoping**: a rule that reads beyond its targets declares `inputs` patterns. A targeted run skips it when
  no target matches, so a docs-only check does not pay for an architecture rule. Whole-workspace runs and CI still
  evaluate everything, so nothing is lost there.
- **Exclusions**: `exclude` under `[rules]` removes paths from every target set; they stay visible for link repair.
- **Snapshots**: `--staged` evaluates Git's index and `--ci` evaluates `HEAD` against its merge base, so unstaged
  edits and ignored local files cannot change the verdict. When your working tree already equals what you stage,
  the staged check runs in place and its cost follows the commit, not the repository size. Policy changes in
  `.devkit/config.toml` take effect in a snapshot only once staged.

This is the check the `rules-check` commit gate runs on every commit; see [Commit gates](gate.md).

## Tune policy for your project

A project never edits a distributed rule file: managed copies are hash-checked against the installation receipt
every time they load. All tuning lives in `[rules]` of `.devkit/config.toml`:

```toml
[rules]
exclude = ["docs/materials/**"]

[rules.phase_overrides]          # park a linter rule in hygiene while you clear existing debt
RULE-document-summary = "hygiene"

[rules.severity_overrides]
RULE-file-length = "error"

[rules.settings.RULE-file-length]
max_lines = 300

[[rules.settings.RULE-file-length.overrides]]
path = "docs/research/**"
max_lines = 800
```

The `linter` phase is what commits and CI enforce; `hygiene` is the wider periodic sweep. A parked rule prints its
remaining count on whole-workspace hygiene runs (`[PHASE_OVERRIDE: ... remaining=3]`), and at zero a
`RULES_PROMOTION_READY` notice tells you to delete the override. A new rule can do the same from its side with
`promote_to`. `devkit rules phases` lists default and effective phases without evaluating anything.

A whole-workspace hygiene run also calls installed hygiene extensions, which report repository state that is not a
file rule, such as stale `plan-*` and `dev-*` branches (see
[Resolve stale activity branches](../journeys/resolve-stale-activity-branches.md)). They never fail the run.

## The document and lifecycle rules

Fourteen `linter` rules keep the Living Spec and feature specs consistent. The `docs` bundle's `core` preset (from
`devkit-docs`) deploys the nine document rules; the `spec` bundle's `core` preset deploys the five rules of the
spec-driven lifecycle. All are errors except `RULE-spec-progress`, `RULE-proposal-boundaries` and
`RULE-ux-coverage`, which are warnings.

| Rule | Bundle | Keeps | Fixes |
| --- | --- | --- | --- |
| `RULE-document-reference` | `docs` | references are exact, resolvable full IDs in code-span form, also in steering files and glossary owners; no duplicate IDs or aliases | bracket form, aliases and handed-off proposal IDs |
| `RULE-id-convention` | `docs` | paths, IDs, `area` and H1 tokens agree (done and dropped milestones under `docs/roadmap/_archive/`); no date or number IDs | aligns `id`, `area`, H1 |
| `RULE-spec-format` | `docs` | required frontmatter on capabilities, use cases, UX documents, proposals, milestones | fills missing fields |
| `RULE-traceability-link` | `docs` | use case and capability links exist on both sides | appends the reverse ID |
| `RULE-code-entrypoints` | `docs` | capability and use case entrypoints exist | by hand |
| `RULE-document-summary` | `docs` | searchable documents carry a short English `summary` | by hand |
| `RULE-steering-documents` | `docs` | `docs/steering/` stays flat and small, each file with a `title` and short English `summary` | by hand |
| `RULE-ux-links` | `docs` | a UX document and the use case steps that cite it agree | by hand |
| `RULE-ux-coverage` | `docs` | the steps of a use case with screens each cite one | by hand |
| `RULE-task-coverage` | `spec` | every acceptance criterion has a task and every task reference exists | by hand |
| `RULE-spec-lifecycle` | `spec` | spec status, task checklist and reconcile status agree | sets `completed` |
| `RULE-spec-progress` | `spec` | a spec with checked tasks is `in-progress` | sets `in-progress` |
| `RULE-reconcile-contract` | `spec` | `reconcile.md` is well formed and its modified targets changed | by hand |
| `RULE-proposal-boundaries` | `spec` | a proposal's owned paths exist | by hand |

When a project's development approach is incubation (`[development] approach` in `.devkit/config.toml`), the document
rules judge as before, but the lifecycle rules apply only to documents still bound to a spec-driven workflow; with
nothing to check they report an `SDD_LIFECYCLE_INACTIVE` omission instead of a pass.

Completed spec bundles are history: they are checked only when you name them and never rewritten by a fix. Free-form
`materials/` directories are exempt. For the day-to-day loop with these rules, follow
[Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md); when adopting devkit in a
repository full of legacy documents, park noisy rules in `hygiene` as described in
[Adopt in an existing repository](../journeys/adopt-in-an-existing-repository.md).

## Write your own rule

A rule is a plugin package directory: `rule.py` with a `BaseRule` subclass, helper modules imported relatively,
`guide.md` beside it, and `tests/` that travel with it.

```text
rules/doc_heading/
  rule.py        # class DocHeadingRule(BaseRule): id, phase, severity, guide="guide.md", check(ctx)
  headings.py
  guide.md       # Overview, Cause of Violation, Remediation, Configuration, Exceptions
  tests/test_rule.py
```

- Read files through `ctx.cache` (cached text, frontmatter, links, one shared parsed Python tree) and report only
  files `ctx.is_file_targeted` accepts.
- Declare typed `settings` (a frozen dataclass), `inputs` when the rule reads beyond its targets, `related` to point
  at the instruction or playbook behind it, and `promote_to` for a rule that starts in `hygiene`.
- Implement `fix` returning the paths you wrote, writing only through `ctx.cache.write_text`.
- For Markdown, build on `devkit_agt.features.rules.scan` instead of tracking fences and comments yourself, so your
  rule agrees with devkit about what is code, a comment or a task.
- Try it with `devkit rules check --rules-dir rules`; test it with `devkit rules test RULE-doc-heading --rules-dir rules`,
  which uses `load_rule` and `check` from `devkit_agt.features.rules.services.testing`.

To distribute it, declare the directory as a `kind = "rule"` asset of your project's bundle and run `devkit sync`.
The `spec-rule` skill walks an agent through the whole procedure.

## When a run fails

| Code | What to do |
| --- | --- |
| `RULES_LOAD_FAILED` | A managed rule file is missing or drifted: run `devkit sync`, or keep a deliberate edit with `devkit override create <bundle>:<asset>` |
| `RULES_SETTINGS_INVALID`, `RULES_CONFIG_INVALID` | Correct the `[rules]` table the message names |
| `RULES_TARGET_INVALID` | Name a file or directory inside the workspace, outside managed copies |
| `DOCS_CONFIG_INVALID` | Correct the malformed `[tool.docs]` table |

Rules that pull per-file Python facts reuse them across runs from a local memo under `.devkit/transient/`; this is
derived state, so a missing or corrupt memo only costs time, never changes findings.

## Sources

- [CAP-GOV-rules-engine](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/governance/CAP-GOV-rules-engine.md):
  the engine, rule sources and per-file facts.
- [CAP-GOV-evaluation-lifecycle](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md):
  targets, scoping, phases, policy and snapshot gates.
- [CAP-GOV-rule-authoring](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/governance/CAP-GOV-rule-authoring.md):
  the rule protocol, workspace cache API and rule tests.
- [CAP-GOV-spec-rules](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/governance/CAP-GOV-spec-rules.md):
  the document and lifecycle rules in full.
- [Rules reference](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/development/reference/rules.md): commands,
  output, exit codes and the built-in rule catalog.
