# UI/UX improvement rename and Impeccable delegation: Planning evidence

## 1. Identity and Boundary

- Planning base: `f810077abd5583303b18105c690b95ca4ac73a3b` on `plan-uiux-improve-ooux-impeccable`.
- Inspected on: 2026-11-10.
- Scope: references to the current bundle in this repository, the release tag `v0.1.5` and the public
  `pbakaus/impeccable` repository. No consumer project, Impeccable installation or host session was run.

## 2. Rename references

Search: `rg --hidden 'uiux[-_]improve|UC-improve-an-interface|CAP-DLV-uiux|ADR-uiux-improvement'` over the worktree,
excluding `.git` and this proposal.

| Path | Reference | Rename action |
| :--- | :--- | :--- |
| `packages/devkit-catalog/src/devkit_catalog/uiux_improve/` | module, `bundle.toml` `name` and asset `id`/`source`, skill directory and `SKILL.md` `name` | move to the qualified module and skill directory |
| `packages/devkit-catalog/pyproject.toml:17` | entry point `uiux-improve = "devkit_catalog.uiux_improve"` | rename key and module |
| `.devkit/architecture.toml:195` | `devkit_catalog` `data_roots` entry `uiux_improve` | rename data root |
| `packages/devkit-catalog/README.md:11,65-70` | bundle table row and the UI/UX improvement section | rename and describe OOUX framing and optional delegation |
| `guides/install/bundle-recommendations.md:37` | recommendation row and `uv run devkit add uiux-improve` | rename and keep the recommendation condition |
| `docs/architecture/ARCH-05-2-components.md:87-89` | bundle name and `devkit_catalog/uiux_improve/bundle/` | rename |
| `docs/capabilities/delivery/CAP-DLV-uiux-improvement.md` | entrypoint path, rule 1 preset, rule 13 test path, section 4 commands and registration | rename and restate the new rules |
| `docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md` | entrypoint path | rename and add extensions |
| `docs/decisions/2026-11/20261105-uiux-improvement-workflow-boundary.md:34` | bundle name in Decision Outcome clause 1 | reference repair; the handoff adds the partial-supersession line |
| `packages/devkit-catalog/tests/integration/bundles/test_uiux_improve.py` | bundle, skill and preset paths | move to the qualified test module |
| `packages/devkit-catalog/tests/e2e/bundles/uiux_improve/` | installed-consumer test | move to the qualified test directory |
| `docs/capabilities/delivery/CAP-DLV-design-exploration.md:29` | cites `CAP-DLV-uiux-improvement` by ID only | none while the capability ID is kept |
| `specs/2026-11/20261105-ux-design-exploration/` | completed spec history | none: completed specs stay as history |

- The release tag `v0.1.5` contains no path or `pyproject.toml` entry matching `uiux`
  (`git ls-tree -r --name-only v0.1.5`, `git show v0.1.5:packages/devkit-catalog/pyproject.toml`).
- The plan-intent decision records that no other workbench repository consumes `uiux-improve`.
- No other tracked file names the bundle, module or skill.

## 3. Upstream Impeccable facts

