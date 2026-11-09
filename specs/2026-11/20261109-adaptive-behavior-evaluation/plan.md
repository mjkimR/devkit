---
id: PLAN-adaptive-behavior-evaluation
spec: SPEC-adaptive-behavior-evaluation
---

# Technical Plan: `SPEC-adaptive-behavior-evaluation`

## 1. Constitution & Invariant Review

The scorer is test support, not a runtime scheduler or shipped interface. `ARCH-05-2-components` places test helpers in package-owned tests/support. `CAP-DLV-adaptive-development` requires truthful evidence. No architecture decision changes.

## 2. Architecture Overview & Impact

A standard-library JSON command scores supplied evidence without executing an agent. Missing execution reports unavailable; malformed or incomplete evidence reports inconclusive. Synthetic records cannot produce a behavioral pass. Evidence records identify the scenario and source and include explicit boolean checks for combined verification and recovery. No dependency or production write is added.

## 3. Component & Interface Design

`python packages/devkit-catalog/tests/support/adaptive_behavior_scorer.py INPUT.json` emits one JSON object with `status`, `scenario`, `source`, and `limitations`. Inputs identify `scenario`, `source`, `evidence_kind`, execution availability, and scenario-specific evidence. The scorer does not validate the authenticity of a supplied trace; its output labels its evidence kind. An observed pass is conditional on supplied evidence being truthful. Fixture mode produces `fixture_pass`, never a behavior pass. Violations take precedence over missing data. The interrupted-writer scenario requires evidence of retained work, ownership and recovery; the scorer only reads evidence and performs no cleanup.

## 6. Verification & Test Plan

Exercise complete, violating, missing, unavailable and synthetic records in deterministic pytest tests without credentials. Run relevant tests, `just test-affected`, lint, types and rules. Review trace claims and limitations independently; no live-agent outcome is claimed.
