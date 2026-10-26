# Q1: Review criteria for AI slop, from cited research, and the limits of automated detection

Spike Q1 of `PROP-review-refactor`: which cited findings on AI slop patterns, causes and refactoring techniques give
review criteria this repository can apply, and where automated detection stops working.

Research date: 2026-10-26. Sources were fetched on that date. When an arXiv preprint has several versions, the
version read is given.

## Legend

- **Basis**: `E` means a primary empirical study or measured result. `V` means official vendor guidance, which may
  cite internal testing that is not published. `P` means practitioner or design preference: established catalogs and
  style guides, not measured. `R` means a rule this repository already has.
- **Detection**: `D` means a deterministic tool can find it with a tolerable false-positive rate. `D?` means a tool
  can only produce candidates, and a person must judge each one. `S` means it needs semantic judgment.
- **Grade of source**: preprints are marked *(preprint)*. Industry reports are marked *(secondary)*. A report read
  only through press coverage is marked *(tertiary)*.

## 1. Evidence base

### 1.1 AI-assisted code quality

| # | Source | Finding used | Grade |
|---|---|---|---|
| C1 | He, Miller, Agarwal, Kästner, Vasilescu, "Speed at the Cost of Quality: How Cursor AI Increases Short-Term Velocity and Long-Term Complexity in Open-Source Projects", https://arxiv.org/abs/2511.04427 v3 (2026-01-26), MSR '26 | Adopting Cursor brings a "substantial and persistent increase in static analysis warnings and code complexity", which the authors call "major factors driving long-term velocity slowdown" (abstract). The velocity gain is transient. | E, peer-reviewed (MSR) |
| C2 | Paul, Zhu, Bayley, "Investigating The Smells of LLM Generated Code", https://arxiv.org/abs/2510.03029 v2 (2026-09-27) | Compared with reference solutions, LLM code has 63.34% more smells on average: 73.35% more implementation smells and 21.42% more design smells. The increase grows with task complexity (abstract). | E *(preprint)* |
| C3 | Borg et al., "Echoes of AI: Investigating the Downstream Effects of AI Assistants on Software Maintainability", https://arxiv.org/abs/2507.00788 v3 (2026-02-26) | In a randomized phase, the authors "did not detect systematic maintainability advantages or disadvantages" when other developers evolved AI co-developed code. They name code bloat and "cognitive debt" as open risks (abstract). | E *(preprint)*, counter-evidence |
| C4 | GitClear, "AI Copilot Code Quality 2025", https://www.gitclear.com/ai_assistant_code_quality_2025_research. The primary page returned HTTP 403, so it was read through LeadDev (2025-02-19), https://leaddev.com/software-quality/how-ai-generated-code-accelerates-technical-debt | 211M changed lines from 2020 to 2024. In 2024, duplicated blocks of 5 or more lines rose about 8x. Copy/pasted lines outnumbered moved (refactored) lines. | Industry *(secondary; tertiary as read)*. Correlational, vendor-owned method |
| C5 | Horikawa et al., "Agentic Refactoring: An Empirical Study of AI Coding Agents", https://arxiv.org/abs/2511.04824 v1 (2025-11-06) | Agent refactorings are mostly low-level: Change Variable Type 11.8%, Rename Parameter 10.4%, Rename Variable 8.5%. They give small but significant structural gains (abstract; 15,451 instances in Java). | E *(preprint)* |
| C6 | Watanabe et al., "On the Use of Agentic Coding: An Empirical Study of Pull Requests on GitHub", https://arxiv.org/abs/2509.14745 v3 (2026-02-09) | 83.8% of Claude Code PRs were merged. 45.1% of merged PRs needed human revision, "especially for bug fixes, documentation, and adherence to project-specific standards" (abstract). | E *(preprint)* |
| C7 | Anthropic, "Prompting best practices", section "Overeagerness", https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices (fetched 2026-10-26; the page covers Claude 4.5 to 5.5) | "Claude Opus 4.5 and Claude Opus 4.6 have a tendency to overengineer by creating extra files, adding unnecessary abstractions, or building in flexibility that wasn't requested". The sample prompt says: "Don't add error handling, fallbacks, or validation for scenarios that can't happen ... Only validate at system boundaries"; "Don't create helpers, utilities, or abstractions for one-time operations". | V |
| C8 | Anthropic, "Best practices for Claude Code", section "Add an adversarial review step", https://code.claude.com/docs/en/best-practices (fetched 2026-10-26) | "Chasing every finding leads to over-engineering: extra abstraction layers, defensive code, and tests for cases that can't happen. Tell the reviewer to flag only gaps that affect correctness or the stated requirements". | V. Applies directly to the review playbook itself |

