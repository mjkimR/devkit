# app-uiux-improve usage guide

This guide is for the person who uses the `app-uiux-improve` bundle. Read it before you select the bundle or later,
when you want to recall the flow. It is not an agent asset: sync never deploys it, and no skill file links it.

## 1. What it is for

`/app-uiux-improve <goal>` improves the interface and user flows of software: web and desktop applications,
dashboards, admin tools, settings and responsive views. The coordinator (the agent you invoke) frames the domain
objects a change touches, improves the screens inline or through an Impeccable session you select, and carries the
changes through your project's own workflow and checks.

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
3. Run Impeccable's `init` in a session you operate. It asks you about the product and writes `PRODUCT.md`.
4. Add an OOUX reference section to `PRODUCT.md`, in that `init` session or by asking the coordinator. The section
   names your glossary, object register and UX document directory by path and says to read them before structural
   work. It copies none of their content, so it cannot drift from them:

   ```markdown
   ## Object model

   Before structural UI work, read docs/steering/glossary.md (object names),
   docs/steering/ux-objects.md (representations and actions per role) and the
   UX documents under docs/ux/ for the affected screens.
   ```

## 3. Per-task flow

1. Start: invoke `/app-uiux-improve <goal>` in your devkit session. The coordinator recovers the goal and completes
   your workflow's steps that come before implementation (branch, worktree, required records).
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
5. Acceptance: the coordinator compares the working tree with the recorded base, verifies the accepted changes,
   reports anything outside the brief and each OOUX document the change made stale, and continues your workflow.
6. Cleanup, only if you ask.

If your workflow drafts new screens before code (for example in a planning document), the screen is drafted there
first and Impeccable implements and refines that draft.

Example request:

```text
/app-uiux-improve Merge the Customers and Invoices pages so overdue invoices can be chased from the customer view. Use Impeccable to polish the result.
```

The coordinator frames Customer and Invoice from your glossary and object register, implements the merged view
through your workflow, then briefs a fresh child to run `polish` and `audit` on the two changed files.

## 4. Launch routes

| Commands | Route | What you do |
| --- | --- | --- |
| `polish`, `audit` and narrow refinement commands (`distill`, `typeset`, `layout`) | A fresh child agent the coordinator starts with the brief | Nothing, unless the child returns a blocker |
| New work, `init`, `shape`, `critique`, or any command the child could not run | Your own Impeccable session, started from the brief the coordinator hands you | Run the commands, answer Impeccable's questions, then tell the coordinator the session finished and what it reported |

The coordinator never uses Impeccable's `live` mode, because it runs agents with the sandbox and approvals turned
off.

## 5. What the coordinator does and does not do

- It runs Impeccable only after you select it for the request. An installed Impeccable is offered, not used.
- It pauses its own product edits while the session runs.
- It accepts only changes to the files the brief lists; other changes are reported, not reverted, deleted or
  delivered.
- It reports `PRODUCT.md`, `DESIGN.md` and shared `.impeccable/` files a session created or changed as your project
  files, with a pointer to Impeccable's "Project files and git" guidance.
- It has no commit, integration or publication authority beyond what your workflow already grants.
- It installs nothing, adds no ignore entries and removes no files unless you ask.

## 6. OOUX document linkage

| Link | What happens |
| --- | --- |
| Framing source | The coordinator reads `docs/steering/glossary.md`, `docs/steering/ux-objects.md` and the UX documents under `docs/ux/` where they exist, and passes their paths to Impeccable as read-only references. Without them it frames in conversation. |
| Persistent anchor | The `PRODUCT.md` reference section (setup step 4) lets Impeccable commands that load `PRODUCT.md` see the same object model. |
| Report-only write-back | After a change, the coordinator names each document the change made stale. It edits none of them; your workflow's own documentation step updates them. |

These paths are a convention. The bundle works without them and needs no document package.

## 7. Opt-in setup and cleanup

Ask the coordinator for any of these; it never does them on its own:

- install Impeccable through a route that needs no prompt answers (otherwise it gives you the exact command);
- add Impeccable's recommended ignore entries, limited to `.impeccable/` paths, after showing you the exact lines;
- remove Impeccable runtime or session output you name, such as screenshots or `review/`;
- add the OOUX reference section to `PRODUCT.md`.

`PRODUCT.md` and `DESIGN.md` hold your product and design context. They are left out of any cleanup unless you
name them, and they change only on your explicit direction.

## 8. Troubleshooting

| Symptom | What to do |
| --- | --- |
| Impeccable asks a question in a child session | The child stops and returns the question as a blocker. Run the command in your own Impeccable session and answer it there. |
| The child cannot load Impeccable | Your agent host does not give child agents the skill. The coordinator moves the command to your session. |
| A change appears outside the edit list | The coordinator reports the file and does not deliver it. Keep, move or revert it yourself, or ask the coordinator to include it in a new brief. |
| HEAD moved or attribution is unverifiable | A commit or checkout happened during the session. Review the reported changes yourself before accepting them. |
| Impeccable is not installed | Install it through a route in section 2, ask the coordinator to, or continue on the inline track. |
| A UX document is stale | Update it through your workflow's documentation step; the coordinator only reports it. |
