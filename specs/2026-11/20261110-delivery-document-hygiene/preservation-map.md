# Contract preservation map

Baseline: `cf1c4fd4767131c2194bfccea618dc722f49108d`.

| Baseline owner and section | Retained owner and section | Permitted textual adjustment |
| --- | --- | --- |
| CAP-DLV-delivery-workflows §1–3, §4.1–4.5, §4.7–4.8, source feedback, shared docs and adaptive applicability | Same ID and sections | Scope/summary now names the split owner; existing core rules retained |
| CAP-DLV-delivery-workflows §4.6, §4.6.1, §4.6.2 | CAP-DLV-delivery-roles §4.1, §4.1.1, §4.1.2 | Heading labels and explicit external rule-15 owner only |
| CAP-DLV-delivery-workflows Worker result inspection | CAP-DLV-delivery-roles §4.2 | Heading label only |
| CAP-DLV-proposal-planning §1–3 and §4.1–4.4, milestone closure | Same ID and sections | Scope/summary and explicit handoff-step owner references only |
| CAP-DLV-proposal-planning §4.5–4.12 | CAP-DLV-proposal-lifecycle §4.1–4.8 | Section labels, references to those labels and explicit original policy-rule owner only |
| CAP-DLV-proposal-planning Host-authorized lifecycle CLI, review briefings and approach precondition | CAP-DLV-proposal-lifecycle, same named sections | Existing local section labels adjusted |
| distribution reference configuration sample | Same reference, compact sample plus canonical configuration link | Duplicate engine/search settings sample omitted; unique extension-warning prose and notice/error tables retained |
| UC-drive-development-to-integration second Scenario 32 | Same UC Scenario 33 | Number only; no scenario body removed |

`relocated-sections.json` records source and expected destination normalized SHA-256 values for all three moved
blocks. Expected destination text is source text with exactly the listed mechanical heading/reference adjustments.
Independent review compares those blocks and also checks non-moved policy, practical examples and diagnostics.
Original capability IDs and portal headings remain; completed specs/materials and aliases are unchanged.

## Reference budget judgment

The reference is 414 lines after removing the duplicated engine/search configuration sample. Its notice/error
indexes and source-snapshot public API subset are unique details that the canonical capabilities delegate to this
reference. Retain those facts instead of deleting 14 lines to pass an advisory threshold. The Host explicitly
confirmed this interpretation; no line-budget override is introduced.

Mechanical comparison: PASS all three expected destination blocks equal the relocated baseline blocks after only
these heading, section-reference and policy-rule-owner substitutions; whitespace is normalized for hashing.
