# iOS App Store Search Attribution CI Baseline

## Status: Completed

## Context

`ios-appstore-search-attribution` has a Python-backed static attribution
privacy baseline behind `make check`. The repository needs that baseline to run
in GitHub Actions so ADClient request, UI state, accessibility, and
local-only handling guardrails are checked before review.

## Objectives

- Run the existing `make check` wrapper in GitHub Actions.
- Keep the hosted job independent of Xcode and Apple framework availability.
- Make the workflow presence part of the static baseline contract.

## Work Completed

- Added `.github/workflows/check.yml` to run `make check` on pushes, pull
  requests, and manual dispatches.
- Set up Python 3.12 for the static checker.
- Extended `scripts/check-baseline.py` to require the CI workflow and this
  completed plan.
- Updated README, VISION, SECURITY, and CHANGES with the CI baseline.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`

## Follow-Up Candidates

- Add a macOS/Xcode test job once the legacy scheme and simulator destination
  are documented.
