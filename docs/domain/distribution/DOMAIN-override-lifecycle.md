---
id: DOMAIN-override-lifecycle
title: "Project override lifecycle"
status: active
area: distribution
summary: "Relates a project override's files and receipt record to its capability-defined states (recorded, drift, not deployed, retained, asset of another bundle, removed upstream) and separates them from ORPHAN_LEFT files."
related_capabilities: [CAP-DIST-workspace-ownership, CAP-DIST-sync-and-transactions]
related_domains: [DOMAIN-bundle-selection-and-installation]
---

# [DOMAIN-override-lifecycle] Project override lifecycle

Once a project override exists, readers confuse its files with its receipt record, and the states that record
passes through with the `ORPHAN_LEFT` warning: an override of a deselected bundle, an override of an asset removed
upstream and a file `ORPHAN_LEFT` names all stay on disk. The difference lies in what the receipt still records and
in which command or sync moves it. This entry relates those states, using only the names and codes of
`CAP-DIST-workspace-ownership` §3, and names the owner of each. The term itself is defined in the
[glossary](../../steering/glossary.md) ("Project override").

## Relationship overview

An override has two halves. Its files are complete replacements under `.devkit/overrides/<bundle>/`, with baseline
copies under `.devkit/overrides/.baseline/<bundle>/` (`CAP-DIST-workspace-ownership` §1). Its record sits in the receipt
under `overrides.<bundle>.<asset>` and holds the baseline and override digests (`CAP-DIST-workspace-ownership` §3 Drift
Detection; `CAP-DIST-sync-and-transactions` §1). Every state below is a relation between those halves, the
installed bundle and the selection. Each one is changed by a command that synchronizes, or by a sync.

| Concept or relationship | Distinction | Authoritative owner |
| --- | --- | --- |
| Override files and receipt record | The files are project-owned, Git-tracked content. The record is sync's evidence of them and never appears under the receipt's `files`. | `CAP-DIST-workspace-ownership` §1, §3; `CAP-DIST-sync-and-transactions` §1 |
| Recorded | `devkit override create <bundle>:<asset>` copies the files and synchronizes, so the current upstream digest becomes the baseline. `--force` replaces the files and the baseline. A plain `devkit sync` also records override files it finds there for the first time, with the current upstream as the baseline. | `CAP-DIST-workspace-ownership` §3 Creating an Override, Drift Detection |
| Drift (`OVERRIDE_DRIFT`) | For a deployed asset, the digest over every upstream file differs from the baseline. The override stays projected. `override_drift` decides whether sync and `devkit status` warn or block. `devkit override accept` moves the baseline and synchronizes, or under `block` defers the sync (`OVERRIDE_SYNC_DEFERRED`). `devkit override remove` ends the record. | `CAP-DIST-workspace-ownership` §3 Drift Detection, Reconciliation |
| Not deployed | The bundle is deselected or the preset narrowed. The record is kept while override files remain, and no drift is reported. Selecting the asset again with a selection command and its sync deploys the override and reports any drift. | `CAP-DIST-workspace-ownership` §3 Drift Detection; `CAP-DIST-sync-and-transactions` §1, §2 |
| Retained (`OVERRIDE_RETAINED`) | A notice from `devkit remove <bundle>` naming the override directory it leaves. It is not a separate record state: the records follow the not-deployed rule. | `CAP-DIST-workspace-ownership` §3 Drift Detection |
| Override naming another bundle than the asset's | Overrides resolve by bundle name and path. The override does not apply and the asset deploys from upstream. Files and record stay while the files remain. `devkit override create` under the asset's own bundle makes an override that applies. | `CAP-DIST-workspace-ownership` §3 Drift Detection |
| Asset removed or renamed upstream, or bundle not installed | The record is kept while files remain under its own override path. `devkit override list` shows `drift_detected: false` for it, because there is no current upstream digest to compare. `devkit override remove` deletes every file under the recorded path and its baseline, and its sync drops the record. | `CAP-DIST-workspace-ownership` §3 Drift Detection, Reconciliation |
| Record dropped | `devkit override remove` deletes the override files of the asset's upstream files and the baselines, then synchronizes; the record disappears with that sync. A sync that finds no override files left carries no record. | `CAP-DIST-workspace-ownership` §3 Reconciliation |
| `ORPHAN_LEFT` | A warning about a file left on disk, never a state of an override record. Sync reports it for a hand-edited managed file that is no longer desired (dropped from `files`) or an edited guidance block under `guidance_block = false`. `devkit override remove` reports it for other project files under the asset's override paths. | `CAP-DIST-workspace-ownership` §2 items 5–6, §3 Reconciliation |

Reconciliation (`override diff`, then `override accept`) is a command outcome that moves a drifted record's
baseline; it is not a state. A record kept for an asset that is not deployed, retained, under another bundle or
removed upstream is still an override record. An `ORPHAN_LEFT` file has no override record and is not recorded under
the receipt's `files` either.

## Worked example

This nonexecuted example uses the asset `starter:development` from the capability's drift example.

1. `devkit override create starter:development` writes the override and baseline copies and synchronizes; the
   receipt records the asset with the current upstream as its baseline (recorded).
2. A package upgrade changes an upstream file of the asset. The next `devkit sync` reports `OVERRIDE_DRIFT` and keeps
   the override projected (drift).
3. `devkit remove starter` deselects the bundle. Its result carries `OVERRIDE_RETAINED`, and the record stays because
   the override files remain (not deployed). Selecting `starter` again redeploys the override, with the drift still
   reported.
4. `devkit override accept starter:development` records the new baseline and synchronizes; drift is no longer
   reported.
5. The project had also put `notes.md` in that override directory. `devkit override remove starter:development`
   deletes the upstream-file overrides and baselines, and its sync drops the record. `notes.md` stays and is named in
   `ORPHAN_LEFT`. From then on it is a project file with no override record.

## Authority boundary

This entry relates states; it settles none of their rules. Override creation, drift policy, retention and
reconciliation belong to `CAP-DIST-workspace-ownership` §3. File ownership and `ORPHAN_LEFT` belong to
`CAP-DIST-workspace-ownership` §2. The receipt's `overrides` and `files` fields and selection inputs belong to
`CAP-DIST-sync-and-transactions` §1 and §2. Where overridden files are projected belongs to
`CAP-DIST-agent-projections`. How available bundles, selection, assets and receipt evidence relate belongs to
`DOMAIN-bundle-selection-and-installation`. The term belongs to the [glossary](../../steering/glossary.md) entry
"Project override". Advisory codes, fields and fixes are mapped in the
[distribution reference](../../development/reference/distribution.md#error-codes); this entry copies no
`[FIX]` or `[ACTION]`.

## Maintenance and next action

Update this entry when `CAP-DIST-workspace-ownership` §3 adds, renames or removes an override state or code, or
changes which command or sync moves a record. For whether an action is allowed or what it guarantees, read
`CAP-DIST-workspace-ownership` §3. For a code an override command printed, read its row in the distribution
reference. For where an override is projected, read `CAP-DIST-agent-projections`.
