# Synchronous Startup Ownership

## Problem

`AttributionRequestCoordinator.start()` assigned timeout and request handles
after invoking abstractions that are permitted to call back synchronously. A
synchronous timeout could make the generation terminal before the request was
created, yet startup continued. A synchronous client completion could finish
the request before its returned cancellable was assigned, leaving that handle
outside coordinator ownership.

## Decision

After each startup abstraction returns, recheck that the same generation still
owns the `.requesting` state. Cancel the returned handle and stop when a
synchronous callback has already completed, timed out, or cancelled the
generation. Assign only handles that the active generation still owns.

## Verification

- Native XCTest models a scheduler that fires inline and requires zero client
  requests after the resulting timeout.
- Native XCTest models a client that completes inline and requires its returned
  request handle to be cancelled.
- The portable baseline requires both ownership checks and both XCTest names.
- Hostile mutations remove each guard independently and must fail the canonical
  portable gate.

## Result

Coordinator startup rejects and cancels timeout or request handles returned after a synchronous terminal callback.
