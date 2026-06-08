# iOS Search Attribution Baseline Plan

status: completed

## Context

`ios-appstore-search-attribution` is a compact Swift 3 sample that requests Apple Search Ads attribution data through `ADClient`. This Linux host does not provide Xcode, so local verification needs a static baseline while full simulator/device builds remain a macOS/Xcode responsibility.

## Objectives

- Keep the ADClient attribution request flow visible.
- Remove raw attribution debug logging and avoid extra segment updates.
- Add a local `make check` baseline for Xcode metadata, plist/storyboard XML, source inventory, and privacy guardrails.
- Document local-only attribution response handling and compatible-toolchain expectations.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
