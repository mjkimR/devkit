# Design lenses

Select the lenses relevant to the supplied goal instead of auditing every dimension; start with the actual task,
content and design-system constraints.

## Object framing (ORCA)

Frame before layout or styling when a request adds, merges or reorders views or flows; skip it for a local change
(one component, one state, copy or spacing). Frame only the objects the request touches; no diagram or notation is
required.

- Objects: name the domain nouns users think in, not widgets ("Invoice", not "Table").
- Relationships: state how objects connect; each relationship is a navigation path between their views.
- CTAs: place each action on the object it acts on rather than in a global menu.
- Attributes: separate the identifiers people scan for from supporting metadata, per view.
- States: give every changed view its empty, loading, error and populated states.

Example: a request merges "Customers" and "Invoices" pages. Objects: Customer, Invoice. Relationship: a Customer has
many Invoices, so the Customer view lists them and each Invoice links back to its Customer. CTAs: "Send reminder" sits
on an overdue Invoice, "Edit contact" on the Customer. Attributes: invoice number and amount identify an Invoice; issue
date and status are metadata. States: a Customer with no Invoices shows an empty state with "Create invoice".

### Framing sources

Read these files only where they exist, using a partial set as far as it goes:

- Object names: the project glossary (`docs/steering/glossary.md`, or a package glossary beside the affected code).
- Representations and CTAs per role: the object register (`docs/steering/ux-objects.md`, or a package register
  beside the affected code).
- Attributes, states and interactions: the UX documents of the affected screens (`docs/ux/<area>/`).

These paths are an optional project convention; if none exist, frame in conversation. Never write these files;
after an accepted change, report each one the change made stale and leave its update to the consumer workflow's own
step.

## Task and information

- Trace the representative task from entry to outcome and recovery. Remove a step only when users retain the
  information and control it provided.
- Group by the decisions people make, not by internal subsystem boundaries. Keep the primary action and its
  consequence apparent at the point of choice.
- Make states explain what happened, what remains and what action is available. Cover empty, loading, error and
  success states when the changed flow reaches them.
- Preserve orientation across screens. When simplifying navigation, show how users regain context and recover.
- Weigh the interpretation cost of icon-only labels against the actual compact-layout requirement.

## Visual structure and character

- Set a clear hierarchy through content order, typography, spacing and contrast before adding decoration.
- Use the existing token and component vocabulary; change it only inside the authorized design scope.
- Choose a distinctive visual or interaction idea that explains content or improves the task. Give unusual ideas
  a concrete purpose beyond surprise.
- Check representative content density, long labels and narrow layouts. Preserve accessible contrast and readable
  text rather than judging a single ideal screenshot.

## Interaction and inclusion

- Make action results visible and preserve recovery for destructive or consequential changes.
- Keep keyboard operation, focus order, focus visibility, labels and error associations usable where applicable.
- Check touch target spacing and responsive transformations for the surfaces changed.
- Add motion or playful feedback only when it serves state, orientation or comprehension. Respect the project's
  reduced-motion behavior and avoid making essential information depend on animation.

## Baseline craft checks

Apply these to every changed view, on both tracks:

- Secondary and disabled text keeps readable contrast against its background.
- Type sizes follow one consistent scale; one typeface is not stretched across every role without a reason.
- No decorative gradient or nested container without a purpose it explains.
- Every changed view has its empty, loading and error states.

## Choose and verify

Compare relevant directions by task clarity, required effort, discoverability, recovery, content fit and
implementation cost, as qualitative tradeoffs tied to the artifacts rather than a universal scorecard. A familiar
design can be the best direction; an unusual idea can still reveal a worthwhile simplification.

After implementation, repeat the representative task, inspect its changed states and record the tools and coverage
actually used. A screenshot review does not establish interactive behavior or real-user usability.

## Reference provenance

This guidance is written originally. These sources supplied structure and perspective, not copied instructions or
evidence of effectiveness:
[Agency Agents design roles](https://github.com/msitarzewski/agency-agents/tree/main/design) (practical and
purposeful unconventional design assignments);
[Impeccable](https://github.com/pbakaus/impeccable) (critique, bolder expression, distillation, delight and polish as
perspectives; a user who selects Impeccable runs its maintained commands in a delegated session instead, and this
guidance copies none of its text); Object-Oriented UX (the ORCA framing order: objects, relationships, CTAs,
attributes); [Anthropic agent prompts](https://github.com/anthropics/claude-cookbooks/tree/main/patterns/agents/prompts)
(bounded researcher delegation).

Before copying upstream text in later work, inspect that revision's license and retain required attribution.
