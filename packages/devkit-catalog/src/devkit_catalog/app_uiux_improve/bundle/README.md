# app-uiux-improve usage guide

For the person who uses the `app-uiux-improve` bundle, before selecting it or to recall the flow. It is not an
agent asset: sync never deploys it and no skill file links it.

## 1. What it is for

`/app-uiux-improve <goal>` improves the interface and user flows of software: web and desktop applications,
dashboards, admin tools, settings and responsive views. The coordinator (the agent you invoke) frames the domain
objects a change touches, improves the screens inline or through an Impeccable session you select, and carries the
changes through an explicitly approved outside-workflow run or your chosen project workflow, with applicable checks.

It does not:

- design slide decks, game loops, 3D graphics or video;
- run Impeccable unless you select it, or install it or clean up its files unless you ask;
- write your glossary, object register or UX documents during the run;
- commit, integrate or publish anything on its own authority;
- require a fixed team of roles, a score or a comparison experiment.

## 2. One-time setup

1. Select the bundle: `uv run devkit add app-uiux-improve`. Selection starts no work and changes no project policy.
2. Optional: install Impeccable through one upstream route. Run it yourself, or ask the coordinator to run a route
   that needs no prompt answers.
   - `npx impeccable install` at the project root (asks for project or global scope and offers a design hook).
   - Claude Code: `/plugin marketplace add pbakaus/impeccable`, then install Impeccable from `/plugin`.
   - Manual copy of upstream `skills/impeccable` into your agent's skill directory (no Node required, no hook).
3. Run Impeccable's `init` through the question relay below when supported, or in a session you operate.
   Confirm every answer and explicitly permit its `PRODUCT.md` creation; choosing the track alone grants no file permission.
4. Add an OOUX reference section to `PRODUCT.md`, in that `init` session or by asking the coordinator. The section
   names your glossary, object register and UX document directory by path and says to read them before structural
   work; it copies none of their content, so it cannot drift:

   ```markdown
   ## Object model

   Before structural UI work, read docs/steering/glossary.md (object names),
   docs/steering/ux-objects.md (representations and actions per role) and the
   UX documents under docs/ux/ for the affected screens.
   ```

## 3. Per-task flow

1. Start: invoke `/app-uiux-improve <goal>` in your session. Before product edits or write-capable delegation, the
   coordinator announces that this procedure runs outside your repository's development workflow and process
   guidelines, and asks for explicit task approval or your choice to follow that workflow. An exact choice already
   supplied is reused; without an answer, dependent edits wait. Review-only work needs no route choice.
2. Framing, in proportion to the request:
   - a local change (one component, one state, copy or spacing) proceeds without framing;
   - a change that adds, merges or reorders views or flows first names the affected objects, their relationships,
     the actions (CTAs) on each object and the attributes each view shows, with empty, loading, error and populated
     states;
   - a review-only request uses the framing as a lens and ends with findings and no product edits.
3. Track: inline is the default. Say "use Impeccable" to select the Impeccable track; the coordinator then writes a
   brief with the goal, the framing, the files Impeccable may edit, a recorded base, the commands and a stop
   condition.
4. Session: Impeccable runs through one of the two launch routes below. The coordinator edits no product files until
   the session returns.
5. Acceptance: the coordinator compares the working tree with the recorded base and both the edit list and approved
   goal scope, verifies the accepted changes,
   reports anything outside the brief and each stale OOUX document, and continues through your selected route.
6. Cleanup, only if you ask.

If you choose your workflow, its pre-implementation steps, required reviews and delivery approvals still apply.
The outside route uses the improvement loop without workflow-specific records. Both retain product constraints,
host permissions, applicable project checks and before/after verification. Independent reviews are optional only
when your selected workflow does not require them. A focus such as color first orders work; only your stated
constraints or explicit deferrals become non-goals. The brief states that authorized brief/specification content
controls Impeccable craft defaults and returns conflicts between authorized sources for a decision.

