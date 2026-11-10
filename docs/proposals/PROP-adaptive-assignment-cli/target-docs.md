---
id: PROP-adaptive-assignment-cli-target
title: Target Living Spec Structure for PROP-adaptive-assignment-cli
status: draft
proposal: PROP-adaptive-assignment-cli
created_at: 2026-11-10
# The Living Spec files this proposal changes, one "- file: <workspace-relative path>" each;
# devkit spec scope compare reads them to find overlaps with other work.
targets:
  - file: docs/capabilities/delivery/CAP-DLV-adaptive-development.md
  - file: docs/usecases/delivery/UC-advance-an-idea.md
---

# [Blueprint] PROP-adaptive-assignment-cli: Target Living Spec Structure for Assignment ledger and return verification commands for adaptive delegation

This document defines the target blueprint of how the docs/ backbone (Living Spec) will evolve if proposal PROP-adaptive-assignment-cli is accepted. It represents a hypothesis plan subject to adjustment during implementation. Upon handoff, it is copied into specs/ to serve as a baseline for plan.md boundaries and reconcile.md targets.

---

## 1. System Capabilities Plan (docs/capabilities/)

- `CAP-DLV-adaptive-development`: add rules for recording an assignment, recording and verifying a return and
  listing outstanding assignments, with their codes and tests. Rules 13, 13a and 14 name the commands as the way a
  Host meets them where the commands are available. The runtime scheduler and agent bus exclusions stay.
- Planning decides whether the command contract stays in this capability or moves to a new capability in the
  delivery area.

---

## 2. Use Cases Plan (docs/usecases/)

- `UC-advance-an-idea`: extensions 5b, 5c and 7b gain the recorded assignment, the verified return and the resume
  from recorded assignments. One scenario covers an out-of-scope return and one covers resume after an interruption.

---

## 3. Architecture & Decision Impact (docs/architecture/ & docs/decisions/)

- `ARCH-05-2-components`: the feature added to `devkit-adaptive` and its declared feature edges.
- Candidate decisions: ledger location and format; required versus optional harness dependency.

---

## 4. Development Conventions & Governance (docs/development/ & .devkit/)

- A reference page for the command group under `docs/development/reference/`.
- Bundle guidance in the entry skill's delegation, orchestration and current-context references names the commands.

---

## 5. System Before & After Comparison (Before & After)

| Aspect | Before | After |
| --- | --- | --- |
| Assignment board | Host context | Recorded ledger |
| Return check | Host reads the diff | Command compares paths, base and checks with the assignment |
| Resume after interruption | `.devkit/adaptive-dev.md` if it was updated | Outstanding assignments listed from the ledger |
| Scheduler, runner, hooks | None | None |
