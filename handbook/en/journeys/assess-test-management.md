---
sources:
  CAP-DLV-test-management: 016f55406ad61d18873316b926cae25ce9e3150a
  UC-assess-test-management: 8b04808f607ef438ef6d97400983304dcc3b0429
title: Assess a selected test suite
---

# Assess a selected test suite

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.6` at source commit `93e3808721b4`, generated 2026-11-13. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

Use the explicitly invoked `maintenance/test-management` playbook to decide whether a selected suite needs a different arrangement. Select `maintenance:testing` or `maintenance:all` and sync first.

1. Name the test roots and the question you want answered. The agent reads code, fixtures, scripts and CI before asking for missing preferences.
2. Establish required commands, collection prerequisites, resource isolation and measured cost. Unknown resource safety leaves the affected command unexecuted.
3. Compare coverage, latency and failure-detection tradeoffs. Independent execution needs actual independently runnable groups; directory names alone establish none.
4. Review the concrete recommendation and candidate changes in one decision round. Keeping the current setup is a valid recommendation.
5. Route decided changes through the repository workflow and report remaining checks and collection actions.

Invocation authorizes assessment. It does not authorize configuration edits. A launched run, an ancestor result or successful cleanup proves no required test pass. Pending evidence retains its exact revision, command and next collection action.

## Sources

- [UC-assess-test-management](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-assess-test-management.md)
- [CAP-DLV-test-management](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-test-management.md)