### 1.2 Refactoring catalogs and design heuristics

| # | Source | Content used | Grade |
|---|---|---|---|
| F1 | Fowler, *Refactoring* 2nd ed. catalog, https://refactoring.com/catalog/ | The refactorings that remove structure: Inline Function, Inline Class, Collapse Hierarchy, Remove Dead Code, Remove Middle Man, Remove Flag Argument, Remove Subclass, Consolidate Conditional Expression. | P (canonical catalog) |
| F2 | refactoring.guru, "Speculative Generality", https://refactoring.guru/smells/speculative-generality | The smell is "an unused class, method, field or parameter". Treatments: Collapse Hierarchy, Inline Class, Inline Method, Remove Parameter. Ignore the smell when framework users need the element, or when tests rely on it. | P *(secondary summary of Fowler, ch. 3)* |
| F3 | Fowler, "Yagni", https://martinfowler.com/bliki/Yagni.html (2015-05-26) | A presumptive feature has costs of build, delay, carry and repair. YAGNI "does not apply to effort to make the software easier to modify". | P |
| F4 | Fowler, "Beck Design Rules", https://martinfowler.com/bliki/BeckDesignRules.html (2015-03-02) | The rules in priority order: passes tests, reveals intention, no duplication, fewest elements. "Anything that doesn't serve the three prior rules should be removed." | P |
| F5 | Metz, "The Wrong Abstraction", https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction (2016-01-20) | "duplication is far cheaper than the wrong abstraction". The remedy is to inline the abstraction back into its callers, then delete what each caller does not use. | P |

### 1.3 Agent guidance and context

