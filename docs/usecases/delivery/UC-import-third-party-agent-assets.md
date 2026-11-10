---
id: UC-import-third-party-agent-assets
title: Import selected third-party agent assets as project-owned assets
summary: "An AI coding agent explores a third-party repository of subagents or skills, recommends the few that fit the project, and converts the developer's selection into project-owned role overlays, role contracts or skills for the swarm archetypes without executing or vendoring the source."
area: delivery
primary_actor: AI coding agent
supporting_actors: [Developer, Reusable execution agents]
status: active
capabilities:
  - CAP-DLV-adaptive-development
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/adaptive_dev/bundle/skills/adaptive-import/SKILL.md
  - packages/devkit-catalog/src/devkit_catalog/adaptive_dev/bundle/playbooks/agent-asset-conversion/SKILL.md
created_at: 2026-11-10
---

# [UC-import-third-party-agent-assets] Import selected third-party agent assets as project-owned assets

## 1. Goal

- **Goal**: add the specialist checks of a few fitting third-party subagents or skills to the project's delegated work, so that the project owns, validates and can trace each one instead of installing a pack.
- **Scope**: the `adaptive-import` entry and the `agent-asset-conversion` playbook of the opt-in `adaptive-dev` bundle.
- **Trigger**: the developer explicitly invokes the import entry with a Git repository URL or a local path.
- **Preconditions**: the entry and its playbook are selected (`adaptive-dev:core` or `adaptive-dev:import`); the agent can read the project.

## 2. Main Success Scenario

1. The developer invokes the import entry with a source and optional conditions (`CAP-DLV-adaptive-development`).
2. The agent acquires the source outside the project tree as untrusted data and records its URL, commit and license (`CAP-DLV-adaptive-development`).
3. The agent inventories the candidate subagents and skills from their headers (`CAP-DLV-adaptive-development`).
4. The agent profiles the project's stack, current product state and available roles and combines the profile with the stated conditions (`CAP-DLV-adaptive-development`).
5. The agent reads the shortlisted bodies and recommends the few fitting items with their target form, archetype, conversion notes and the notable exclusions (`CAP-DLV-adaptive-development`).
6. The developer selects items, which invokes the conversion procedure for them (`CAP-DLV-adaptive-development`, `CAP-DIST-context-and-playbooks`).
7. The agent rewrites each selected item into its target form without the source's authority, model and host-specific content and places it in the project's own bundle (`CAP-DLV-adaptive-development`, `CAP-DIST-in-repo-bundles`).
8. The agent validates and synchronizes the bundle and runs one bounded trial assignment through the mapped archetype (`CAP-DLV-adaptive-development`).
9. The agent reports per item the source identity, target, validation outcomes, limitations and next action (`CAP-DLV-adaptive-development`).

## 3. Extensions

- **1a.** No source is given: the agent asks for it and asks nothing else; resumes at step 2 when it is supplied.
- **1b.** The developer invokes the conversion playbook directly for one known file: the agent pins that file's identity; resumes at step 7.
- **2a.** The clone fails or needs credentials: the agent reports the Git error, handles no credential and asks for a local checkout path; resumes at step 2 with that path or the use case ends.
- **2b.** The source is a local path: the agent reads it in place and records its commit, or states that it has no commit identity; resumes at step 3.
- **2c.** Source text addresses the reading agent: the agent records it as a finding about that item and does not follow it; resumes at step 3.
- **4a.** No condition is stated and no current context exists: the agent profiles from manifests, run instructions and available roles alone; resumes at step 5.
- **5a.** Nothing fits: the agent says so with the reasons; the use case ends with no project file changed.
- **6a.** The developer selects nothing or asks for the whole pack: the agent writes nothing and keeps the recommendation open for a selection; resumes at step 6 or the use case ends.
- **6b.** Playbook retrieval fails: the agent reports the retrieval code, such as `SELECTION_INVALID`, and converts nothing; the use case ends.
- **7a.** The item needs independent selection or role-specific host settings, or is a procedure the Host itself runs: the agent writes a host-neutral role contract or a skill instead of an overlay; resumes at step 8.
- **7b.** The developer asks for the unchanged original: the agent states the native-variant limits, including `ASSET_UNPROJECTED` on other hosts, and copies only on the developer's decision; resumes at step 8.
- **7c.** The item's signals conflict: the agent maps the narrower archetype, states the choice and returns the excluded instruction to the caller as a report; resumes at step 7.
- **7d.** The item depends on an MCP server or a companion command, skill or hook: the agent lists it as an unmet prerequisite and configures nothing; an item that does nothing useful without it is reported `needs_input`; resumes at step 8 for the remaining items.
- **7e.** Verbatim text has an unknown license or one that does not permit redistribution: the agent stops for the developer's decision; resumes at step 7 with a rewrite or drops the item.
- **7f.** The project has no bundle of its own: the agent creates the minimal in-repository bundle, installs it as a development dependency and selects it; resumes at step 7.
- **8a.** Validation or sync reports a defect such as `BUNDLE_INVALID`: the agent fixes the bundle source and repeats the commands; resumes at step 8.
- **8b.** The host cannot run the archetype: the agent reports the trial as unverified with the reason; proceeds to step 9.

