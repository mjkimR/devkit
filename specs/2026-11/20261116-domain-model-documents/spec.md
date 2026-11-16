---
id: SPEC-domain-model-documents
title: Domain-model documentation
summary: Establishes maintained conceptual domain views with clear authoritative sources, reusing document discovery unless the early pilot demonstrates a gap.
status: completed
created: 2026-11-16
depends_on:
  - SPEC-design-document-foundation
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-domain-model-documents] Domain-model documentation

## 1. Problem Statement & Motivation

Existing owners define validity and transformations separately. Two maintained conceptual entries make the relationships understandable together while preserving one normative owner per statement. The accepted direction is recorded by `ADR-linked-domain-relationship-views`; `PROP-domain-model-documents-target` retains the binding D1–D6 blueprint.

## 2. User Stories

- **US-1**: As an agent, I want to distinguish delivery relationships and distribution identities before selecting the relevant contract.
- **US-2**: As a document author, I want generic guidance and owner-led discovery in global and registered package contexts.

## 3. Non-Goals

- **Scope Excluded**: new Kind, identity grammar, runtime, namespace schema, template, viewer or lifecycle automation; normative transfers; operations implementation; class or schema catalogs; whole-layer reading prerequisites.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Useful relationship entries

- **Given** the current delivery and distribution owners
- **When** both ID-free entries are reviewed under D1
- **Then** each independently provides question, overview, authority boundary and next useful step; the delivery walkthrough distinguishes membership, prerequisite and provenance; every substantive summary identifies its owner and no normative statement transfers.

### [AC-02] Independent global discovery

- **Given** two fresh independent readers starting only with an owner ID and relationship question
- **When** they resolve the owner and follow selected links under D2
- **Then** each finds the withheld entry, explains the correct distinction and reaches the needed authority; opened sections, avoidable reads and next-step clarity are recorded.

### [AC-03] Registered package discovery

- **Given** an ignored fixture with global, registered alpha and unrelated beta documents
- **When** a fresh reader follows the alpha owner route and namespace commands under D3
- **Then** the route succeeds, default list/search covers global plus alpha, global-only excludes alpha and all-namespaces includes beta; relative links resolve at actual depth.

### [AC-04] Identity boundary

- **Given** two ID-free domain entries and existing indexed owners
- **When** list, search, resolve, refs and ordinary links are checked under D4
- **Then** entries remain absent as independent indexed nodes, existing owner operations still work and all selected ordinary destinations exist.

### [AC-05] Generic guidance delivery

- **Given** the existing docs instruction asset with domain conventions
- **When** it is synchronized into an isolated consumer under D5
- **Then** delivered bytes match the source, guidance has no repository IDs and no domain scaffold or identity is generated.

### [AC-06] Verified source and outcome

- **Given** the accepted D1–D6 scope
- **When** scoped rules, sync, workflow, existing distribution checks and applicable repository checks run
- **Then** results and source identity are recorded alongside a qualitative before/after comparison without timing or universal-discovery claims.

## 5. Assumptions and preserved evidence

The accepted ID-free direction and exact target scope remain valid on the current base. Existing contracts retain all validity, relation grammar, handoff and receipt/projection authority. Foundation validates design routes only. Planning inventories and options in [preserved materials](../../../docs/materials/2026-11/20261116-domain-model-documents/options-and-evidence.md) remain historical; Development supplies independent domain evidence. Operations follows sequentially in ~~`PROP-operations-documents`~~ (source Git `534ad541e9d1e87beffa6bbc4f1afa95c71f6106`); `PROP-design-document-lifecycle` and `PROP-design-document-viewer` remain deferred.
