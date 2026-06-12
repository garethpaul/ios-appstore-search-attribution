# Swift 5 Device SDK Type-Check

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
  the hosted Xcode 16.4 SDK, while preserving legacy ADClient behavior.
- Replaced the obsolete global accessibility announcement API with
  `UIAccessibility.post`.
- Added explicit iAd framework linkage so the ADClient reference resolves at
  link time.
- Upgraded Xcode-enabled `make check` runs to parse the Xcode project and
  type-check both Swift sources against the current iOS device SDK without
  launching the app or requesting attribution.
- Documented that current simulator and device SDKs expose the deprecated iAd
  module for compilation but omit the ADClient implementation required to link
  an executable. Full runtime/link verification therefore requires an older
  compatible SDK or a separate AdServices migration.
- Extended the static baseline and project documentation to preserve the build
  contract.

## Verification

- `python3 scripts/check-baseline.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- hosted macOS device-SDK type-check
- `git diff --check`
