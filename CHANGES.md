# Changes

## 2026-06-08

- Removed raw attribution debug logging and the sample segment update from launch handling.
- Made attribution requests user-triggered instead of running automatically during app launch.
- Moved attribution completion state and button updates onto the main queue.
- Added an in-flight disabled button title while the attribution request is running.
- Added `make check` and a static iOS attribution baseline for plist/storyboard XML, Xcode metadata, source inventory, and privacy guardrails.
- Documented the legacy Xcode, Swift 3, ADClient, and local-only attribution response expectations.
