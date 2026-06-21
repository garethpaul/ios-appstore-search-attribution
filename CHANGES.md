# Changes

## 2026-06-21

- Made the portable attribution baseline explicitly skip Xcode project parsing
  when `xcodebuild` is unavailable while keeping full native XCTest mandatory.
- Added a regression proving Linux lint does not attempt an unavailable Xcode
  subprocess while hosted macOS remains responsible for full `make check`.

## 2026-06-19

- Replaced the retired iAd callback with the current AdServices token and Apple
  attribution REST flow while retaining safe unsupported behavior before iOS 14.3.
- Added an ephemeral, credential-free URL session with fixed endpoint ownership,
  10-second request and 20-second resource timeouts, and a streamed 64 KiB cap.
- Added strict JSON/MIME/status/Boolean validation, fixed 404 intervals, bounded
  500 backoff, and three total attempts.
- Added generation-owned cancellation across timeout, navigation, backgrounding,
  duplicate starts, and late completions without caching, persistence, or logging.
- Added native XCTest with mocked networking, location-independent Make gates,
  hosted Xcode validation, and compatibility with the enabled default CodeQL setup.

## 2026-06-18

- Added a generation-owned attribution request timeout so a missing ADClient
  completion restores retry state and any late completion remains unable to
  overwrite newer work.

## 2026-06-13

- Made every Make verification target derive the checkout root so the static
  attribution baseline works from external directories.
- Kept malformed attribution responses retryable unless the required
  `Version3.1` dictionary and `iad-attribution` field are present.
- Required `iad-attribution` to decode as Boolean before completion while
  preserving both `true` and `false` as valid local-only outcomes.

## 2026-06-10

- Migrated the project setting and app launch signature from Swift 3 to Swift 5.
- Replaced the obsolete global accessibility announcement API with the Swift 5
  `UIAccessibility.post` API.
- Raised the deployment target from iOS 10 to iOS 12, the minimum supported by
  the hosted Xcode 16.4 SDK.
- Added the missing iAd framework build-phase linkage required by ADClient.
- Upgraded Xcode-enabled validation to parse the project and type-check both
  Swift sources against the iOS device SDK. Current iOS SDKs no longer provide
  a linkable ADClient implementation.
- Added pinned, read-only macOS GitHub Actions CI for the canonical `make check`
  baseline.
- Pinned Python 3.12 setup, disabled checkout credential persistence, and added
  a static guard requiring the CI workflow and completed CI plans to remain.
- Kept hosted validation from launching ADClient or handling attribution
  responses.
- Guarded attribution completion with a request generation so a stale completion
  from an earlier retry or a duplicate result cannot overwrite active state.

## 2026-06-09

- Added accessibility announcements for user-triggered attribution state changes.
- Added local `make lint`, `make test`, and `make build` gate aliases for the
  static attribution baseline.
- Added state-specific accessibility text for requesting, completed, and retry
  attribution states.
- Centralized button state updates for attribution titles, enabled state, and
  accessibility text.

## 2026-06-08

- Removed raw attribution debug logging and the sample segment update from launch handling.
- Made attribution requests user-triggered instead of running automatically during app launch.
- Moved attribution completion state and button updates onto the main queue.
- Added an in-flight disabled button title while the attribution request is running.
- Kept the attribution button disabled in the completed state after a successful request.
- Added accessibility text that describes the local-only attribution request.
- Added `make check` and a static iOS attribution baseline for plist/storyboard XML, Xcode metadata, source inventory, and privacy guardrails.
- Documented the legacy Xcode, Swift 3, ADClient, and local-only attribution response expectations.
