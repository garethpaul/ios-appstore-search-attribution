# Attribution Completed State

status: completed

## Context

The attribution button is disabled while `ADClient` is requesting attribution
and is re-enabled on failure so the user can retry. The success callback should
also explicitly keep the button disabled when attribution is completed, avoiding
a misleading retryable control if callbacks arrive in an unexpected order.

## Objectives

- Disable the attribution button when the success callback marks attribution
  completed.
- Preserve retry behavior on attribution failure.
- Extend the static baseline to require the completed-state button guard.
- Document the completed state alongside the in-flight attribution UI guard.

## Verification

- `make check`
- `git diff --check`
