# spec-specify reference: bugfix characterization and evidence

The expected behavior was agreed at `plan-intent`; characterization is Development work under the shared contracts of
`SKILL.md` §4. `devkit workflow show sdd-spec-bugfix` holds the Red/Green and alternative-evidence rules.

## Stage `characterize`

Fill the skeleton's `Defect Characterization` items; write no user story.

- **Current behavior**: trigger, environment, observed wrong result, with evidence (log, failing command, test).
- **Expected behavior and its basis**: the result the contract requires, citing its capability, use case, ADR or test by
  ID. If it cannot be kept (disputed, or a design decision rather than a defect), raise a problem for the Host.
- **Behavior to preserve**: neighboring paths and contracts that must keep working, their existing tests and the gap.
- **Reproduction conditions**: the exact command, data and environment, or the observation conditions when automation
  is impossible.
- **Acceptance criteria**: one `[AC-NN]` scenario for the resolved behavior and one per preserved behavior.
- **Screens**: when the fix changes a screen, draft it per `SKILL.md` §4; the optional UX review runs inside
  `characterize`, before `plan-tasks`.

## Stage `reproduce`

Write a test that fails on the characterized defect before any fix and keep it as the regression test. Then:

```bash
devkit workflow envelope new --unit <dir> --kind red --stage reproduce \
  --summary "<defect reproduced as characterized>" \
  --check reproduced="PASS <test or command> fails as characterized" \
  --base <ref> --head $(git rev-parse HEAD)
```

- If the failure is not the characterized one, record `--check reproduced="FAIL ..."` and run
  `devkit workflow return --unit <dir> --to characterize`.
- If the reproduction ran on uncommitted work, omit `--head` and say so with `--assume`.

## Stage `fix-verify`

Fix within the task's `_Boundary:`, then verify resolution under the same conditions and preservation over the
declared paths:

```bash
devkit workflow envelope new --unit <dir> --kind green --stage fix-verify \
  --summary "<resolved and preserved>" \
  --check resolved="PASS <same conditions now give the expected result>" \
  --check preserved="PASS <preserved behaviors and the tests run>" \
  --base <ref> --head $(git rev-parse HEAD)
```

- Without automated evidence, state the remaining uncertainty with `--unverified "<what remains unconfirmed>"`.
- If the fix needs a contract change or a design choice outside the agreed intent, raise a problem for the Host and
  state whether the reproduction evidence still holds.
