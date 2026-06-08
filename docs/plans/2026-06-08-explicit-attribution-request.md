# Explicit Attribution Request Plan

status: completed

## Context

`ios-appstore-search-attribution` requests Apple Search Ads attribution data through `ADClient`. The existing baseline keeps the response local-only, but the sample still requests attribution during app launch.

## Objectives

- Move the attribution request behind an explicit user action.
- Prevent duplicate attribution requests while one is running or after one succeeds.
- Re-enable the action after a request failure without logging or transmitting details.
- Extend the static baseline so attribution cannot move back into launch or view-load code.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