| # | Source | Finding used | Grade |
|---|---|---|---|
| G1 | Gloaguen, Mündler-Sasahara, Müller, Raychev, Vechev, "Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?", https://arxiv.org/abs/2602.11988 v3 (2026-09-29) | LLM-generated context files had no significant effect on resolution: −0.5% on SWE-bench, −2% on CTXbench (§4.2, Table 3). Developer-written files gained about 2.4%, which is not significant (p=0.21) but significantly beat generated files (p=0.038). Cost rose 20-23% (§4.2). Agents follow named tooling: uv was used about 1.6 times per instance when named and under 0.01 times otherwise (§4.3). Codebase overviews did not shorten navigation (§4.3). Length and content category had no strong effect (§4.4). Recommendation: include "only ... specific additional instructions beyond what is already available in the codebase" (§6). | E *(preprint)* |
| G2 | Lulla et al., "On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents", https://arxiv.org/abs/2601.20404 v2 (2026-03-30) | 10 repositories, 124 PRs. With AGENTS.md, median runtime was about 28.6% lower and output tokens about 16.6% lower. Completion was comparable (abstract). | E *(preprint)*, partly counter to G1 on cost |
| G3 | Liu et al., "Lost in the Middle: How Language Models Use Long Contexts", https://arxiv.org/abs/2307.03172 v3, TACL | Accuracy is highest when relevant information sits at the start or end of the context and drops when it sits in the middle (abstract). | E, peer-reviewed. Tested on retrieval and QA, not on instructions |
| G4 | Jaroslawicz et al., "How Many Instructions Can LLMs Follow at Once?" (IFScale), https://arxiv.org/abs/2507.11538 v1 (2025-07-15) | The best model reaches 68% accuracy at 500 instructions. Earlier instructions are favored: primacy peaks around 150-200 instructions (§4.6). At high density, errors are mostly omissions (§4.8). Strong models stay at ≥95% up to 100 instructions, while weaker models collapse early (Tables 1-3). | E *(preprint)*. The instructions are keyword-inclusion constraints, so the absolute thresholds do not transfer |
| G5 | Geng et al., "Control Illusion: The Failure of Instruction Hierarchies in Large Language Models", https://arxiv.org/abs/2502.15851 v4, AAAI-26 | Models "struggle with consistent instruction prioritization, even for simple formatting conflicts". The system/user split does not reliably resolve conflicts (abstract). | E, peer-reviewed |
| G6 | Hong, Troynikov, Huber, "Context Rot", Chroma Technical Report (2025-07-14), https://www.trychroma.com/research/context-rot | Across 18 models, "model performance consistently degrades with increasing input length" even on simple tasks. Distractors have non-uniform impact. | Industry technical report *(secondary)* |
| G7 | Anthropic, "Effective context engineering for AI agents" (2025-09-29), https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | Context has an "attention budget". Aim for "the minimal set of information that fully outlines your expected behavior", where "minimal does not necessarily mean short". Use canonical examples instead of a "laundry list of edge cases". "Bloated tool sets ... ambiguous decision points" are a failure mode. | V |
| G8 | Anthropic, "Best practices for Claude Code", section "Write an effective CLAUDE.md" and "Avoid common failure patterns", https://code.claude.com/docs/en/best-practices (fetched 2026-10-26) | The per-line test: "Would removing this cause Claude to make mistakes?" "Bloated CLAUDE.md files cause Claude to ignore your actual instructions". Include and exclude tables. "If you emphasize many lines, none of them stands out." Things that must always happen belong in hooks. Test edits "by observing whether Claude's behavior actually shifts". | V |
| G9 | Anthropic, "Skill authoring best practices", https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices (fetched 2026-10-26) | "Concise is key". Keep the SKILL.md body under 500 lines. References one level deep. "Avoid offering too many options". "Use consistent terminology". "Avoid time-sensitive information". Degrees of freedom should match how fragile the task is. "Build evaluations first" and write "minimal instructions" against a baseline. | V |
| G10 | Anthropic, "Prompting best practices", section "Tool usage" (URL as C7) | Newer models "might now overtrigger"; "soften any aggressive language" such as "CRITICAL: You MUST". | V |
| G11 | OpenAI, "GPT-5 prompting guide", section "Instruction following", https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide (archived page, undated) | "poorly-constructed prompts containing contradictory or vague instructions can be more damaging to GPT-5 than to other models". The model spends reasoning reconciling contradictions, and removing contradictions improved performance. | V |
| G12 | OpenAI Codex, "AGENTS.md", https://learn.chatgpt.com/docs/agent-configuration/agents-md (fetched 2026-10-26, undated) | Files are concatenated from root to current directory, so later files override earlier ones. `project_doc_max_bytes` defaults to 32 KiB. Files past the limit are not loaded. | V. A hard truncation, not a soft quality effect |
| G13 | Jha et al., "Characterizing Prompt Compression Methods for Long Context Inference", https://arxiv.org/abs/2407.08892 v1, ICML 2024 Es-FoMo workshop | Token pruning "often lag[s] behind extractive compression". Extractive compression reaches 10x with minimal loss. Abstractive summarization gives only marginal gains (abstract). | E *(workshop)* |

### 1.4 CLI command surface

| # | Source | Content used | Grade |
|---|---|---|---|
| L1 | Prasad, Firshman, Tashian, Parish, *Command Line Interface Guidelines*, https://clig.dev/ (undated, living document) | Sections "Help": "Lead with examples", "Display concise help text by default", "Display the most common flags and commands at the start", "link to the web version of the documentation". "Subcommands": "Be consistent across subcommands", "Don't have ambiguous or similarly-named commands" (example: `update` vs `upgrade`), "Don't allow arbitrary abbreviations", "Don't have a catch-all subcommand". "Output": "Suggest commands the user should run". "Arguments and flags": "Use standard names for flags". "Future-proofing": keep changes additive, and change an interface only after a "well-documented deprecation process". | P (widely cited guideline) |
| L2 | GNU Coding Standards §4.8.2 "--help", https://www.gnu.org/prep/standards/html_node/_002d_002dhelp.html (undated page) | `--help` prints brief invocation documentation to stdout, exits successfully and ignores other options. It ends with a bug-report address and the home page. | P (convention) |
| L3 | POSIX.1-2024 (IEEE Std 1003.1-2024, Issue 8), XBD ch. 12 "Utility Conventions", §12.2 Utility Syntax Guidelines, https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap12.html | Guidelines 3-14 cover single-character options, `--` ending options, options before operands, and no optional option-arguments. | P (standard; applies to single-letter options) |
| L4 | Click 8.5.x, "Help Pages", https://click.palletsprojects.com/en/stable/documentation/ | "the docstring of the function is automatically used" as help. Short help is the first sentence, ellipsized on overflow. `\f` truncates help. | V (framework docs). Explains why docstrings are user-facing help in devkit |

