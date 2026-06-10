# Hosted Project Validation

status: completed

## Context

The static baseline covered attribution privacy, source inventory, project
metadata, and UI-state guardrails, but it only printed a reminder when Xcode
was installed. The repository had no current hosted project-file validation.

## Completed Scope

- Added a pinned GitHub Actions workflow with read-only repository permissions.
- Runs the canonical `make check` gate on a bounded `macos-15` job.
- Parses `ios-search-ads-sample.xcodeproj` whenever Xcode is available.
- Kept ADClient calls and attribution response handling outside hosted CI.
- Documented that project parsing does not prove the deprecated iAd service is
  functional on current iOS releases.
- Extended the checker and documentation to preserve the CI contract.

## Verification

- `python3 scripts/check-baseline.py`
- `make check`
- workflow YAML parse
- `git diff --check`
