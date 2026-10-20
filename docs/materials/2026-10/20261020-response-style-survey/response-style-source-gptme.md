---
id: MAT-response-style-source-gptme
title: "Response-style source: gptme"
summary: "Records the pinned gptme prompt, observed popularity and maintenance, license scope and transferable reply-style ideas."
created_at: 2026-10-20
---

# [MAT-response-style-source-gptme] gptme

## Provenance

- First-party repository: https://github.com/gptme/gptme
- Metadata endpoint: https://api.github.com/repos/gptme/gptme
- Observed: 2026-10-20 Asia/Seoul (2026-10-19 23:04 UTC); 4,456 stars, not archived.
- Default branch: `master`; its retrieved commit: `90221f5ff2958b575ac0da4a8685ccb0cd996ea6`, dated 2026-10-19T22:28:15Z.
- Repository pushed_at: 2026-10-19T22:51:01Z (not proof that the default branch or prompt changed then).
- Prompt: [pinned source](https://github.com/gptme/gptme/blob/90221f5ff2958b575ac0da4a8685ccb0cd996ea6/gptme/prompts/templates.py); section: prompt_gptme.communication_guidance, lines 135-147.
- Prompt SHA-256: `f2615f5cca6c47a70c27a62fc425aaaa89703e109ba075a2b221b189d5321dfe`. This fingerprints the retrieved bytes, not a mirror stored here.
- License: [pinned license text](https://github.com/gptme/gptme/blob/90221f5ff2958b575ac0da4a8685ccb0cd996ea6/LICENSE), MIT; applies to this inspected repository file or plugin. Website terms and unrelated plugins are not inferred.

## Practice and interpretation

Pair efficient communication with complete explanations; compact and full prompt modes retain that balance. Avoid empty offers to continue.

## Scope and limits

The source also asks for a concrete next step at the end. That conflicts with devkit replies where the task is already complete, so do not import it unconditionally. A source comment claims cross-model measurements, but no linked dataset or protocol was verified; it is a source claim, not measured evidence here.

This source establishes published practice, not effectiveness. Separate repository ownership does not establish
independent prompt ancestry. Do not count repeated wording as multiple independent votes until provenance is
checked. Only original paraphrases of ideas enter the candidate; no source examples, wording or structure are
copied. Revalidate the pin before Development if the affected file is no longer available.
