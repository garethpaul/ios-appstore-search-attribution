## iOS App Store Search Attribution Vision

This document explains the current state and direction of the project.
Project overview and developer docs: [`README.md`](README.md)

iOS App Store Search Attribution is a Swift sample showing how to request Apple
Search Ads attribution data through `ADClient`.

The repository is useful as a compact iOS attribution sample with the documented
Apple endpoint and a small Xcode project. Project context lives in
[`README.md`](README.md).

The goal is to keep the attribution request flow clear, privacy-conscious, and
aligned with Apple's APIs.

The current focus is:

Priority:

- Preserve the ADClient attribution request example
- Keep Apple's endpoint and request type documented
- Avoid storing attribution responses or device identifiers unnecessarily
- Keep attribution requests user-triggered rather than automatic on launch
- Show a clear in-flight button state while attribution is being requested
- Keep attribution completion UI state changes on the main queue
- Keep attribution button state-specific accessibility text aligned with local-only behavior
- Keep accessibility announcements aligned with user-triggered attribution state
  changes
- Keep the centralized button state helper as the source of truth for attribution
  titles, enabled state, and accessibility text
- Ignore a stale completion from an earlier retry or duplicate terminal result
- Keep malformed attribution response payloads retryable and local-only
- Maintain the small sample project structure
- Keep `scripts/check-baseline.py` passing for local-only attribution handling,
  Swift/Xcode metadata, source inventory, and privacy guardrails
- Keep `make lint`, `make test`, `make build`, and `make check` available as
  local verification gates
- Keep the project on Swift 5 with the oldest deployment target supported by
  the hosted Xcode SDK
- Keep pinned, credential-free macOS GitHub Actions CI on Python 3.12, parsing
  the project and type-checking Swift against the device SDK through the
  canonical `make check` gate

Next priorities:

- Add manual verification steps for attribution response handling
- Evaluate migration from deprecated ADClient separately from build-toolchain
  maintenance
- Document privacy expectations for attribution data

Contribution rules:

- One PR = one focused attribution, build, or documentation change.
- Verify behavior on a compatible iOS environment when changing the request.
- Keep signing files and generated build products out of git.
- Keep `.github/workflows/check.yml` aligned with the static attribution,
  project parsing, and device-SDK type-checking baseline.
- Document any data storage or logging change.

## Security And Privacy

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Attribution responses can involve device and campaign information. Do not log,
store, or transmit attribution data beyond the sample's explicit purpose.

Current baseline: `make lint`, `make test`, `make build`, and `make check` run
`scripts/check-baseline.py` without Xcode. It verifies the ADClient request
flow, Swift 5/iOS 12 project context, plist/storyboard XML, source inventory,
and local-only attribution guardrails. It also verifies that attribution remains
behind an explicit user action, is not requested from app launch or view-load
code, shows an in-flight disabled button title, keeps the completed state
disabled, and updates completion UI state on the main queue. State-specific
accessibility text should describe the local-only attribution action across
requesting, completed, and retry states through the centralized button state
helper.
Accessibility announcements should describe user-triggered attribution state
changes for requesting, completed, and retry states.
Only the active in-progress request generation should apply completion state, so
a stale completion cannot overwrite a newer retry.
A malformed attribution response should not enter completed state unless the
required version dictionary and attribution field are present.
On macOS, the baseline should parse the project and type-check both Swift files
against the current device SDK without launching the app or invoking ADClient.
Current iOS SDKs no longer provide a linkable ADClient implementation, so full
runtime/link verification requires an older compatible SDK or a separate
AdServices migration. Successful type-checking does not prove the service works.

## What We Will Not Merge (For Now)

- Collection of attribution data without privacy notes
- Private campaign or account data
- Broad project migration bundled with attribution behavior changes
- Generated signing material

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
