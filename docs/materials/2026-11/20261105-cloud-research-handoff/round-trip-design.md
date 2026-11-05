# Cloud request and intake design evidence

Inspected at branch input `b107d208164afafb277a25f9793627561d92364e` on 2026-11-05.

## Existing contracts and implementation

- `CAP-DLV-deep-research` rules 7, 16–23 permit only transient run and coordinator-owned retained material writes,
  define partial resume when the user names the material, and prohibit rewriting complete materials. Its interface
  already stores requested output, question, in-flight state and useful retained notes without a fixed schema.
- `ADR-deliverable-driven-research` keeps roles optional, source reopening selective and follow-up proportionate.
  Extending this with report provenance requires no mandatory full re-search or comparative provider experiment.
- `UC-research-an-idea-and-shape-a-roadmap` steps 4–7 cover assignments, validation and partial retention; its
  extension 2c and Scenario 12 cover the same user-named partial material being resumed.
- `packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/skills/deep-research/references/workspace.md`
  steps 8–11 already select useful evidence and remove required transient-only references before retention.
- `packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/skills/deep-research/references/synthesis.md`
  steps 6–9 retain partial state and leave committing to the user's Git policy.
- `packages/devkit-catalog/tests/integration/bundles/test_deep_research.py` currently enumerates exact reference
  paths and checks reference/body self-containment. Adding a reference requires adjusting the deployed set, not
  only adding prose. Existing retention/authority checks stay intact.
- `packages/devkit-catalog/tests/e2e/bundles/deep_research/test_installed_consumer.py` verifies installation without
  devkit-spec and copied reference availability; the added reference needs equivalent installed coverage.

## Decision comparison

| Option | Request/result association | Durable resume | Cost/boundary |
| --- | --- | --- | --- |
| Existing generic brief only | Left to individual sessions | Existing partial convention, but pending cloud payload unspecified | Minimal text; misses the reusable handoff gap |
| Manual request plus intake | Plain request label/revision and explicit readable report match | Same partial material retains safe request and pending action | Manual user transfer; no runtime/dependency |
| Browser/API adapters | Provider task IDs and adapter-specific polling | Needs durable external execution state | Account, cost, upload and runtime scope beyond this change |

Select the manual round trip. A plain disposition in the material is enough; no registry, validation schema or
provider role is necessary. One optional reference keeps the main skill brief. No guide pointer is added because
`CAP-DLV-deep-research`'s no-suggestion policy still applies.

## Verification and limits

Planning uses inspected local contracts and does not submit to a cloud service, test paid account access, validate
API parity or measure convenience. Provider-neutral readable content is the supported input, so exact UI export
menus and API availability are not acceptance dependencies. The proposal's former API links are not retained as
support for consumer-app access or a runtime commitment.

Development should review the target document's seven examples and run focused distribution/installed checks.
Source text assertions establish distributed instruction boundaries, not successful behavior by every agent or
provider. No new feature edge or production change is made during Planning.
