# Attribution Accessibility Affordance

status: completed

## Context

Search Ads attribution can expose sensitive device and campaign context, so the
sample keeps the request behind an explicit button and keeps the response
local-only. Assistive technologies should receive the same local-only action
context through the button's accessibility text.

## Objectives

- Add accessibility text to the attribution request button.
- Preserve explicit, user-triggered attribution behavior.
- Keep attribution responses local-only with no logging, storage, upload, or
  segment behavior.
- Extend the static baseline so the accessibility affordance stays aligned
  with the privacy boundary.

## Verification

- `python3 scripts/check-baseline.py`
- `make check`
- `git diff --check`
