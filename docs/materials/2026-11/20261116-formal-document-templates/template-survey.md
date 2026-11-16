# Template survey for formal design, domain and operations documents

Planning evidence for `SPEC-formal-document-templates`. Four scouts ran on 2026-11-16 against worktree head
`94a6472c2`: one internal inventory and three external surveys (design-explanation templates, domain and operations
templates, template lifecycle management). Envelopes: historical Git `5664442947e15f78f81da1b2efcc65368d89b3ea:docs/proposals/PROP-formal-document-templates/envelopes/scout-01.yaml` to historical Git `5664442947e15f78f81da1b2efcc65368d89b3ea:docs/proposals/PROP-formal-document-templates/envelopes/scout-04.yaml`.

## 1. Internal inventory

### 1.1 Delivered documents

| Document | Question form | Authority boundary | Maintenance note | Central table |
| --- | --- | --- | --- | --- |
| `DESIGN-distribution-transactions` | bold `**Reader question:**` label | prose only | `Maintenance touchpoints` | none |
| `DESIGN-distribution-file-directory-replacement` | bold `**Reader question:**` label | prose only | `Maintenance seam` | none |
| `DOMAIN-bundle-selection-and-installation` | `## Question`, restates `summary` | `## Authority boundary and next useful step` | none | Concept / Relationship to the next concept / Authoritative detail |
| `DOMAIN-delivery-relationships` | `## Question` | `## Authority boundary and next useful step` | none | Relationship / Question answered / Representation and owner |
| `OPS-distribution-sync` | none | `## Authority and coverage boundary` | none | Symptom or documented state / Discriminating evidence / Next useful owner |

All five use topic headings; none uses the templates' numbered `## 1.`–`## 3.` sections. All five omit the
template's empty `related_*` lists except where a link is used, and quote `title`.

### 1.2 Templates and instructions

- `templates/{design,domain,operations}.md` carry guidance as body prose, pre-seed five empty `related_*` lists
  (design also `entrypoints: []`), show `status: draft` without the value list and have no table skeleton or
  authority-boundary section. `capability.md` and `ux.md` carry guidance in HTML comments and show the status values.
- No writing instruction mentions a question, authority boundary or maintenance note. `operations-writing.md`
  item 4 omits the normal-state observation that `operations.md` §2 and `CAP-DOCS-documentation-ownership` §3.1
  require; `domain-writing.md` item 4 omits the distinguishing example and glossary pointer of `domain.md` §2.
- `templates/design-template.md` was added in `386c6b0b2` and reduced to a pointer in `97518c2ae`; no tag
  (v0.1.0–v0.1.6) contains either commit. References: `packages/devkit-docs/tests/integration/bundles/docs/test_distribution.py`
  (template stem set, pointer checks), `packages/devkit-docs/README.md` (template count),
  `CAP-DOCS-documentation-ownership` §4, `CAP-DOCS-document-model` (file count, pointer clause), the tracked receipt
  `.devkit/installation.json`.
- `packages/devkit-docs/tests/e2e/bundles/docs/test_installed_consumer.py` instantiates the three templates by
  replacing placeholders and truncating at `## 1.`: removing that heading keeps the whole template body silently,
  and changed placeholder text makes the replacements no-ops.

### 1.3 Question clauses in force

- `CAP-DOCS-documentation-ownership` §3.3 item 2: "Authors SHOULD state the reader question, overview, authority
  boundary and next useful action."
- `ADR-linked-domain-relationship-views` §4: "An entry gives its question, relationship overview, authority boundary
  and next useful step", pointing at a §3.4 that `97518c2ae` removed. Its partial supersession by
  `ADR-formal-role-document-identities` does not cover this clause.
- `ADR-documentation-ownership-and-linked-design-entries` names a "question-specific entry" as a driver: a document
  focused on one question, which a scoping step satisfies without a section.

### 1.4 Overlap with `PROP-design-bundle-layout`

Both proposals edit `templates/design.md`, `templates/domain.md`, items 2, 6 and 7 of `design-writing.md` and
`domain-writing.md`, `CAP-DOCS-documentation-ownership` §3.3, the four design and domain documents and
`test_installed_consumer.py`. `PROP-design-bundle-layout` owns paths, the `area` field and support placement; it
leaves sections and guidance to this proposal. `depends_on` sequences the two.

## 2. External practice

