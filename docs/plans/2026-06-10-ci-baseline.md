# iOS App Store Search Attribution CI Baseline

## Status: Completed

## Context

`ios-appstore-search-attribution` has a Python-backed static attribution
privacy baseline behind `make check`. The repository needs that baseline to run
in GitHub Actions so ADClient request, UI state, accessibility, and
local-only handling guardrails are checked before review.

## Objectives

- Run the existing `make check` wrapper in GitHub Actions.
- Pin the hosted toolchain and actions without persisting checkout credentials.
- Keep ADClient execution and attribution payload handling outside hosted CI.
- Make the workflow presence and security posture part of the baseline contract.

## Work Completed

- Added `.github/workflows/check.yml` to run `make check` on bounded macOS jobs
  for pushes, pull requests, and manual dispatches.
- Set up Python 3.12 with an immutable action and used an immutable checkout
  action with credential persistence disabled.
- Integrated project parsing and Swift device-SDK type-checking while keeping
  attribution requests and response handling outside the job.
- Extended `scripts/check-baseline.py` to require the CI workflow and this
  completed plan.
- Updated README, VISION, SECURITY, and CHANGES with the CI baseline.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`

## Follow-Up Candidates

- Add link or runtime validation only after migrating away from the unavailable
  ADClient implementation or documenting a compatible legacy SDK environment.