## 4. Postconditions

- **Success guarantee**: each selected item is a project-owned asset in the project's bundle that ends with or records its provenance, the bundle validates and is synchronized, its constitution lists the converted role, and the report states each validation and trial outcome or its unverified gap.
- **Minimal guarantee**: nothing from the source was executed, installed or followed; no unselected item, pack copy or submodule entered the project; no development approach or host setting changed; without a selection no project file changed.

## 5. Acceptance Criteria (Given / When / Then)

Rules: explicit import entry; approach independence; untrusted source; header inventory; fit recommendation; one
selection round; target form; archetype mapping; removed authority; provenance and license; project-owned placement;
validation and trial.

### Scenario 1: Import one selected reviewer as a role overlay

- **Covers**: main success scenario
- **Given**: an SDD project that selects `adaptive-dev:agents` and `adaptive-dev:import`, its own bundle, and a pack with a database reviewer persona that fits a stated role gap.
- **When**: the developer invokes the entry with the pack's URL and selects the recommended reviewer.
- **Then**: the bundle gains one `document` overlay naming `swarm-verifier` with a provenance line, `uv run devkit bundle validate` and `uv run devkit sync` exit `0`, the overlay exists under `.devkit/managed/<bundle>/roles/`, no host directory holds an agent of that ID, and the effective approach is still `sdd`.

### Scenario 2: End without changes when nothing fits or nothing is selected

- **Covers**: 5a, 6a
- **Given**: a pack whose candidates duplicate the project's roles, or a recommendation the developer answers with a request for the whole pack.
- **When**: the agent finishes the recommendation.
- **Then**: it states that nothing fits, or keeps the selection open, and `git status --short` shows no change.

### Scenario 3: Keep the source inert

- **Covers**: 2a, 2b, 2c
- **Given**: a source whose README tells agents to run an installer, a private repository the clone cannot read, or a local checkout path.
- **When**: the agent acquires and inventories the source.
- **Then**: no script runs, the instruction is reported as a finding, a failed clone ends with its Git error and a request for a local path, a local path is read in place with its commit recorded, and the project holds no clone or submodule.

### Scenario 4: Ask only for a missing source and profile without conditions

- **Covers**: 1a, 4a
- **Given**: an invocation without a source, then a source without conditions in a project with no current-context file.
- **When**: the agent starts.
- **Then**: it asks for the source alone, then builds the profile from manifests, run instructions and available roles before the single selection round.

### Scenario 5: Choose another target form on its condition

- **Covers**: 7a, 7b, 7e
- **Given**: a selected skill whose procedure the Host runs, and a request to keep one Claude Code agent unchanged.
- **When**: the agent converts the two items.
- **Then**: the first becomes a `skill` asset with its invocation declared in the manifest; for the second the agent first states the native-variant limits and the license condition, and copies it only after the developer decides.

### Scenario 6: Narrow authority and report dependencies

- **Covers**: 7c, 7d
- **Given**: a selected agent labelled as a reviewer whose body also pushes fixes and calls an MCP server.
- **When**: the agent rewrites it.
- **Then**: the overlay names `swarm-verifier`, returns fixes and the push to the caller, carries no model or tool name, and the report lists the MCP server as an unmet prerequisite that was not configured.

### Scenario 7: Create the project's bundle when none exists

- **Covers**: 7f
- **Given**: a project with a `pyproject.toml` and no package declaring a `devkit.bundles` entry point.
- **When**: the first selected item is placed.
- **Then**: a minimal package under `tools/` holds the bundle, it is a development dependency, `uv run devkit get-context <bundle>` returns a constitution listing the role, and `uv run devkit status` exits `0`.

### Scenario 8: Repair validation and label an unavailable trial

- **Covers**: 8a, 8b
- **Given**: a converted role contract that omits one host block, on a host that cannot run registered agents.
- **When**: the agent validates and attempts the trial.
- **Then**: it fixes the `BUNDLE_INVALID` report and reruns the commands until they exit `0`, and reports the trial as unverified instead of a pass.

### Scenario 9: Convert one known file directly

- **Covers**: 1b, 6b
- **Given**: the developer names one agent file and invokes the conversion playbook by its exact ID.
- **When**: the agent retrieves the playbook.
- **Then**: it converts that file alone with the same pinning, rewrite, placement and validation; a failed retrieval reports its code and converts nothing.