| Source | Opening | Scope / authority | Guidance form | Tables | Old documents | Enforcement |
| --- | --- | --- | --- | --- | --- | --- |
| [KEP template](https://github.com/kubernetes/enhancements/blob/master/keps/NNNN-kep-template/README.md) | Summary, then Motivation | Goals and Non-Goals | HTML comments, removed when complete | none | untouched; changed KEPs warned | heading diff on changed files, warns only ([script](https://github.com/kubernetes/enhancements/blob/master/hack/verify-toc-vs-template.sh)) |
| [Rust RFC](https://github.com/rust-lang/rfcs/blob/master/0000-template.md) | Summary, then Motivation | none | body prose | none | minor amendments only | none |
| [Go design doc](https://github.com/golang/proposal/blob/master/design/TEMPLATE.md) | Abstract, then Background | none | `[bracketed]` | none | none | none |
| [PEP 12](https://peps.python.org/pep-0012/) | Abstract, then Motivation | Rejected Ideas | `[bracketed]` | none | historical records ([PEP 1](https://peps.python.org/pep-0001/)) | headers only |
| [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/) | Context and scope | Goals and non-goals | essay | none | n/a | none |
| [arc42 9.1](https://github.com/arc42/arc42-template) | Introduction and Goals | refer, don't repeat (§9) | help blocks; with-help and plain builds | placeholder rows outside help | template version only | none |
| [MADR 4.0](https://github.com/adr/madr) | Context and Problem Statement; question optional inside it | scope explicit | `{braces}`, `<!-- optional -->`; four variants | none | changelog only; renamed `template.md` without alias | optional markdownlint |
| [Good Docs Project](https://gitlab.com/tgdp/templates) | short scope intro | out-of-scope (guide), related resources | template + guide + process + example files | glossary Term/Abbreviation/Definition/Source | not stated | style lint |
| [Diátaxis](https://diataxis.fr/explanation/) | "about X" title; "why" question as a scoping prompt | "closely bounded" | n/a | n/a | n/a | n/a |
| [DDD Crew canvas](https://github.com/ddd-crew/bounded-context-canvas) | Name and Purpose | Assumptions, Open Questions | separate README | Ubiquitous Language | n/a | n/a |
| [GitLab runbooks](https://gitlab.com/gitlab-com/runbooks/-/blob/master/docs/README.md) | Symptom | Services, Escalation; link instead of duplicate | visible bullets | Symptom → Cause → Identifiable by → Solution | n/a | none |
| [Good Docs troubleshooting](https://gitlab.com/tgdp/templates/-/raw/main/troubleshooting/guide_troubleshooting.md) | one-line scope, then Symptom | links | guide file + `{placeholders}` | Symptom / Cause / Solution | n/a | none |
| [KCS v6](https://library.serviceinnovation.org/KCS/KCS_v6/KCS_v6_Practices_Guide/030/030/020/010) | Issue ("symptom, question or problem") | internal resolution field | one simple template | Issue / Environment / Resolution / Cause | evolve the template | n/a |
| [Copier](https://copier.readthedocs.io/en/stable/configuring/) / [cruft](https://cruft.github.io/cruft/) | n/a (scaffolds) | n/a | n/a | n/a | update and migrations | answers-file commit marker |

Observations that bear on the proposal:

1. **No source puts a question section beside a summary.** The question, when present, is one optional sentence
   inside the problem statement (MADR) or an authoring prompt (Diátaxis). MADR 3.0 removed a separate opening field
   because "all description should go into Context and Problem Statement".
2. **Scope is set by exclusions plus pointers to the owning document,** not by restating it (KEP and Google
   non-goals, arc42 §9, GitLab "link to README"). devkit's owner column in domain and operations tables goes further
   than external glossaries and is what makes those documents routers.
3. **Guidance lives in comments or a separate guide.** QEMU and psf/black moved issue-template suggestions into HTML
   comments because authors left them in ([QEMU](https://lists.gnu.org/archive/html/qemu-devel/2022-12/msg00153.html),
   [black #2269](https://github.com/psf/black/pull/2269)); comments hide leftovers in rendered output but stay in the
   raw text. The Good Docs Project keeps "a few embedded writing tips" in the template and the reasoning in the guide.
4. **Table skeletons are placeholder rows outside the help text** (arc42 §1, §5, §12); filled samples stay in help.
5. **Copy-once systems never migrate old documents** and carry no per-document template version; only scaffold tools
   that regenerate output (Copier, cruft) do. For five documents, migration is a local cost choice with no precedent
   either way.
6. **Body sections are suggestions in practice.** PEP 12 calls them "Suggested Sections"; KEP's heading check warns on
   changed files only. If a check is ever added, a warn-only leftover-guidance check is the cheapest start.
7. **Template files are retired without aliases** when unreleased or with a changelog entry (MADR rename, GitHub issue
   forms replacing Markdown templates).

## 3. Not reached

C4 guidance, Vale and remark-lint-frontmatter, official PagerDuty and Atlassian runbook templates, ITIL known-error
records, the Evans DDD Reference glossary, Backstage TechDocs, Obsidian and Notion templates, and the Good Docs
Project's deprecation policy. No empirical study measures question/summary duplication.
