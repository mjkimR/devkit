---
id: PADR-response-style-guidance-budget
title: Retain the guidance budget until placement evidence exists
summary: "Keeps the 300-byte fragment contract and one response style until actual host evidence warrants a separately reviewed placement change."
proposal: PROP-response-style-survey
status: draft
created_at: 2026-10-20
---

# [PADR-response-style-guidance-budget] Retain the guidance budget until placement evidence exists

## 1. Context & Problem Statement

`CAP-DIST-manifest-spec` limits each guidance fragment to 300 UTF-8 bytes. The current response-style pointer is
shorter than that cap. A statement that a once-read skill fades in a long session is a hypothesis, not an observed
reload or compaction failure. More always-loaded text affects every bundle sharing the distribution contract.

## 2. Decision Drivers

Keep portable asset behavior and a bounded prompt budget. Change a shared contract only when the missing
always-loaded information causes a measured failure before ordinary skill discovery can address it.

## 3. Considered Options

| Option | Benefit | Cost or risk |
| --- | --- | --- |
| Keep one <=300-byte pointer and the discoverable skill | Existing supported contract; smallest change | Does not assume complete long-session retention. |
| Raise the limit for all bundles | Simple validator change | Unmeasured aggregate context growth. |
| Add a per-bundle exception | Limits the immediate relaxation | New manifest policy and exception maintenance. |
| Split one instruction across fragments | Existing syntax may allow more text | Evades the intended budget without evidence. |

## 4. Decision Outcome

Retain the 300-byte contract and one response style with the existing language variable. Do not implement presets,
new variables, per-host variants, manifest exceptions or fragment splitting. A candidate may improve the pointer
within the current limit. `MAT-response-style-measurement-design` bounds an optional synthetic reminder diagnostic
at 16 extra generations; its result cannot prove compaction behavior or justify changing the shared limit alone.
An actual limit expansion needs observed host behavior, an aggregate guidance budget and a new accepted design.

The current scope settles the question as retain-limit; it promises no unimplemented distribution change and
claims no measured long-session effect. The canonical bundle contract reflection goes in
`CAP-DIST-content-packages`; the manifest contract stays unchanged.

## 5. Consequences

Development stays in the response-style bundle, its existing deployment checks and spec-local benchmark materials.
Shorter text cannot remove mandatory workflow fields, tables, numbers or risks. Writing rules describe form;
workflow and user requirements supply required content. A necessary report-schema change would be separate work.
