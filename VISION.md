# Vision

Keep this repository a small, privacy-preserving reference for current Apple Ads attribution.

Changes should preserve these ownership boundaries:

- `AdServicesAttributionClient` owns token generation, the fixed Apple endpoint, private session configuration, response bounds, strict decoding, and bounded retry policy.
- `AttributionRequestCoordinator` owns one active request, timeout, cancellation, generation checks, and terminal state.
- `ViewController` owns user intent, lifecycle transitions, accessibility, and main-thread rendering only.

Do not add attribution persistence, general-purpose endpoints, analytics forwarding, response logging, hidden launch requests, or live-network tests. Keep `make check`, native XCTest, hosted Xcode, and Swift CodeQL green. A broader UI or architecture migration should be separate from attribution correctness changes.
