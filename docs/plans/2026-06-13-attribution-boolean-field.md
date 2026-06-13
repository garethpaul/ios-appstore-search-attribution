# Validate Attribution Boolean Field

status: completed

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

- Required `iad-attribution` to decode as `Bool` in the callback guard before
  terminal state can be entered.
- Preserved both Boolean outcomes as valid and routed missing or non-Boolean
  values through the existing retry state.
- Extended the deterministic checker to reject untyped extraction, wrong field
  types, missing local consumption, completion reordering, stale plan status,
  and missing verification evidence.
- Documented the Boolean contract and local-only privacy boundary in the
  repository guidance and change log.

## Verification Completed

- All four Make gates (`make lint`, `make test`, `make build`, and
  `make check`) passed against the completed implementation.
- `python3 -m py_compile scripts/check-baseline.py`, workflow YAML parsing, and
  `git diff --check` passed.
- A prepared baseline passed and six hostile mutations were rejected: removing
  the `Bool` cast, casting the field as `String`, removing local consumption,
  moving completion before consumption, reopening the plan, and removing
  required verification evidence.
- `xcodebuild was unavailable` on this Linux host, so device-SDK Swift
  type-checking and ADClient runtime behavior were not executed locally. The
  canonical checker reports that limitation without claiming runtime coverage.
