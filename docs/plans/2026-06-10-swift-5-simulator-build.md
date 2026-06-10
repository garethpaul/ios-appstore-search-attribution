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
- Raised the deployment target from iOS 10 to iOS 12, the minimum accepted by
  the hosted Xcode 16.4 simulator SDK, while preserving legacy ADClient behavior.
- Replaced the obsolete global accessibility announcement API with
  `UIAccessibility.post`.
- Added explicit iAd framework linkage so the ADClient reference resolves at
  link time.
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