Verification uses the changed local branch build before and after with the same representative task and data. A
deployed environment is at most a baseline. When a live backend is costly or shared, use repeatable mocks and retain
a re-runnable capture method; report mocked coverage as mocked, not an end-to-end check, and name missing live
coverage. Color work reports computed contrast ratios for key pairs/states using effective composited colors.

If your selected workflow drafts new screens before code (for example in a planning document), the screen is drafted there
first and Impeccable implements and refines that draft.

Example request:

```text
/app-uiux-improve Merge the Customers and Invoices pages so overdue invoices can be chased from the customer view. Use Impeccable to polish the result.
```

The coordinator frames Customer and Invoice from your glossary and object register, implements the merged view
through your selected route, then briefs a fresh child to run `polish` and `audit` on the two changed files.

## 4. Launch routes

| Commands | Route | What you do |
| --- | --- | --- |
| `polish`, `audit` and narrow refinement commands (`distill`, `typeset`, `layout`) | A fresh child that loads the skill through the host mechanism | Nothing unless a question or blocker returns |
| New work, `init`, `shape`, `critique` | Question relay when native loading, same-child continuation and required nested roles are observed for this host/project | Confirm every answer in the complete packet, including source-cited pre-fills, before the same child writes; one explicit confirmation of the whole visible packet is enough |
| Any command whose required capability is unavailable or unverified | Your own Impeccable session from the supplied brief | Run the command and answer its questions, then report what finished |

The relay's first phase only inspects and drafts questions. Omitted answers or confirmation of gaps alone does not
approve the pre-fills. Additional questions and relevant source changes return for confirmation; lost continuation
uses your session. Confirming answers does not grant missing `PRODUCT.md` or `DESIGN.md` file/action permission.
A partial run is reported against the base without blind replay or unsolicited reversion. Native plugin loading and
interactive behavior on Claude Code and Codex remain unverified; the instructions require actual per-run observations.

The coordinator never uses Impeccable's `live` mode, because it runs agents with the sandbox and approvals turned
off.

## 5. What the coordinator does and does not do

- It runs Impeccable only after you select it for the request. An installed Impeccable is offered, not used.
- It pauses its own product edits while the session runs.
- It accepts only changes matching both listed files and the approved goal. An in-list but out-of-scope change,
  such as an unrelated dependency bump, is reported and excluded without unsolicited reversion or deletion.
- It reports `PRODUCT.md`, `DESIGN.md` and shared `.impeccable/` files a session created or changed as your project
  files, with a pointer to Impeccable's "Project files and git" guidance.
- It reuses your current task authority; if commit, integration or publication authority is missing, it presents
  the verified result and asks once for the named remaining effects. Choosing a route alone grants none.
- It asks before adding surfaces or behavior beyond your approved goal or changing a constraint; an in-goal file
  addition alone does not require another decision.
- It installs nothing, adds no ignore entries and removes no files unless you ask.

## 6. OOUX document linkage

| Link | What happens |
| --- | --- |
| Framing source | The coordinator reads `docs/steering/glossary.md`, `docs/steering/ux-objects.md` and the UX documents under `docs/ux/` where they exist, and passes their paths to Impeccable as read-only references. Without them it frames in conversation. |
| Persistent anchor | The `PRODUCT.md` reference section (setup step 4) lets Impeccable commands that load `PRODUCT.md` see the same object model. |
| Report-only write-back | After a change, the coordinator names each document the change made stale. It names the affected statement and a concrete follow-up through your documentation process, or a separate task if none exists. It edits none and creates no follow-up record without a separate request. |

These paths are a convention. The bundle works without them and needs no document package. If untracked or excluded
`PRODUCT.md` or `DESIGN.md` must be read by a session elsewhere, the brief passes absolute read-only paths; their
consumer ownership and upstream retention guidance stay intact without inferred copy, commit, ignore or removal.

## 7. Opt-in setup and cleanup

Ask the coordinator for any of these; it never does them on its own:

