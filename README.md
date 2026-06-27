# ios-appstore-search-attribution

Small iOS sample for explicitly requesting Apple Ads attribution without logging or persisting the token or response.

## Current Flow

- The user taps **Request Attribution**; the app never requests attribution at launch.
- `AAAttribution.attributionToken()` produces the short-lived token on iOS 14.3 or later.
- An ephemeral `URLSession` posts that token to `https://api-adservices.apple.com/api/v1/` as `text/plain` and accepts only a `200` JSON response.
- Every HTTP redirect is rejected so the token is never forwarded beyond Apple's fixed endpoint.
- The response body is streamed with a 64 KiB limit and decoded with a strict Boolean `attribution` field. Numeric and string lookalikes are rejected.
- A `404` retries at Apple’s documented five-second interval. A `500` uses bounded 5- then 10-second backoff. Both stop after three total attempts.
- Tokens and attribution records remain memory-only, are not persisted or cached, and are never printed.

The request coordinator owns one active request, a 30-second UI deadline, generation invalidation, duplicate-completion rejection, and lifecycle cancellation. A URLSession task starts only after its request operation accepts exact ownership. Leaving the screen, backgrounding the app, or timing out cancels active work and prevents rejected or late callbacks from changing the UI.

Coordinator startup rejects and cancels timeout or request handles returned after a synchronous terminal callback.

## Requirements

- Xcode with an available iPhone simulator
- Python 3
- iOS 14.3 or later for a live AdServices token; the project retains an iOS 12 deployment target so older systems fail safely as unsupported

## Verification

```bash
make lint   # static architecture and policy checks
make test   # native XCTest with mocked URLProtocol networking
make build  # unsigned simulator build
make check  # static checks plus XCTest
```

All Make targets derive the repository root, so an absolute Makefile path can be
invoked from another working directory, including checkout paths containing
spaces. XCTest covers request construction, redirect rejection, strict schema
parsing, status/MIME/size rejection, retry exhaustion and backoff,
cancellation, timeouts, stale completions, duplicate starts, and main-thread UI
state ownership. Tests make no live Apple network calls.

On hosts without Xcode, `make lint` runs the portable policy baseline and reports
the skipped project parse explicitly. Full `make check` still requires Xcode and
an available iPhone simulator for native XCTest.

GitHub Actions runs `make check` on macOS. The repository's enabled GitHub
default CodeQL setup provides hosted code scanning without a conflicting
advanced-configuration workflow.

## Live Validation

Live attribution cannot be proven in the simulator. Use a signed App Store-distributed build on a physical device, with a real Apple Ads campaign and Apple’s propagation window. Do not add token, payload, campaign, or device logging when diagnosing live behavior.
