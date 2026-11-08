# Assignment contract review

Reviewer: Development worker. Source: commit `0257205d`. Method: inspect the installed bundle's source instructions
against these assignments; this is a contract walkthrough, not a live-agent execution.

## Independent deliverables

Input: writer A adds a CSV parser and writer B edits a usage guide; no shared interface. Each assignment has
one owner, dependency `none`, a passing parser test or guide lint respectively, and a handoff of actual paths and source SHA. The delegation
reference requires these fields. No interface identity or ordering is needed. Observation: the two writers can
proceed in isolated worktrees and the Host checks the combined result. Gaps: none in this fixture.

## Disjoint files, shared API

Input: writer A defines `parse_csv(bytes) -> Rows` in `parser.py` and writer B consumes it in `importer.py`. The coordinator assigns A ownership of
the interface and sequences B after agreement; B receives `parse_csv(bytes) -> Rows` at source commit `abc1234`.
If B's base lacks that version, it receives the identified contract or waits. If the interface changes, the Host
reassesses B before accepting the handoff. Observation: file separation alone does not authorize fanout. Completion
is `pytest tests/test_parser.py` for A, `pytest tests/test_importer.py` for B, and each handoff names its paths and SHA. Gaps: no runtime enforcement is claimed.

## Isolation unavailable

Input: the same `parser.py` and `importer.py` assignment has no worktree isolation. The coordinator retains one owner at a
time, resolves the interface first, supplies interface `parse_csv(bytes) -> Rows` at `abc1234` to B and runs both parser and importer tests after B hands off its paths and SHA.
Observation: serial execution keeps the same evidence and handoff without a team or graph file. Gaps: host
availability is not tested by this walkthrough.

## Overlay review

- Architect: identifies deliverables, blocking dependencies, interface ownership and invalidating assumptions.
- Builder: checks interface and failure handling and reports a contract mismatch without editing another owner's API.
- QA tester: reports expected and observed results, reproduction and coverage limits for its assigned flow.
- Reviewer: checks the actual diff, regressions, compatibility and failure handling; hypotheses are labelled.
- All four retain the caller's permissions and lifecycle. No overlay grants new authority.

No unresolved contract gap was found. Packaging and projection tests establish file properties, not model behavior.
