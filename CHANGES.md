# Changes

## 2026-06-09

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
