# Applying agreed changes

The application procedure is the resolved `review-refactor` text; this file names the sections that apply,
overrides three points and adds the performance evidence.

## 1. Sections that apply

Follow these sections in order:

1. `review-refactor references/applying.md "Branch and edit tasks"`; the branch follows override 3.
2. `review-refactor references/applying.md "Subagent edits"`.
3. `review-refactor references/applying.md "Commits and verification"`.
4. `review-refactor references/criteria.md "Preservation evidence"`, including its differential comparison.
5. `review-refactor references/applying.md "Review"`.
6. `review-refactor references/applying.md "Report"`.
7. `review-refactor references/applying.md "Integration"`; the path follows override 3.
8. `review-refactor references/applying.md "Contract removals"`, without its compatibility-policy exception: a
   removed option is a contract change.

The work item's route is the entry file's decision round route, not
`review-refactor references/applying.md "Work items and route"`.

## 2. Overrides

1. Every difference found by the differential comparison or the review is a contract change: fix it so old and new
   agree, or return the change to the decision round as its own contract-change work item. `review-refactor`'s
   approved behavior change inside the behavior-preserving work item does not apply.
2. Edit tasks may run in parallel in isolated checkouts, but every timing run waits until no edit task or
   verification runs; schedule measurements between edit tasks.
3. The work item's branch and integration path are those of the feature workflow the decision round routed it to,
   whatever the number of modules it edits. Text of the cited sections naming the overall-refactor workflow's branch
   policy or integration path (with the `spec` bundle, task kind `overall-refactor`) does not apply.

## 3. Per-change measurement

1. Measure each change by the measurement protocol: old is the previous checkpoint, new is that checkpoint with only
   this change applied, same input, same session, interleaved.
2. Record in the commit body, beside the preservation evidence: target, state, run count, median, minimum and range
   for old and new, the noise floor and the load before and after.
3. If the median difference is below the noise floor, record "no measurable change" and return the change to the
   decision round, unless the user approved it for another reason the measurement shows (fewer subprocesses, lower
   peak memory).

## 4. Differential inputs

Run old and new on the repository's own corpus plus the input domain's edge and error cases, since a faster API
often differs on error paths and unusual states. Include at least those that apply to the changed code:

- empty, malformed or unclosed input;
- unreadable entries (a file or directory without read permission);
- symbolic link loops and links into unreadable directories;
- differently spelled paths (case, Unicode normalization, relative against absolute, trailing separators);
- a vanished working directory, and a file removed between listing and reading;
- for a cache: off, cold and warm, and an entry written by the previous format;
- for a memo: inputs that differ only in a value outside the memo key, and a failing call repeated.

Record the input count and the result. Compare stdout, stderr, exit codes and written files, not only return values.

## 5. Reviewer brief additions

Add to the brief of the cited "Review" section:

- each change's classification and its claim of equal behavior;
- the error paths of every replaced API (which inputs raise, return a default or skip), old against new;
- cache invalidation (version, fingerprint, what makes an entry stale) and memo keys (every input that changes the
  answer, and whether a failure is memoized).

Handle each confirmed difference by override 1.

## 6. Final measurement

At the work item's final head, after the full verification and with no edit task or verification running:

1. Measure every target interleaved against the intake revision in one session, by the measurement protocol, in each
   state the baseline recorded.
2. Record the result in the work item's report and in the run report beside the baselines.
3. If a target shows no measurable change against the intake revision, report it in those words; never cite the
   per-change figures as the run's saving.
