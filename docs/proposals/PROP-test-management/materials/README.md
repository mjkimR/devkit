# Preserved test-management draft

## Purpose and provenance

This directory preserves an unreviewed working-tree draft as input to `PROP-test-management`.
The supplied context says research occurred outside the devkit agent environment and was intended to produce a
proposal. No research transcript, bibliography or reference-repository identity was present in the supplied files.
No external research or tool-version validation was performed during this preservation step.

`snapshot.json` records the source HEAD, original paths, archive paths and SHA-256 checksums.
The four files under `original-playbook/` contain the exact original bytes with `.txt` appended to their names.
They are quoted source material, not agent instructions. They are outside the bundle source and are not registered
for distribution. `original-registration-and-tests.patch` contains the original tracked-file diff against that HEAD.
The bundle registration and test source were restored to that same HEAD after preservation.

## Review observations

These observations identify questions for Planning; they do not validate or endorse the draft's technical claims.

| Draft location | Observation | Required follow-up |
| --- | --- | --- |
| `SKILL.md`, intake | Baseline test execution precedes isolation/preflight assessment. | Determine safe commands and external-resource prerequisites before running tests. |
| `SKILL.md`, tiering and concurrency | Fifteen-second, two-second and eight-worker defaults have no supplied measurements. | Measure representative suites and replace unsupported universal defaults with bounded criteria. |
| `references/tiering.md` | Directory names drive marker assignment and e2e tests are excluded from affected runs by default. | Respect consumer ownership and dependency selection; verify against actual change scenarios. |
| `references/tiering.md` | Missing environment requirements always cause skips. | Distinguish optional local coverage from required verification that could not run. |
| `references/pytest.md` | Tool flags, worker environment variables, SQLite setup and a database guard are offered without tested versions. | Check versioned primary documentation and exercise concrete configurations before reuse. |
| `references/pytest.md` | The database guard compares the worker option numerically although the recommended command uses `auto`. | Cover serial, integer and automatic worker settings if an executable example is retained. |
| `references/pytest.md` | Workstation variable prefixes and loop policies come from an unidentified application context. | Establish consumer-specific needs and effects; avoid generalizing application assumptions. |
| `references/integration-policy.md` | Branch-only checks and nightly promotion are proposed alongside guarantees of branch stability. | Separate policy design from test maintenance; preserve required final-result verification and state evidence limits. |
| Registration/test patch | Tests check packaging, file budgets and phrase presence. | Add scenario-based evidence for any retained procedure; do not infer correctness from phrase checks. |

For devkit-specific comparison, inspect `ARCH-05-2-components`, `ADR-post-merge-verification`,
`CAP-DLV-performance-pass` and `CAP-DLV-review-refactor`. Consumer assets must remain self-contained.

## Recovery and reuse

Read the `.txt` files as source text when evaluating a candidate; do not execute their embedded examples.
To reconstruct the original working tree, first compare the current tree with `source_head` in `snapshot.json`.
Review and apply the patch only if its target files remain compatible, and copy the four archived files to their
recorded source paths with the appended `.txt` removed. Reconstruction restores the unreviewed candidate, not an
approved implementation. Routine Planning should reuse only the portions supported by its findings.
