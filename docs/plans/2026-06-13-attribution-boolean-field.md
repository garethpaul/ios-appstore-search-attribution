# Validate Attribution Boolean Field

status: planned

## Context

The attribution completion verifies the `Version3.1` dictionary and the
presence of `iad-attribution`, but it accepts the field as an untyped object.
Malformed values such as strings or null placeholders can therefore mark the
request complete instead of returning the user to the retry state.

## Requirements

- R1. `iad-attribution` must decode as `Bool` before completed state is entered.
- R2. Both `true` and `false` are valid terminal attribution values.
- R3. Missing or non-Boolean values must use the existing retry path.
- R4. The validated Boolean must remain local and must not be logged, stored, or
  transmitted.
- R5. Request generation, main-queue completion, weak capture, accessibility,
  and button-state behavior must remain unchanged.
- R6. The deterministic checker must reject an untyped field extraction or
  completion before validation.

## Scope Boundaries

- Do not execute ADClient requests during local or hosted validation.
- Do not change project settings, iAd linkage, deployment target, or workflow.
- Do not add persistence, logging, analytics, or network transmission.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `python3 -m py_compile scripts/check-baseline.py`
- Workflow YAML parsing
- `git diff --check`
- Hostile mutations must reject removed Bool casting, untyped extraction,
  removed local consumption, completed-state reordering, stale plan status, and
  missing verification evidence.

## Work Completed

Pending implementation.

## Verification Completed

Pending implementation and verification.
