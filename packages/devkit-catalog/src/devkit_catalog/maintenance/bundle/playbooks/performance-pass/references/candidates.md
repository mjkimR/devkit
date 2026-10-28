# Candidates and the decision round

Read before the decision round. A candidate is a proposed change with a measured cost behind it; the decision round
decides every candidate of the run together.

## 1. Candidate record

Record per candidate:

- Key: a report-local key.
- Location: file and symbol at the recorded revision, dirty content included.
- Mechanism of the cost: repeated work, per-item system calls, subprocesses, allocation or a slower algorithm.
- Measured share: the share of the target metric the location owns, measured unprofiled, with its state (`warm`,
  `cold`).
- Proposed change: what replaces what.
- Expected saving: an estimate derived from the share (the share the change removes), labelled as an estimate until
  the change is measured.
- Risk: the inputs or states under which the new code could behave differently from the old.
- Classification: behavior-preserving or contract change (section 3).
- Planned differential inputs: the corpus and the edge and error cases the comparison will run.
- Route, edited paths and write scope (section 5).

## 2. Selection

1. Drop a candidate whose expected saving is below the noise floor and count it in the coverage.
2. Report a measured cost no change can remove (for example a probe whose answer is not known in advance) as `keep`,
   with the reason.
3. Prefer removing repeated work (one scan instead of many, a memo within one run, fewer processes) over
   micro-optimization of a single call.
4. Search open follow-ups (feedback, proposals, issues) before creating one; reuse a match and link earlier report
   keys. On a repeat run, recheck the earlier dispositions.

## 3. Classification

Classify by observable behavior, not by the size of the edit.

Behavior-preserving: for every accepted input, these stay the same: stdout, stderr, exit codes, written files and
their bytes, persisted formats that other versions or tools read, error behavior (which inputs fail and how) and the
order of observable side effects.

- A change to a private cache's format qualifies when a version or fingerprint invalidates old entries and outputs
  are identical with the cache off, cold and warm.
- A memo within one run qualifies when its key covers every input that changes the answer and it never memoizes a
  failure.

Contract change, each its own work item:

- changed output: content, order or format;
- new state kept between runs where none existed (a cache file, a daemon);
- concurrency or parallelism that can change ordering, errors, locking or resource use;
- changed defaults, accuracy or error handling;
- a removed option.

If a candidate's classification depends on an input you have not checked, classify it as a contract change until
the differential comparison shows otherwise.

## 4. Presentation

Present all candidates of the run in one round, ranked by expected saving. Give each its key, location, mechanism,
measured share, proposed change, expected saving, risk, classification, planned differential inputs and proposed
disposition. Present dropped candidates as a count and kept costs with their reasons.

- Present each contract change apart from the behavior-preserving candidates, naming the observable difference.
- Leave an unanswered candidate pending; nothing is applied for it.

## 5. Route and write scope

1. Put the run's agreed behavior-preserving changes into one work item, whether it edits one module or several.
2. Route it through the repository's feature workflow at the depth its own classification gives (with the `spec`
   bundle, `session` when no contract or specification text changes).
3. Route each agreed contract change as its own work item through the repository's normal development workflow.
4. Do not follow `review-refactor references/applying.md "Work items and route"`; its direct-mode overall-refactor
   route belongs to `review-refactor` runs.
5. State the route and the edited paths in the round. The edited paths, following edits included (tests of the
   changed code, documentation naming it), are the write scope; keep every edit inside it.