A Planning scout read the public repository at `main` =
[`a49e3e9be2daccdf96ccf1a081b73d7dd9f456fe`](https://github.com/pbakaus/impeccable/tree/a49e3e9be2daccdf96ccf1a081b73d7dd9f456fe)
(plugin version 4.8.2) on 2026-11-10. Paths below are relative to that commit. The documentation site was not read.

| Topic | Upstream evidence | Planning consequence |
| :--- | :--- | :--- |
| Install routes | `README.md` "Installation": `npx impeccable install` at the project root (asks project or global scope and offers the design hook); Claude Code: `/plugin marketplace add pbakaus/impeccable`, then install Impeccable from `/plugin`; "Manual copy, no Node required" copies `skills/impeccable` into the host's skill directory and skips the hook and subagents. `npx skills add` is not documented. | The skill names these three routes and installs nothing itself. |
| Runtime | `README.md`: Node is needed only for `npx`; the skill runs a self-contained engine binary. | devkit gains no Node or npm dependency. |
| Invocation | One skill, `impeccable` (`.agents/skills/impeccable/SKILL.md`), with 24 commands: `shape`, `init` (alias `teach`), `document`, `extract`, `critique`, `audit`, `polish`, `bolder`, `quieter`, `distill`, `harden`, `onboard`, `animate`, `colorize`, `typeset`, `layout`, `delight`, `overdrive`, `clarify`, `adapt`, `optimize`, `live`, `generate`, and `craft` (deprecated alias of ordinary new work). | The brief names commands by these identifiers; devkit copies none of their text. |
| Commands that report | `audit`: "Don't fix issues; document them" (`reference/audit.md:1`). `critique` reports and stores a snapshot under `.impeccable/critique/` and "MUST run as two isolated sub-agents", declaring degraded output otherwise (`reference/critique.md:8,35-42`). | A critique inside a delegated child needs nested children; the session reports degraded coverage when they are unavailable. |
| Commands that edit | `polish` edits UI as refinement (`reference/polish.md:3`); ordinary new work (`craft`) builds or changes UI. | Edits follow the brief's edit list. |
| Context writers | `init` writes `PRODUCT.md` and `.impeccable/config.json` (`reference/init.md:56-58,100,114`); `document` writes `DESIGN.md` and `.impeccable/design.json` and does not silently overwrite (`reference/document.md:71,251-255`). | These files are consumer-owned project context. |
| `shape` | A discovery interview in rounds of two or three questions, waiting for answers between rounds, then a seven-part brief presented for explicit confirmation; "shape never writes code or a direction contract" (`reference/shape.md:9-58`). The brief stays in conversation; no input format for an existing brief is documented. | `shape` needs the user in the loop. A fresh child cannot run it; the coordinator's framing takes its structural role there. |
| Project files and Git | `README.md` "Project files and git": "Shared artifacts stay tracked: config.json, live/config.json, design.json, surfaces/*.md, critique/*.md. Keep PRODUCT.md and DESIGN.md in the repo too. The rest is screenshots, caches, and runtime state." Its gitignore block lists `config.local.json`, `hook.cache.json`, `hook.pending.json`, `*.png`, `review/`, `questions/`, `live/server.json`, `live/sessions/`, `previews/`, `annotations/`, `cache/` and `manual-edit-*`. `reference/init.md:124` commits `.impeccable/critique/ignore.md` but not `critique/*.md`. | Upstream's own guidance differs on critique snapshots; the skill points to upstream guidance instead of restating a list. |
| `.gitignore` edits | The README tells users to copy the block. No `.gitignore` write was found in the inspected installer sources (not exhaustive). | The coordinator leaves `.gitignore` to the user's direction. |
| Detector and hooks | `npx impeccable detect <dir\|url>` runs 62 deterministic rules, exit 2 on findings. Hooks run after edits (Claude Code `PostToolUse` on `Edit\|Write` and `Stop`, written to `.claude/settings.local.json` for a project install; Codex needs approval at `/hooks`). | A user-installed hook can also react to the coordinator's own edits; the skill installs no hook. |
| Live mode | `README.md` "Live mode": apply runs `codex` or `claude` with sandbox and approvals off. | The brief excludes `live`, because it bypasses the consumer's approvals. |
| Scope guidance | `reference/init.md:7`: confirm shared versus app-specific scope before writing; `SKILL.md`: "Never repair drift as a side effect of a design task." No guidance on running Impeccable in a separate session beyond the critique sub-agents. | The edit list and stop condition come from the coordinator's brief. |
| License | Apache-2.0 (`LICENSE`); `NOTICE.md` credits MIT-licensed platform references. | Nothing is copied; attribution applies only if later work copies text. |
