# Design lenses

Read when choosing or developing the design direction. Select the lenses relevant to the supplied goal instead
of auditing every dimension. Start with the actual task, content and design-system constraints.

## Task and information

- Trace the representative task from entry to outcome and recovery. Remove a step only when users retain the
  information and control it provided.
- Group by the decisions people make, not by internal subsystem boundaries. Keep the primary action and its
  consequence apparent at the point of choice.
- Make states explain what happened, what remains and what action is available. Cover empty, loading, error and
  success states when the changed flow reaches them.
- Preserve orientation across screens. When simplifying navigation, show how users regain context and recover.

Example: a settings page can group choices by the person's goal, expose the most frequent action first and keep
advanced choices reachable. Hiding every label behind an icon saves space while increasing interpretation work;
compare that cost against the actual compact-layout requirement.

## Visual structure and character

- Set a clear hierarchy through content order, typography, spacing and contrast before adding decoration.
- Use the existing token and component vocabulary; change it only inside the authorized design scope.
- Choose a distinctive visual or interaction idea that explains content or improves the task. Give unusual ideas
  a concrete purpose beyond surprise.
- Check representative content density, long labels and narrow layouts. Preserve accessible contrast and readable
  text rather than judging a single ideal screenshot.

Example: a dashboard can emphasize the next decision with a strong typographic region and quieter supporting
metrics. Its character can come from purposeful composition instead of adding gradients to every card.

## Interaction and inclusion

- Make action results visible and preserve recovery for destructive or consequential changes.
- Keep keyboard operation, focus order, focus visibility, labels and error associations usable where applicable.
- Check touch target spacing and responsive transformations for the surfaces changed.
- Add motion or playful feedback only when it serves state, orientation or comprehension. Respect the project's
  reduced-motion behavior and avoid making essential information depend on animation.

## Choose and verify

Compare relevant directions by task clarity, required effort, discoverability, recovery, content fit and
implementation cost. Use qualitative tradeoffs tied to the artifacts rather than a universal scorecard.
A familiar design can be the best direction; an unusual idea can still reveal a worthwhile simplification.

After implementation, repeat the representative task and inspect its changed states. Record the tools and
coverage actually used. A screenshot review does not establish interactive behavior or real-user usability.

## Reference provenance

This guidance is written originally. The following repositories supplied structural and design-perspective
references, not copied instructions or evidence of effectiveness:

- [Agency Agents design roles](https://github.com/msitarzewski/agency-agents/tree/main/design): separate practical
  design assignments and purposeful unconventional expression.
- [Impeccable](https://github.com/pbakaus/impeccable): critique, bolder expression, distillation, delight and polish
  as selectable perspectives.
- [Anthropic agent prompts](https://github.com/anthropics/claude-cookbooks/tree/main/patterns/agents/prompts): bounded
  researcher delegation.

When copying upstream text in later work, inspect that revision's license and retain required attribution first.
