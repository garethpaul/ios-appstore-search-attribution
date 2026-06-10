# Changes

## 2026-06-10

- Migrated the project setting and app launch signature from Swift 3 to Swift 5.
- Replaced the obsolete global accessibility announcement API with the Swift 5
  `UIAccessibility.post` API.
- Raised the deployment target from iOS 10 to iOS 12, the minimum supported by
  the hosted Xcode 16.4 simulator SDK.
- Upgraded Xcode-enabled validation from project parsing to an unsigned iOS
  Simulator build.
- Added pinned, read-only macOS CI for the canonical `make check` baseline.
- Kept hosted validation from launching ADClient or handling attribution
  responses.

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
