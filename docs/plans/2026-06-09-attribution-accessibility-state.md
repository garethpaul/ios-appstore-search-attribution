# Attribution Accessibility State

status: completed

## Context

The attribution button already described the local-only request before a scan
starts. Once the request begins, succeeds, or fails, the visual title changes
and assistive technologies should receive matching state text.

## Completed Scope

- Added an in-flight accessibility label and hint when attribution is requested.
- Added a retry accessibility label and hint when attribution fails and the
  button is re-enabled.
- Added a completed accessibility label and hint when attribution succeeds and
  the button remains disabled.
- Extended the static baseline and docs so state-specific accessibility remains
  aligned with the local-only privacy boundary.

## Verification

- `make check`
- `git diff --check`
