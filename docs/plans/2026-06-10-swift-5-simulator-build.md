# Swift 5 Simulator Build

status: completed

## Context

The hosted gate parsed the Xcode project but did not compile its Swift sources.
The target still selected Swift 3 and used the corresponding app-launch
signature, so metadata validation could pass while current Xcode rejected the
application source.

## Completed Scope

- Updated both target configurations from Swift 3 to Swift 5.
- Updated the app delegate launch-options signature for Swift 5.
- Preserved the documented iOS 10 deployment target and legacy ADClient sample
  behavior.
- Upgraded Xcode-enabled `make check` runs to compile an unsigned Debug build
  for the iOS Simulator without launching the app or requesting attribution.
- Extended the static baseline and project documentation to preserve the build
  contract.

## Verification

- `python3 scripts/check-baseline.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- hosted macOS simulator build
- `git diff --check`
