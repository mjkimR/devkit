---
title: UX object register
summary: "Read when reviewing the representations and calls to action of formal documents, supporting files, decisions and relations in repository viewer screens."
---

# UX object register

| Object | Role | Representations | Calls to action |
| --- | --- | --- | --- |
| Decision (ADR) | Developer reading repository | Header, Markdown body, raw source, related decision link | Open decision, view raw, follow related decision |
| Proposed decision (PADR) | Developer reading proposal | Source-labelled header, proposed supersession rows, Markdown body | Open proposal decision, follow target ADR |
| Supersession relation | Developer reading decision | Direction, related ID/title/status, whole/partial scope, replacement text, unavailable target | Follow related decision, reload relations |
| Design / Domain / Operations | Developer reading repository | Group entry, canonical ID/title/status, source/body, raw source, declared metadata | Search, include retired, open document, view raw, follow reference, Back |
| Reference | Developer reading repository | Incoming/outgoing direction, field, written ID, canonical ID/title/status, provenance label, unavailable/incomplete row | Follow target, reload references, Back |
| Supporting artifact | Developer reading repository | Parent identity, path, format/source, preview/raw bytes, unavailable/unsupported explanation | Open file, view raw, download, retry, Back |
