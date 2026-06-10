# Attribution Accessibility Announcements

status: completed

## Context

The attribution sample already centralized ready, requesting, retry, and
completed button labels, hints, titles, and enabled states. Because requesting,
retry, and completed states are triggered by user-initiated asynchronous
attribution work, assistive technologies should also receive announcements when
those states change.

## Completed Scope

- Extended the centralized attribution button state helper with an `announce`
  flag.
- Kept the initial ready state silent during view setup.
- Posted accessibility announcements for requesting, retry, and completed
  attribution states.
- Extended the static privacy baseline so announcement behavior stays aligned
  with state-specific accessibility text.
- Updated README, VISION, SECURITY, and CHANGES with the announcement guardrail.

## Verification

- `python3 scripts/check-baseline.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
