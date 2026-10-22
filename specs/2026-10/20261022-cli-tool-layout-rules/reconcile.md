---
reconcile_id: REC-cli-tool-layout-rules
feature: SPEC-cli-tool-layout-rules
status: resolved
targets:
  - file: docs/capabilities/cli/CAP-CLI-agent-cli-toolkit.md
    resolution: modified
---

# Reconcile: `SPEC-cli-tool-layout-rules`

`CAP-CLI-agent-cli-toolkit` is the contract of the `cli-tool` bundle. Its summary and scope name five rules, rule 11
the five rules of the default preset (AC-08), and the new rules 16 to 19 state what `RULE-cli-tool-layout` (AC-01,
AC-02) and `RULE-cli-tool-layers` (AC-03 to AC-07) enforce, including the documented gaps (imports of a feature
package, `if TYPE_CHECKING:`). The interface section lists the two assets and the layout rule's settings. Its
entrypoint `packages/devkit-catalog/src/devkit_catalog/cli_tool/` already covers the new rules.

No other Living Spec document changes:

- `docs/architecture/`: the bundle is content of `devkit-catalog`; no container, component or output contract
  changes.
- `CAP-GOV-rule-authoring`: the two rules use the plugin-package contract unchanged, one directory per rule.
- `CAP-DIST-content-packages`: the catalog's opt-in contract is unchanged; the bundle only gains assets.
- No story, ADR or glossary term changes.

Repository guides kept in step (not Living Spec): the `cli-tool-structure` instruction (required feature layout, the
two rules), the catalog README row and the `cli-tool` row of `guides/install/bundle-recommendations.md`; the consumer
smoke expects the five rules.
