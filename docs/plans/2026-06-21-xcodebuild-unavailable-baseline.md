# Xcodebuild-Unavailable Baseline

status: completed

## Context

The full native test runner correctly requires Xcode, but the otherwise portable
Python baseline also launched `xcodebuild` unconditionally. Linux lint therefore
failed before it could report the documented native-test boundary.

## Scope

1. Resolve `xcodebuild` before attempting the project metadata parse.
2. Skip that native-only parse explicitly when the tool is unavailable.
3. Preserve project-parse failure handling when Xcode is installed.
4. Add regression coverage for the unavailable-tool path.

## Work Completed

- Added an executable lookup before the Xcode project parse.
- Added a clear project-parse skip message for portable lint environments.
- Added a unit test that rejects any subprocess attempt when Xcode is absent.
- Preserved full `make check` as Xcode-required and hosted macOS as the native
  project and XCTest authority.

## Verification Completed

- Python baseline and regression tests passed without Xcode on Linux.
- Repository-root, external-directory, and hostile Make-root lint checks passed.
- Local `make check` passed portable stages and then stopped at the explicit
  Xcode-required native-test gate.
- Hosted macOS validation is required before merge to confirm project parsing and
  native XCTest remain green.

## Risk And Rollback

This changes verification behavior only when Xcode is unavailable. Rollback
restores the unconditional project-parse subprocess and the corresponding test.
