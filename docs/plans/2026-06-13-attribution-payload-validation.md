# Attribution Payload Validation

status: planned

## Context

The attribution callback currently marks a request completed whenever `error`
is nil, even if the response omits the `Version3.1` dictionary or its
`iad-attribution` field. That presents an incomplete or malformed response as a
successful terminal request.

The sample already has a retry state for unusable results and intentionally
keeps valid attribution values local without logging, storage, or transmission.

## Priority

Completion is a user-visible terminal state that disables the request button.
It should require the response shape the sample actually consumes, otherwise a
transient or incompatible payload cannot be retried.

## Requirements

- R1. A nil transport error alone must not mark attribution completed.
- R2. Completion must require a `Version3.1` dictionary containing a non-nil
  `iad-attribution` value.
- R3. Missing or malformed required payload data must enter the existing retry
  state and leave `attributionRequestCompleted` false.
- R4. A present false attribution value remains valid; validation checks field
  presence, not truthiness.
- R5. Preserve generation guards, main-queue UI work, weak capture, local-only
  handling, button text, accessibility, and dependency/toolchain settings.
- R6. Add a callback-scoped static contract and completed verification evidence.

## Implementation Units

### U1. Fail closed on malformed responses

- **File:** `ios-search-ads-sample/ViewController.swift`
- Guard the required response dictionary and field before setting completed
  state, routing guard failure through `.retry`.

### U2. Enforce terminal-state ordering

- **File:** `scripts/check-baseline.py`
- Require payload validation, retry-and-return on failure, local consumption of
  the present field, and completed state only after the guard.

### U3. Document response semantics

- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`
- Record that malformed responses stay retryable without retaining payloads.

## Scope Boundaries

- Do not migrate from iAd/ADClient to AdServices in this change.
- Do not log, persist, upload, segment, or display attribution payload values.
- Do not change request generation, accessibility copy, project settings, or CI.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `python3 -m py_compile scripts/check-baseline.py`
- Parse plist, storyboard, workspace, project, and workflow metadata with all
  available local parsers.
- `git diff --check`
- Hostile mutations removing either required payload key, retry state, early
  return, local consumption, completion ordering, plan status, or verification
  evidence must be rejected.
