# Manual procedure verification

Executed against the weekly-report playbook on 2026-10-21. These are controlled exercises, not a report of real
external delivery or publication. No generic runtime harness was added. Python standard-library calculations,
exclusive file creation, local readback, SHA-256 comparison and git cat-file checked the concrete artifacts.

| Scenario | Actual observation and disposition |
| --- | --- |
| AC-02 interval and DST | America/New_York March 2 to March 9, 2026: -05:00 to -04:00, 167 elapsed hours. Start included, end excluded by comparisons. Unknown timezone branch requires input before generation. |
| AC-03 bounded evidence | fixture-1-report.md cites real committed spec and ADR at 2711ff71b904753dc8b4d34a57dca0a51ca6f395; git cat-file resolved both. Unchecked tasks/no verification record correctly yields no delivered-work claim. A reachable commit alone and unknown integration time remain qualified. |
| AC-04 health/prior | Missing hygiene, simulated stale drift and failed review remain distinct; no clean or resolved claim. Absent prior and different-scope prior remain non-comparable. Existing feedback linked unchanged. |
| AC-05 dirty/change | Actual dirty implementation is separated from captured committed requirements. Walked through a changed HEAD and same-path edited diff: affected observations must restart or become unverified. Path-list equality alone is insufficient; playbook explicitly compares content/diffs. No fixture source was falsely attributed to history. |
| AC-06 rerun | fixture-2-report.md exclusively created, names superseded fixture-1, retains same logical key and different run. First report digest remains bc74df264e3698de052c05455ffb49dd616b7f8f0ba9b46eefd809fe3464f33b. Both artifacts read back. |
| AC-07 pending | Without authority/destination no send occurred; companion record retains pending attempt. |
| AC-07 confirmed failure | Simulated denied destination recorded failed with generation completed, then simulated lost response recorded unknown. This is a procedure branch exercise, not a real tool failure. |
| AC-07 verified receipt/retry | Local fixture receipt copied exact immutable report; SHA-256 matches. Inspection resolves unknown to published without a duplicate send, retaining run and digest. No external publication. |
| AC-06 failure branches | Walked through missing identity, invalid interval, write/readback failure: generation failed; optional unavailable citations are explicitly unverified and do not falsify success. |
| AC-07 collision/unknown | Walked through mismatching destination bytes and unverifiable destination: collision requires explicit replacement authority; unknown stays unknown and requests disposition. No blind retry or content mutation. |

Limitations: publication failures, changing revision, unavailable identity and collision branches are manual
step-throughs, not injected connector failures. Controlled publication verifies local bytes only. No model
adherence guarantee, real external account, remote freshness, release, scheduler or durable-history test is claimed.
