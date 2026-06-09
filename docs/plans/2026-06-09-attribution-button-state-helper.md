# Attribution Button State Helper

status: completed

## Context

The attribution sample already exposed state-specific button titles,
accessibility labels, hints, and enabled states. Those mutations lived across
setup and request-completion paths, which made it easy for future changes to
drift between visual state and accessibility state.

## Objectives

- Centralize ready, requesting, retry, and completed attribution button states.
- Keep request callbacks from mutating button titles, accessibility text, or
  enabled state directly.
- Preserve duplicate-request and completed-state guards.
- Extend the static baseline so state-specific UI and accessibility text remain
  aligned.

## Work Completed

- Added `AttributionButtonState` for ready, requesting, retry, and completed
  states.
- Added `applyAttributionButtonState(_:)` to update title, accessibility text,
  and enabled state in one place.
- Routed initial setup, in-flight requests, retry failures, and completed
  success through the helper.
- Updated README, SECURITY, VISION, CHANGES, and the static checker.

## Verification

- `python3 scripts/check-baseline.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
