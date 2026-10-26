# Applying agreed changes

Read when a decision round approved changes. The applied work is refactoring, not feature development: you work with
the user in the conversation, with no planning or development worker and no work unit, unless the route below sends a
work item to the feature workflow.

## 1. Work items and route

1. Put the batch's agreed behavior-preserving changes into one work item; make each approved contract change its own
   work item (§8).
2. Apply the single-module test once per work item: it is a single-module refactor when every source file its agreed
   changes edit, call sites, imports and re-exports included, lies inside one feature or module of the repository's
   declared layout. Leave following edits out of the test. Examples in a layered monorepo: one feature directory or
   one package-level module of one package; on the guidance surface, one skill, playbook or instruction; on the CLI
   surface, one command group's module.
3. Route the work item:
   - Several modules: the repository's workflow for a behavior-preserving refactor across several areas (with the
     `spec` bundle, `sdd-overall-refactor`), even though the decision round agreed its changes, because the run's
     direction settles batch by batch with the user.
   - One module: the repository's feature workflow at the depth its own classification gives (with the `spec`
     bundle, `session` when the change touches no contract and no specification text).
   - No declared layout: name the route with the edited paths in the decision round; the user's approval settles it.
4. State the route, the test result and the edited paths in the decision round. Never split or merge a work item to
   change its route.
5. The batch's write scope is the edited paths the decision round states for its agreed changes, following edits
   included. Keep every edit inside it.

Where the repository has no refactor workflow, the steps below are the procedure.

## 2. Branch and edit tasks

1. Create the work item's own branch; never commit to the base branch. With the `spec` bundle, use the branch the
   overall-refactor workflow's Git policy allows.
2. Split the work item into edit tasks. When useful and the host supports subagents, use general subagents for
   parallel edits across many files, drafting and research; otherwise do the same steps yourself.

## 3. Subagent edits

- Give each editing subagent the agreed edits and an explicit write scope: a subset of the batch's write scope,
  disjoint from every other subagent working at the same time.
- Run parallel editing subagents on the same change only. Apply, verify and commit changes one after another, each on
  the previous checkpoint.
- Check each result against the diff before relying on it: the diff stays inside the assigned paths and matches the
  agreed change.
- Revert a rejected edit hunk by hunk; never reset a path another scope owns. Then redo the change or return it to
  the decision round.
- Subagents never commit, ask the user, approve a change or write the run's records.

## 4. Commits and verification

1. Run the change's relevant verification before and after it, with only that change applied on the previous
   checkpoint; record both results and the reachability evidence from `criteria.md` §4.
2. Before each commit, confirm the working tree holds only the committed work plus the current change; revert
   anything else, such as files a verification run wrote.
3. Commit the change as a checkpoint: one commit per change, the change record in the commit body.
4. At the work item's final head, run the repository's full verification on a clean tree (for example the full test
   suite, lint, type checks and governance rules).

## 5. Review

Before integration, have the work item's diff reviewed by a fresh reviewer subagent when the host supports it,
otherwise do a self-review and record it as such. Fix its findings before integration. Where the repository's
workflow defines review effort and bounded rounds (with the `spec` bundle, the run's activity effort, at `high` in
bounded rounds), follow them.

## 6. Report

Put the work item's report in the final response and the commit body: what changed and why, every breaking change
(each compatibility-policy removal with the inputs it no longer accepts), the verification results and anything left
for follow-up.

## 7. Integration

Integrate only after the report, through the repository's integration path and its own integration approval; without
a repository policy, the user's explicit approval. The decision round never supplies it. With the `spec` bundle, use
the session integration path with task kind `overall-refactor`; a single-module work item uses its feature
workflow's path.

## 8. Contract removals

- The decision round may approve removing a command, option, public interface or compatibility path.
- Route each approved removal as its own work item through the repository's normal development workflow, classified
  by its own criteria, with the contract and documentation updated. Keep it apart from the batch's
  behavior-preserving work item and never route it as a refactor.
- Exception: a compatibility path covered by the declared compatibility policy (no external consumer for that
  package) is a behavior-preserving removal in the batch's work item; its change record still names the inputs no
  longer accepted.
