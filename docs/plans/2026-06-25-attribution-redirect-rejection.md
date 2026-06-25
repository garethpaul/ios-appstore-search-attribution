# Attribution Redirect Rejection

## Status: Completed

## Problem

The attribution client owns a single fixed Apple endpoint but URLSession follows
HTTP redirects by default. A redirect response could therefore move the POST,
including the short-lived attribution token, to a different origin.

## Design

- Reject every HTTP redirect at the URLSession task-delegate boundary.
- Route every proposed redirect through a deterministic policy that returns no request.
- Keep the endpoint fixed rather than adding a general-purpose same-origin
  redirect allowlist.
- Preserve ephemeral configuration, bounds, retries, cancellation, and local-only handling.

## Test-First Evidence

- RED: the portable baseline failed because no redirect delegate or nil redirect completion existed.
- GREEN: source contracts require delegate wiring and a native XCTest verifies a token-bearing redirected request is rejected.

## Verification

- Root and external-directory portable baselines plus 35 Python tests pass locally.
- A hostile mutation that follows the redirect is rejected by the portable baseline.
- The first hosted URLProtocol redirect simulation timed out without completing; the replacement test directly exercises the policy without a mock-loader lifecycle dependency.
- Native XCTest and the unsigned simulator build passed on hosted macOS after the deterministic policy-test correction.
- No real attribution token was generated and no live Apple request was made.
