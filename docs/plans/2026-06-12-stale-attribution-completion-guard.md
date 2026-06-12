# Stale Attribution Completion Guard

status: completed

## Context

Search Ads attribution completion is asynchronous. After a failed request
re-enables the button, a retry can begin while delayed or duplicate completion
work from the previous request is still queued on the main thread. That stale
work can mark the retry complete or switch its button back to the retry state.

## Work Completed

- Assign a monotonically increasing generation to each attribution request.
- Capture the generation in the completion and accept it only while that same
  request remains active.
- Preserve weak controller capture, main-queue UI changes, local-only response
  handling, and existing ready/requesting/retry/completed states.
- Extend the static baseline with generation and in-progress guard contracts.

## Verification Completed

- Local `make check`, `make lint`, `make test`, and `make build` passed. The
  local environment did not provide `xcodebuild`, so these runs exercised the
  complete static baseline and reported the hosted Xcode requirement.
- `python3 -m py_compile scripts/check-baseline.py` and `git diff --check`
  passed.
- Hostile mutations changing the plan status, inserting an unfinished-work
  marker, falsifying a run ID, removing the generation comparison, or removing
  the active-request guard were rejected by the baseline.
- The implementation push Check run `27394447779` completed successfully for
  commit `fb6e802113e5afc388123c0f66260a4965e573f9`.
- The implementation pull-request Check run `27394453676` completed
  successfully for commit `fb6e802113e5afc388123c0f66260a4965e573f9` and
  ran the hosted macOS project validation and Swift 5 device-SDK type-check.
- The post-merge Check run `27394475807` completed successfully for commit
  `680f82901bd475b9ec441b41ee10c6f493975e51`.
- The CodeQL setup run `27402322779` completed successfully for commit
  `680f82901bd475b9ec441b41ee10c6f493975e51`.
- The checker preserves both completion predicates:
  `requestGeneration == strongSelf.attributionRequestGeneration` and
  `strongSelf.attributionRequestInProgress else`.
