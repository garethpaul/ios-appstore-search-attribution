# Attribution Task Activation Ownership

Status: Completed

## Problem

Cancellation can race with creation of a retry or initial URLSession task. The
request operation already rejected and invalidated a session when it no longer
owned a completion, but `startAttempt` resumed the task unconditionally after
that rejection. A canceled attribution request could therefore start transport
work that no active operation owned.

## Decision

- Make `RequestOperation.setActive` return whether it accepted exact ownership
  of the session, task, and delegate.
- Return `false` after invalidating a session rejected because cancellation or a
  terminal completion already won.
- Resume a task only after activation returns `true`.
- Preserve the existing cancellation path for a task accepted immediately before
  cancellation; cancellation still owns and cancels that exact task.

## Verification

- The portable source gate requires the Boolean activation handshake and
  accepted-ownership guard before `task.resume()`.
- A Python regression mutates the guard back to unconditional activation and
  proves the baseline rejects it.
- Root and external-directory portable gates plus hosted `make check` are
  required before merge.