- install Impeccable through a route that needs no prompt answers (otherwise it gives you the exact command);
- add Impeccable's recommended ignore entries, limited to `.impeccable/` paths, after showing you the exact lines;
- remove Impeccable runtime or session output you name, such as screenshots or `review/`;
- add the OOUX reference section to `PRODUCT.md`.

`PRODUCT.md` and `DESIGN.md` hold your product and design context. They are left out of any cleanup unless you
name them, and they change only on your explicit direction.

### Tracked context across worktrees

To keep one tracked copy, put existing context under `docs/materials/impeccable/` (or your chosen in-repository
source directory) and commit that source through your own process. A typical source contains `PRODUCT.md`, optional
`DESIGN.md` and optional `.impeccable/`. The helper creates none of this content.

Before requesting setup, review the exact local exclude lines it adds:

```text
/PRODUCT.md
/DESIGN.md
/.impeccable
```

Stop editors, context-writing sessions and other helpers that can modify those root entries or the source during
link mode. Mutating setup requires quiescent entries; noncooperating concurrent writers are unsupported. Run the
script deployed inside your selected host's skill directory, for example:

```sh
sh .agents/skills/app-uiux-improve/scripts/link-impeccable-context.sh
sh .agents/skills/app-uiux-improve/scripts/link-impeccable-context.sh --check
```

For another layout, append its path: `sh <installed-skill>/scripts/link-impeccable-context.sh docs/context`.
Relative paths resolve from the current worktree root, including when invoked from a subdirectory. Run setup once
per worktree and clone; linked worktrees share Git's exclude file but each needs its own relative links.
Source symlinks escaping the worktree and symlinked source entries are refused. Existing root entries are preserved.
The script neither stages/untracks anything nor edits the root `.gitignore`. Root symlink exclusion does not ignore
runtime files reachable through a tracked `.impeccable` source; retain your own source-side ignore policy.

Check mode changes no files, locks or temporary files. It reports stable link/exclude codes and actions, then exits
0 when clean, 1 for unresolved states, or 2 when it cannot run. Repeated link mode changes no existing correct links
or exclude bytes. An I/O failure can retain completed links or exclude lines; inspect the report before rerunning.
If an editor replaces a link, `LINK_REPLACED` reports whether file/directory content is equal, differs or has a type
mismatch. Preserve both versions, merge desired changes into the tracked source by your own decision, then restore
the root link manually. Check again before continuing. The coordinator performs this recovery only on your request.
The local-only absolute read-only path fallback remains available when you do not use links.

## 8. Troubleshooting

| Symptom | What to do |
| --- | --- |
| Impeccable asks another question in a child session | Dependent writes stop; confirm the complete returned question round through the same child, or use your own session when relay capabilities are missing. |
| The child cannot load Impeccable | Plugin skills are visible only where their plugin is enabled. Check the observed current-project plugin enablement and native skill availability. Use your session if loading fails; do not load plugin-cache files or change enablement without a setup request. |
| The detector reports `hasVisualImplementation=false` | Inspect the actual target, UI code and executable local branch build. The signal is advisory; `--target` guarantees no detection fix. Report detector limits separately from inspected evidence. |
| A child cannot run `AUTONOMY_DIRECTIVE_CHECK` | The brief names actual capabilities and stop conditions, but does not satisfy or override a required live probe. Report it unavailable and stop dependent work; use your session or already authorized inline work, preserving native loading, every-answer confirmation and host permissions. |
| Audit persistence is unsupported | Check the installed supported help/interface before persistence. Return findings in the session report instead of inventing or retrying `audit-storage write`; create no unrequested file or installation change. These are local mitigations, not upstream runtime fixes. |
| A change appears outside the edit list | The coordinator reports the file and does not deliver it. Keep, move or revert it yourself, or ask the coordinator to include it in a new brief. |
| HEAD moved or attribution is unverifiable | A commit or checkout happened during the session. Review the reported changes yourself before accepting them. |
| Impeccable is not installed | Install it through a route in section 2, ask the coordinator to, or continue on the inline track. |
| A UX document is stale | Use the reported document and affected statement for your documentation process or a separate task; the coordinator reports rather than edits it. |
