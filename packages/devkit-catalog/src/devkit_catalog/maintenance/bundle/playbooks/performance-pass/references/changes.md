# Applying agreed changes

Read once the decision round approved changes. The application procedure is `review-refactor`'s, resolved as the
playbook's entry file describes; this file names the sections that apply, overrides two points and adds the
performance evidence.

## 1. Sections that apply

Follow these sections of the resolved `review-refactor` text, in order:

1. `review-refactor references/applying.md "Branch and edit tasks"`: the work item's own branch, dirty paths that do
   not belong to the run, edit tasks with write scopes.
2. `review-refactor references/applying.md "Subagent edits"`: isolated checkouts, disjoint write scopes, results
   moved onto the branch one at a time.
3. `review-refactor references/applying.md "Commits and verification"`: verification before and after each change,
   one commit per change, full verification at the final head.
4. `review-refactor references/criteria.md "Preservation evidence"`, including its differential comparison of old
   and new code on the same inputs.
5. `review-refactor references/applying.md "Review"`: a fresh reviewer before integration.
6. `review-refactor references/applying.md "Report"`: the work item's report in the final response and the commit
   body.
7. `review-refactor references/applying.md "Integration"`: the repository's integration path and its own approval.
8. `review-refactor references/applying.md "Contract removals"`: for an approved removal, its own work item. Its
   compatibility-policy exception does not apply here: a removed option is a contract change.

The route of the work item is this playbook's decision round route;
`review-refactor references/applying.md "Work items and route"` is not followed.

## 2. Overrides

1. Every difference found by the differential comparison or the review is a contract change. Fix it so old and new
   agree, or return the change to the decision round as its own contract-change work item.
   `review-refactor`'s approved behavior change inside the behavior-preserving work item does not apply to this run.
2. Edit tasks may run in parallel in isolated checkouts, but every timing run waits until no edit task or
   verification runs. Schedule the measurements between edit tasks, never beside them.

## 3. Per-change measurement

1. Measure each change by the measurement protocol: old is the previous checkpoint, new is that checkpoint with only
   this change applied, same input, same session, interleaved.
2. Record in the commit body, beside the preservation evidence: target, state, run count, median, minimum and range
   for old and new, the noise floor and the load before and after.
3. If the median difference is below the noise floor, record "no measurable change". Return the change to the
   decision round unless the user approved it for another reason (fewer subprocesses, lower peak memory) that the
   measurement shows.

## 4. Differential inputs

Run old and new on the repository's own corpus plus the input domain's edge and error cases. A faster API often
differs from the one it replaces on error paths and unusual states, not on the corpus. Include at least those that
apply to the changed code:

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

Ask for the inputs or states under which behavior differs, each with a reproduction. Confirm each reported difference
against the code, then handle it by the first override.

## 6. Final measurement

At the work item's final head, after the full verification and with no edit task or verification running:

1. Measure every target interleaved against the intake revision in one session, by the measurement protocol, in each
   state the baseline recorded.
2. Record the result in the work item's report and in the run report beside the baselines.
3. If a target shows no measurable change against the intake revision, report it in those words; never cite the
   per-change figures as the run's saving.
