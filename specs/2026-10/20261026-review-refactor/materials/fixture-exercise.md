# Review-refactor fixture exercise (manual evidence)

`SPEC-review-refactor` AC-08. Manual evidence, not test coverage. Decisions are simulated and change only the
fixture: a disposable Git repository at `<worktree>/scratch/rr-fixture` (ignored by `.gitignore:47 /scratch/`,
never committed to the worktree). The worker's removal of the fixture was denied by the host's permission system, so
it remains at that ignored path for the Host to delete; nothing of it is tracked. Its `git init` and commits are fixture operations. No
real workflow, review or integration was opened. Patches: `fixture-patches.txt` (`git format-patch main..HEAD`).

## 1. Fixture and intake

| Field | Value |
| --- | --- |
| Run ID | rr-20261026-fixture-01 |
| Layout | `app/features/{orders,invoices}/`; package-level `app/utils/` created only when needed; features never import each other (fixture README) |
| Compatibility policy | "no external consumers exist; breaking changes may be made in place without shims or legacy readers" |
| Test command (full verification) | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s <fixture>/tests -t <fixture>` |
| Seed | `f0fb203` on `main`; clean tree; 5 tests OK |
| Surfaces and roots | `code`, root `app/` (one batch); simulated user selection |

## 2. Findings and decision round (simulated)

| Key | Location | Question | Cost | Disposition (simulated decision) |
| --- | --- | --- | --- | --- |
| RR-F1 | `app/features/orders/service.py:10-21` | Duplicated behavior: the line-sum loop in `order_total` and `order_total_with_tax` | A change to line arithmetic must be repeated in both | Consolidate, behavior preserved: approved |
| RR-F2 | `app/features/orders/service.py:4-7`, `app/features/invoices/service.py:4-7` | Repeated technical helper: `format_money` in two features | A formatting fix must be repeated per feature | Fold into a utility, behavior preserved: approved |
| RR-F3 | `app/legacy.py:1-10` | Speculative compatibility: unreached v1 configuration reader | Dead code read and kept type-correct on every change | Remove under the declared compatibility policy: approved |

Route statement given in the round: the work item edits `app/features/orders/service.py`,
`app/features/invoices/service.py`, `app/utils/` (new) and `app/legacy.py`. Single-module test: fails (two
features, a package-level utility module and a package-level module), so the work item routes as a behavior-preserving
refactor across several areas in direct mode. Batch write scope: those paths plus `tests/test_app.py` as following
edits (none were needed). No contract work item: RR-F3 falls under the compatibility-policy exception.

Branch: `refactor/rr-code-batch` from `main` (never committed on `main`).

## 3. Change records

### C1 (RR-F1): consolidate the line-sum loop, applied by the playbook's agent

- Commit `70bb98b`; `order_total_with_tax` now calls `order_total` (patch 1/3: `service.py` +1/-3).
- Deviation: the diff check ran before the verification, which rewrote the tracked
  `app/features/orders/__pycache__/service.cpython-312.pyc`, and `git commit -a` swept it into `70bb98b`. The tree
  was not rechecked between verification and commit, so the commit holds a file outside the change. It is left as
  recorded (fixture history is not rewritten); the playbook text was corrected to require the check before each
  commit (`references/applying.md` §4 step 2), as the agreed design states.
- Reachability: `rg -n "order_total|order_total_with_tax"` -> `orders/service.py:10,17,25`,
  `tests/test_app.py:4,9,12`; dynamic reach `rg -n "getattr|importlib|__import__|entry_points|eval\("` -> none; no
  `pyproject.toml` or `setup.cfg` (no entry points).
- Verification before (checkpoint `f0fb203`): `Ran 5 tests ... OK`; after: `Ran 5 tests ... OK`.
- Placement: feature-local; no helper introduced. Characterization test: none needed (`test_total`,
  `test_total_with_tax` exercise both callers).

### C2 (RR-F2): fold `format_money` into `app/utils/money.py`, applied by an editing subagent

- Subagent write scope: `app/utils/__init__.py`, `app/utils/money.py`, `app/features/orders/service.py`,
  `app/features/invoices/service.py`; it ran no state-changing Git command and wrote no record.
- Diff check by the playbook's agent: the `.py` hunks stay inside the scope and match the agreed change (both local
  copies removed, one import each, `money.py` byte-identical to the removed body). Rejected: the test run had
  rewritten two tracked bytecode files (`app/features/{orders,invoices}/__pycache__/service.cpython-312.pyc`, tracked
  by the seed commit) and created an untracked `app/utils/__pycache__/`; these were outside the scope and were
  reverted path by path (`git restore -- <two paths>`, removal of the two untracked files), with no reset of other
  paths. Later runs used `PYTHONDONTWRITEBYTECODE=1`.
- Commit `77b9cb9` (4 files, +6/-10).
- Reachability: `rg -n "format_money"` -> `orders/service.py:4,23`, `invoices/service.py:4,11`; dynamic reach none.
- Verification before (checkpoint `70bb98b`): `OK`; after: `Ran 5 tests ... OK`.
- Placement: package-level `app/utils/` (technical helper), the lowest common owner both features may depend on;
  no new cross-package or foundation module, so no extra decision. Characterization test: none needed
  (`test_summary`, `test_line`, `test_negative_line` exercise both callers).

### C3 (RR-F3): remove the v1 configuration reader, applied by the playbook's agent

- Commit `4d5f673` (`app/legacy.py` deleted, -10 lines).
- Inputs no longer accepted: v1 `key = value` configuration text through `app.legacy.read_v1_config`.
- Reachability: `rg -n "read_v1_config|legacy\b"` -> `app/legacy.py:4` and the README policy line only;
  `rg -n -i "\bv1\b"` -> `app/legacy.py:1`; dynamic reach none; no entry points.
- Verification before (checkpoint `77b9cb9`): `OK`; after: `Ran 5 tests ... OK`.

## 4. Full verification and remaining steps

- Final head `4d5f673f2c67f98346dad91154719fa8258b1319`, clean tree (`git status --short --untracked-files=all`
  empty), full test command verbose: 5 tests `ok`, `OK`.
- Line delta: `git diff --shortstat main HEAD` -> 7 insertions, 23 deletions (net -16 source lines; one bytecode
  file from the C1 deviation); reported, not the justification.
- Not exercised (no real workflow): the independent review, the work-item report and integration; in a real run
  the playbook's agent would start a fresh reviewer subagent, put the report (no breaking change; C3's no-longer-accepted
  input named) in the final response and commit body, and integrate only after its own approval.

## 5. Observation

The verification command itself wrote tracked files (the seed commit tracked bytecode, a fixture setup defect). In
C2 the diff check after the test run caught it and the hunks were reverted; in C1 the check ran before the test run
and the file entered the commit. The playbook draft said "before each change"; the agreed rule is "before each
commit", which would have caught C1. `references/applying.md` §4 step 2 now reads so. No new rule is needed.
