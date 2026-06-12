# Stale Attribution Completion Guard

status: completed

## Context

Search Ads attribution completion is asynchronous. After a failed request
re-enables the button, a retry can begin while delayed or duplicate completion
work from the previous request is still queued on the main thread. That stale
work can mark the retry complete or switch its button back to the retry state.

## Completed Scope

- Assign a monotonically increasing generation to each attribution request.
- Capture the generation in the completion and accept it only while that same
  request remains active.
- Preserve weak controller capture, main-queue UI changes, local-only response
  handling, and existing ready/requesting/retry/completed states.
- Extend the static baseline with generation and in-progress guard contracts.

## Verification

- `make check`
- `git diff --check`
- Mutations removing either guard condition must fail the baseline.
- Hosted macOS validation must build the Swift 5 sample for the device SDK.
