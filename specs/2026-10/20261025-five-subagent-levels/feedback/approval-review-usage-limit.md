---
id: FB-approval-review-usage-limit
title: Preserve explicit recovery evidence for approval-review usage failures
scope: upstream
kind: friction
category: tool-error
target: "exec_command require_escalated automatic approval reviewer"
origin: agent
severity: workaround
recurring: false
status: forwarded
created_at: 2026-10-25
---

# [FB-approval-review-usage-limit] Preserve explicit recovery evidence for approval-review usage failures

## 1. Friction / Question

- **Context**: A Development worker requested a separately reviewed write in its assigned sibling worktree.
- **Expectation**: The approval route reviews the scoped operation or reports that review is unavailable.
- **Actual**: The automatic approval reviewer failed on an account usage limit before executing the operation.
  The response distinguished reviewer unavailability from an unsafe-action determination and prohibited bypass.
- **Workaround**: Preserve the clean worktree and original operation. After the indicated reset, verify current
  time and read-only usage availability, then retry through the same separately reviewed route. That retry passed.
- **Suggestion**: Keep reviewer-unavailable failures distinct from policy denials and expose their reset/retry
  evidence to the Host so a blocked worker can be diagnosed without changing execution routes.

## Diagnostic Details

- **Reproduction**: Observed on one scoped exec_command call with sandbox_permissions=require_escalated.
- **Expected / Actual**: A reviewed mutation was requested; no process was created because review could not run.
- **Versions**: Codex desktop approval-review service version unknown; repository package version 0.1.3.
- **Conditions**: Sibling worktree writes required escalation; the account had reached the reviewer's usage limit.
- **Workarounds Attempted**: No alternate write route was attempted. After the reset time, usage readback reported
  ordinaryUsageAllowed=true, and retrying the original review route succeeded.
- **Related Assets**: Development-worker permission and unavailable-approval procedure; exec_command approval review.

## Evidence

```text
Automatic approval review failed: usage limit.
The action was not executed because automatic approval review could not be completed.
This is a review failure, not a determination that the action is unsafe.
Later read-only availability: ordinaryUsageAllowed=true; reset time had passed.
Same reviewed worktree mutation: executed and committed successfully.
```

## Disposition

Forwarded on the user's decision (2026-10-27). A report for the Codex approval-review service was drafted (keep
reviewer-unavailable failures distinct from policy denials; expose the reset time and availability so the same
reviewed route can be retried) and handed to the user, who reviewed it. The agent did not send it; any submission is
the user's, outside devkit. No repository change is needed.
