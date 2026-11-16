# Classify an interrupted synchronization

**Reader question:** What does TRANSACTION_PENDING mean, and which recovery owner applies when later edits cause RECOVERY_BLOCKED?

This non-normative entry is a symptom-to-owner map. A pending journal, a later-edited file and a legacy journal
need different evidence before choosing the existing recovery authority. Absence of a journal alone says nothing
about remaining desired-state changes.

## Select the owner from the evidence

| Observed symptom or documented state | Evidence that separates it | Next authority to read |
| --- | --- | --- |
| Interrupted sync reports `TRANSACTION_PENDING` | A pending sync journal is reported | `CAP-DIST-sync-and-transactions` §3 item 6, Recovery; the [distribution reference](../../../development/reference/distribution.md#error-codes) maps the code to its advisory action |
| `RECOVERY_BLOCKED` after a subsequent edit | A recorded path no longer matches the journal's before/after evidence | The same capability Recovery item owns the stop condition; the reference's `RecoveryError` row identifies `HALT` |
| `RECOVERY_BLOCKED` with an older journal | The journal lacks `directories` | The same Recovery item and reference row own version-specific/manual recovery selection; follow the actual advisory's `[FIX]` |
| No pending journal, but desired-state changes remain | Desired inventory differs, for example after changing a preset without sync | `CAP-DIST-sync-and-transactions` “Readiness Gate” owns the normal-state decision |

Start with the row matching the reported code and evidence, then read that owner and its actual advisory before
acting. Recovery commands and stop conditions stay in those owners. This map is not an alternative recovery
procedure and does not authorize an agent to resolve later edits itself.

## Normal-state observation

After the owner's recovery decision, next consult `CAP-DIST-sync-and-transactions` “Readiness Gate” for
`uv run devkit sync --check` and interpretation of exit codes. The [distribution reference](../../../development/reference/distribution.md#devkit-status)
also explains why installed-state diagnostics alone are insufficient. The no-journal/drift paper case remains
not ready under that owner; it does not become ready merely because no rollback remains.

## Evidence boundary

These are documented-state classifications, not observed recovery results. The pilot executes no recovery,
creates no journal fixture and changes no capability/advisory action. It adds evidence selection and the path
from symptom to recovery owner and readiness owner without copying their instructions.
