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
- Maintain the small sample project structure

Next priorities:

- Add Xcode/iOS version and framework availability notes
- Add manual verification steps for attribution response handling
- Modernize Swift/project settings in a dedicated pass
- Document privacy expectations for attribution data

Contribution rules:

- One PR = one focused attribution, build, or documentation change.
- Verify behavior on a compatible iOS environment when changing the request.
- Keep signing files and generated build products out of git.
- Document any data storage or logging change.

## Security And Privacy

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Attribution responses can involve device and campaign information. Do not log,
store, or transmit attribution data beyond the sample's explicit purpose.

## What We Will Not Merge (For Now)

- Collection of attribution data without privacy notes
- Private campaign or account data
- Broad project migration bundled with attribution behavior changes
- Generated signing material

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
