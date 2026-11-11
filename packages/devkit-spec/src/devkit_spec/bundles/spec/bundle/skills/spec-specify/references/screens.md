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