## 2. Candidate review criteria

The ID prefixes are `RC-C` for code, `RC-G` for guidance and `RC-L` for CLI. Each criterion is a review question.
A finding against it must cite a location and a maintenance cost, as the proposal's design section requires.

### 2.1 Code

| ID | Criterion | Sources | Basis | Detection (tooling) |
|---|---|---|---|---|
| RC-C1 | **Duplicated behavior**: two or more places implement the same behavior, and a change to one must be repeated in the others. Count only behavior, not lines that merely look alike. | C4 (duplication trend), C1 (rising warnings), F4 | E (trend, correlational) + P | D? Token clones: jscpd v5 finds exact clones by default and renamed or near-miss clones opt-in (https://github.com/kucherenko/jscpd, README). Line clones: pylint `duplicate-code` R0801, "Similar lines in %s files" (pylint 4.1.3 docs). Neither is installed or configured here. Both find textual or token clones, not semantic duplication (jscpd's `--semantic` is experimental). Whether the copies represent one concept is S |
| RC-C2 | **Abstraction without demonstrated reuse**: a helper, base class, protocol, factory or configuration option with a single caller or implementation, or added "for later". | C7, F2, F3, F5; repo: `AGENTS.md:12` (create `base`/`utils` "until needed") and `:14` (no `BaseRepository`, Command or Unit of Work "without a concrete requirement") | V + P + R | S. A single-implementation count is mechanizable (AST and import graph), but whether an abstraction is wrong or premature is a judgment call. Remedies: Inline Function/Class, Collapse Hierarchy, Remove Middle Man (F1). Metz's inline-then-re-extract procedure (F5) |
| RC-C3 | **Speculative compatibility paths**: deprecation shims, legacy readers, version branches or migration code with no current consumer. | Repo policy `AGENTS.md:36` (no external consumers; "do not bump schema versions or add migration paths, deprecation shims, or legacy readers"); C7 ("building in flexibility that wasn't requested"); F3 | R + V + P | D? `rg` for `legacy|deprecat|compat|shim|fallback|v1` produces candidates. Whether a path has a consumer is S, and `devkit-advisory`/`devkit-cli` are excluded by `AGENTS.md:37-38` (semver contracts) |
| RC-C4 | **Unused code**: unreachable or uncalled functions, classes, parameters and imports, and commented-out code. | F1 (Remove Dead Code), F2 | P | D for imports and locals: ruff `F401`/`F841` (selected through `F`, `pyproject.toml:15`). D? for functions and classes: vulture, which says "likely to miss some dead code", scores confidence from 60-100% where "Values below 100% are very rough estimates", and flags code "only called implicitly" (https://github.com/jendrikseipp/vulture, README v2.3). In this repository, entry points, click decorators, `__init__` exports and rule plugins are reached dynamically, so a whitelist is needed. Not configured. Commented-out code: ruff `ERA001` (not selected) |
| RC-C5 | **Defensive boilerplate without a boundary**: catch-all `except`, silent `pass`, fallbacks or validation for states internal code cannot reach. | C7 ("only validate at system boundaries"), C8; repo `AGENTS.md:29` (failures are raised `AdvisoryError`s, not swallowed) | V + R | D? ruff `BLE001` blind-except, `S110` try-except-pass, `S112` try-except-continue, `B904` (none selected). Whether a state is reachable is S. A boundary handler is correct, so `BLE001` hits need triage (22 in `src`, see §3) |
| RC-C6 | **Unused parameters and flags**: a parameter no caller varies, or a boolean flag that switches between two behaviors. | F1 (Remove Flag Argument, Remove Parameter), F2 | P | D? ruff `ARG001-005` (not selected). Most hits are required protocol or stub signatures (§3). Flags: S |
| RC-C7 | **Complexity growth in AI-touched code**: functions whose branching or argument count grows. Report these as maintenance-cost evidence, not as defects. | C1, C2 | E | D for measurement: ruff `C901`, `PLR0912`, `PLR0913` (not selected), plus the repository's file-length warning (`packages/devkit/src/devkit_agt/features/rules/services/builtins/file_length/rule.py:8`, 400 lines). A threshold is a preference, and the remedy is S |
| RC-C8 | **Agent-generated surface churn**: renames, type changes or comment and docstring additions with no behavioral motivation. | C5 (agents favor low-level renames), C7 ("Don't add docstrings, comments, or type annotations to code you didn't change") | E + V | S. Matches the proposal's "cosmetic churn" non-goal. Criterion: no finding without a named cost |
| RC-C9 | **Behavior preservation** (gate, not smell): every refactoring keeps agreed behavior and passes relevant verification. | F1 (refactoring is behavior-preserving by definition), F4 rule 1; repo `AGENTS.md:57` (`just test-affected`) | P + R | D for the test run itself. Whether tests cover the agreed behavior is S |

### 2.2 Agent guidance (AGENTS.md, CLAUDE.md, skills, playbooks, instructions)

| ID | Criterion | Sources | Basis | Detection (tooling) |
|---|---|---|---|---|
| RC-G1 | **Information the agent can derive**: overviews, directory trees, file-by-file descriptions, standard language conventions, and anything already in the README. Remove or link it. | G1 (§4.3: overviews don't help; §6: include only what is "beyond what is already available"), G8 (Exclude table) | E + V | S. Matches the remediation text in `packages/devkit/src/devkit_agt/bundles/authoring/bundle/rules/agent_guide_size/rule.py:18-27` ("Drop project structure trees") |
| RC-G2 | **Keep repository-specific operational constraints**: tooling commands, boundaries, invariants and gotchas the agent cannot infer. These are the content shown to change behavior. | G1 (§4.3: named tools are used about 160 times more often), G8 (Include table) | E + V | S. Protective criterion: a removal must show the constraint is enforced or stated elsewhere |
| RC-G3 | **Duplicated instructions** across always-loaded guides, bundle constitutions, skills and playbooks: the same rule stated in several places, where the copies can drift apart. | G7 (minimal set), G9 (consistent terminology), G4 (each instruction adds to density) | V + E (indirect) | D? Near-duplicate sentences can be found with shingling or embeddings (not configured). Deciding which copy is canonical is S. The managed `.devkit/managed/` copies are excluded (projections, fixed at the source bundle) |
| RC-G4 | **Conflicting or overlapping-scope instructions**: two directives that cannot both hold, or an unclear precedence between nested guides. | G5 (hierarchies fail on conflicts), G11 (contradictions are especially damaging), G12 (later files override) | E + V | S. No deterministic tool detects semantic contradiction. An LLM pass produces candidates, and each candidate needs human confirmation |
| RC-G5 | **Obsolete exceptions and time-relative content**: carve-outs for removed code, "for now" or "temporary" notes, references to retired commands. | G9 (avoid time-sensitive information); repo: `RULE-agent-asset-wording` covers time-relative words (`packages/devkit/src/devkit_agt/bundles/authoring/bundle/rules/agent_asset_wording/rule.py:1`); `RULE-cli-contract` checks cited `devkit` commands exist (`packages/devkit/src/devkit_agt/features/rules/services/builtins/cli_contract/rule.py:1`) | V + R | D for wording and command citations (existing rules). Whether an exception still applies is S |
| RC-G6 | **Always-loaded context size**: what loads on every turn, compared with on-demand material (skills and references), and where critical directives sit. | G3, G6, G4 (primacy, omissions), G8, G9 (500-line SKILL.md), G12 (32 KiB hard truncation) | E + V | D for size: `RULE-agent-guide-size` (8192 bytes, `.../agent_guide_size/rule.py:32`) and `RULE-skill-document-size` (12288 bytes, `.../skill_document_size/rule.py:33`). Position and relevance are S. The thresholds are preference: G1 §4.4 found length has no strong effect |
| RC-G7 | **Emphasis and hedging inflation**: many MUST, CRITICAL or IMPORTANT lines, or hedged directives. | G8 ("If you emphasize many lines, none of them stands out"), G10 (overtriggering), repo `AGENTS.md:28` (no hedged directives) | V + R | D: `RULE-agent-asset-wording` (`.../agent_asset_wording/rule.py:30-36`, hedges and emphatic capitals) |
| RC-G8 | **Too many options or laundry-list edge cases** in place of one default with an escape hatch, or canonical examples. | G7, G9 ("Avoid offering too many options") | V | S |
| RC-G9 | **Mechanical requirement as prose**: an "always/never" instruction that a rule or hook could enforce. | G8 (hooks are "deterministic and guarantee the action"; rules that already hold can be deleted "or convert[ed] to a hook"); repo: recurrence prevention through `CAP-GOV-rule-authoring` (proposal §3) | V + R | S to identify. Adopting a rule needs an evidenced recurring failure (proposal §3) |
| RC-G10 | **Behavioral verification of guidance edits**: each removal or consolidation is checked against observed agent behavior or a representative task, not against byte counts. | G8 ("test changes by observing whether Claude's behavior actually shifts"), G9 (evaluations first, baseline), G1 (§6 "rigorously evaluated") | V + E | S. Gate criterion |

### 2.3 CLI command surface

| ID | Criterion | Sources | Basis | Detection (tooling) |
|---|---|---|---|---|
| RC-L1 | **Overlapping or similarly-named commands** (the `update`/`upgrade` class), and catch-all defaults. | L1 (Subcommands), G7 (ambiguous tool sets for agents) | P + V | D? The click tree can be walked to list names, then compared by edit distance or synonyms. Overlap in purpose is S |
| RC-L2 | **Fragmented operations**: one user goal needs several commands in a fixed sequence. | L1 (consistency; suggest next commands), G7 ("If a human can't tell which tool to use, an AI agent can't be expected to do better") | P + V | S. Merging commands changes the contract: proposal §3 says it becomes a separately scoped follow-up |
| RC-L3 | **Inconsistent grouping and flag names**: noun-verb ordering, the same concept spelled with different flags, non-standard flag names. | L1 ("Be consistent across subcommands", "Use standard names for flags"), L3 | P | D: walk the click tree and compare option names across commands (not built). Choosing the canonical name is S |
| RC-L4 | **Help accuracy and usefulness**: the docstring and help describe actual behavior, the most common usage comes first, examples are included, and help names the next step or a doc link. | L1 (Help), L2, L4 (docstrings are help); repo `AGENTS.md:26-28` (sentinels, `[ACTION]` directives) | P + R | D for existence (non-empty help, `\f` placement, every documented command exists: `RULE-cli-contract`). Accuracy against behavior is S |
| RC-L5 | **Contract changes stay out of refactoring**: a removal, rename or consolidation of a command or flag is a contract change and never a behavior-preserving refactor. | L1 (Future-proofing: additive changes, deprecation), proposal §3; repo `AGENTS.md:36` (in-place breaking changes allowed, but still a contract change) | P + R | S (classification gate) |

## 3. Automated detection limits

1. **Clone detectors find text, not concepts.** jscpd and pylint R0801 match token or line sequences (L-sources in RC-C1).
   Renamed or near-miss detection is opt-in, and semantic detection is experimental. They miss duplicated behavior
   written differently. They also flag deliberate parallel structure, such as test arrangements or click command
   boilerplate. Per F5, merging such copies can be the worse outcome.
2. **Dead-code tools cannot see dynamic dispatch.** vulture states its own limits (RC-C4). In this repository,
   commands mount through `devkit.commands` entry points, hygiene through `devkit.hygiene`, and rules load from
   bundles (`AGENTS.md:16`; `docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md`, section 3, "Hygiene
   extensions"). Each of these is a source of false "unused" reports.
3. **Measured false-positive load in this repository** (read-only probe, ruff 0.17.0 with `--preview --no-cache
   --exit-zero` over `packages tools`, 2026-10-26). Unselected rules produce 810 findings: ARG001 199, PLR6301 162,
   C901 110, PLR0913 107, ARG005 88, ARG002 70, PLR0912 50, BLE001 23, S112 1. Split by location: 193 of the 199
   ARG001 hits, all 88 ARG005 hits and 52 of 70 ARG002 hits are in `tests/` (stub and monkeypatch signatures that
   must match). In `src`: 6 ARG001, 18 ARG002, 22 BLE001, 126 PLR6301. These counts are review inputs, not
   rule-adoption evidence. Adopting any of them needs `CAP-GOV-rule-authoring` evidence (proposal §3), and the
   current selection is `pyproject.toml:15`.
4. **Size checks measure bytes, not quality.** `RULE-agent-guide-size` and `RULE-skill-document-size` are budgets.
   G1 §4.4 found that context-file length had no strong effect on success. G2 found that an AGENTS.md lowered runtime
   and tokens. A size warning is therefore a prompt to review, not a finding.
5. **Contradiction, obsolescence, derivability and purpose overlap** (RC-G1, G4, G5, L1, L2) have no deterministic
   detector. G5 shows that even the model does not resolve conflicts reliably, so an LLM reviewer's conflict list is
   a candidate list that needs human confirmation.
6. **The reviewer also over-reports.** C8: a reviewer asked to find gaps will find some, and acting on all of them
   adds abstraction and defensive code. The playbook therefore requires a named cost for each finding and drops
   preference-only findings by default.
7. **Thresholds from studies do not transfer.** IFScale's 100-500 instruction curves use keyword-inclusion
   constraints (G4). Lost in the Middle tests retrieval (G3). Both support the direction "fewer, prominent, non-
   conflicting directives". Neither supports a numeric budget for this repository.

## 4. When reducing lines or tokens removes necessary constraints

- **G7**: "minimal does not necessarily mean short". The target is the minimal set that "fully outlines your
  expected behavior".
- **G1 §4.3**: agents act on repository-specific instructions (uv used about 1.6 times per instance when named,
  under 0.01 otherwise). Deleting such a line changes behavior. Developer-written files beat generated ones, and
  length did not predict effect (§4.4).
- **G8**: the deletion test is behavioral ("Would removing this cause Claude to make mistakes?"), and edits are
  verified by observed behavior.
- **G9**: degrees of freedom. Fragile operations need low-freedom, exact instructions ("Run exactly this script").
  Compressing them into a heuristic removes the guardrail. Testing across models: "What works perfectly for Opus
  might need more detail for Haiku."
- **G13**: token-level pruning loses more task performance than extractive selection. Removing whole irrelevant
  units is safer than shortening every unit.
- **G12**: in the opposite direction, overflow past 32 KiB silently drops whole files in Codex. Size matters there
  for loading, not for quality.
- **C3** (code side): no measured maintainability penalty from AI-assisted code in a randomized setting. This
  argues against treating AI origin, or line count, as a defect in itself.

Derived review rule (all three surfaces): a reduction is acceptable when the removed content is (a) derivable from
the repository, (b) duplicated with a named canonical copy kept, (c) enforced mechanically elsewhere, or (d) shown by
a behavioral check to be unnecessary. Token or line delta is reported but is never the justification
(proposal §3: "token or line reduction alone is not proof of correctness").

## 5. Gaps

- GitClear primary report (HTTP 403). Figures are taken from LeadDev coverage only.
- Fowler, *Refactoring* 2nd ed. ch. 3 smell text (Duplicated Code, Speculative Generality, Dead Code). Only the
  catalog index and a secondary summary were read.
- pylint `min-similarity-lines` and jscpd `min-tokens` defaults are not confirmed from the fetched pages. vulture
  v2.3 is the version shown in its README pre-commit example, not a confirmed latest release.
- No study was found that directly measures duplication or conflicts inside AGENTS.md or skills sets. RC-G3 and
  RC-G4 rest on general instruction-conflict evidence (G5, G11).
