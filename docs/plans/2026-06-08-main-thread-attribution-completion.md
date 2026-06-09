# Main-Thread Attribution Completion Plan

status: completed

## Context

The sample requests Apple Search Ads attribution data through `ADClient` after a user taps the attribution button. The completion handler controls button state and request flags, so those UI-facing updates should be explicit about returning to the main queue.

## Objectives

- Dispatch attribution completion handling onto the main queue.
- Keep duplicate-request, retry, and completed-state behavior unchanged.
- Extend the static baseline so future changes keep completion state and UI updates inside the main-queue block.
- Document the main-thread completion expectation alongside the existing local-only attribution guardrails.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
