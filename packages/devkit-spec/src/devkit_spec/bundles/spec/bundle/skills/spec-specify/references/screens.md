# spec-specify reference: screens

Read from `SKILL.md` §4 when the change adds or changes what a person sees and operates.

- **Screens**: when the change adds or changes what a person sees and operates, add a `Screens` section to `spec.md`
  with one draft per screen, modal or panel in the `ux` template's shape (`ux-writing`), with the use case step
  citations and root `docs/steering/ux-objects.md` or namespace `docs/packages/<name>/steering/ux-objects.md` rows
  they need; read both registers for namespace UX. A bundle handed off from a proposal: carry the Screens drafts of
  `target-docs.md` here, so `spec-sync` and the reconcile verification read one place. An open screen arrangement:
  take the recommended candidate and record the others as an assumption.
- When `spec.md` has a Screens section, offer the optional UX review before the plan: delegate the `ux-reviewer`
  (`spec-ux-review`, recommended at `medium` and `high`) on the drafts and fold its findings into `spec.md` before
  `spec-plan` (feature) or `plan-tasks` (bugfix), recording its `ux-review` envelope at this stage.

## Feature specify commit sequence

For `sdd-spec-feature` at `specify`, keep the draft and its review evidence together:

1. Write the uncommitted Screens section of `spec.md`; leave `plan.md` and `tasks.md` uncommitted while drafting.
2. If the optional review is accepted, give the reviewer the last committed HEAD and the uncommitted drafts;
   record that HEAD with an assumption naming the uncommitted Screens in its `ux-review` envelope at `specify`.
3. Fold the findings into `spec.md` before running `spec-plan`, then `spec-tasks`.
4. Run `devkit rules check <dir>` after `tasks.md` covers the criteria; fix violations until it passes.
   A skeleton `tasks.md` cannot cover the criteria and is expected to fail `RULE-task-coverage` during drafting.
5. Commit `spec.md`, `plan.md`, `tasks.md` and the associated `ux-review` envelope together with an ordinary
   manual commit; preserve the envelope's reviewed HEAD and assumption. Do not commit the review record alone
   while the reviewed spec remains uncommitted.

At `build-verify`, report even draft-fixed findings in the implementer's closure by `spec-ux-review`.
