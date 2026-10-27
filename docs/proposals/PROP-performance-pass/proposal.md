---
id: PROP-performance-pass
title: Performance pass maintenance playbook
summary: Add a maintenance playbook that measures, profiles and applies behavior-preserving performance changes to user-selected commands with differential preservation evidence, separate from review-refactor.
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-27
target_area: delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-maintenance-operations
boundaries:
  owns:
    - delivery/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-performance-pass] Performance pass maintenance playbook

## 1. Background & Hypothesis

A performance pass over this repository on 2026-10-27 (rules check 3.0s to 1.7s, a one-file commit-gate check 0.92s
to 0.38s, `sync --dry-run` 1.25s to 1.14s) borrowed the `maintenance/review-refactor` procedure, but its goal is
latency, not a smaller surface, and it needed steps that playbook does not have: a measured baseline, profiling
without being misled by profiler inflation or child processes, per-component timing, and differential old/new
comparisons as preservation evidence. A fresh review still found a regression (a symlink loop breaking every file
listing) that tests missed.

Hypothesis: a separate, router-structured maintenance playbook that turns a user-selected set of slow operations into
measured, behavior-preserving changes with differential evidence makes such passes repeatable in any repository and
keeps `review-refactor` focused on maintenance cost.

## 2. Technical Spike Questions

- **Q1**: Which entry modes does the router need (a measurement-only survey, a targeted pass on named commands or
  checks, a regression investigation), and what does each load?
- **Q2**: What measurement protocol is portable: warm-up, repetitions and the statistic reported, cold versus warm
  caches, machine noise and concurrent load, and how a baseline is recorded so a later run can compare?
- **Q3**: How does profiling guidance stay language-neutral while naming the known traps (deterministic profiler
  inflation, work in child processes, garbage collection and allocation, caches rebuilt on the first run)?
- **Q4**: What does a decision round show (each candidate with its measured share, expected saving and risk), and
  which changes count as behavior-preserving versus contract changes (output, caching across runs, concurrency)?
- **Q5**: Which parts are shared with `review-refactor` (parallel application in isolated checkouts, differential
  comparison, adversarial review, report) and how are they referenced rather than copied?

## 3. Proposed Design & Impact

- A directory-form playbook `maintenance/performance-pass` in the `maintenance` catalog bundle, authored with the
  `authoring/skill-authoring` playbook as a router: `SKILL.md` holds entry, intake, mode selection and completion;
  references hold measurement, profiling, candidate evaluation and the decision round, application and evidence, and
  the report.
- Application reuses the `review-refactor` procedure for parallel disjoint-scope changes and differential evidence
  (`CAP-DLV-review-refactor`) by reference.
- Living Spec: a capability under `docs/capabilities/delivery/`, a use case, the bundle preset and the content-package
  capability's asset list; handbook entries follow at the next release.

## 4. Lifecycle & Retirement Criteria

- Accepted when Planning answers Q1 to Q5 and the router layout passes the authoring playbook's size and structure
  rules.
- Retire or merge into `review-refactor` if a later run shows the two playbooks share most of their procedure.
