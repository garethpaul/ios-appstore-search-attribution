# Changes

## 2026-06-27 - P2 - Reject synchronously terminal startup work

### Summary
The request coordinator now rechecks generation and requesting state after
timeout scheduling and request construction, cancelling returned handles when a
synchronous callback has already made that startup terminal.

### Work completed
- Prevented request startup after a scheduler fires the timeout synchronously.
- Cancelled request handles returned after synchronous client completion.
- Added native XCTest cases for both callback orderings.
- Added portable source contracts and hostile guard-removal mutations.
- Coordinator startup rejects and cancels timeout or request handles returned after a synchronous terminal callback.

### Validation
- The new native cases were added first; local execution is unavailable because
  this host does not provide Xcode.
- The portable baseline failed before the coordinator ownership guards existed.
- All 37 Python security and mutation tests pass after implementation.
- Both timeout-guard and request-guard removal mutations are rejected.
- Hosted baseline run `28273664039` passed native XCTest and unsigned project
  validation, while CodeQL run `28273663245` and default code scanning passed
  on the implementation head before this evidence-only documentation amend.
- `codex review --base master` was attempted on the implementation head but
  stopped before analysis because the OpenAI API returned HTTP 401; immutable
  manual review of the exact diff found no actionable issues.

### Bugs / findings
- P2: protocol-conforming synchronous schedulers or clients could previously
  start a request after timeout or leave a terminal request handle uncancelled.

### Next action
- Re-run the required review attempt and merge only after the replacement
  evidence-only pull-request head passes hosted checks.

## 2026-06-26 - P1 - Resume only operation-owned attribution tasks

### Summary
Attribution URLSession tasks now start only after the request operation accepts
exact ownership, closing a cancellation race that could resume rejected work.

### Work completed
- Changed task activation into a Boolean ownership handshake.
- Kept rejected sessions invalidated and returned before `task.resume()`.
- Added a portable ordering contract, hostile mutation regression, and
  completed design record.

### Validation
- Test-first portable baseline reproduced the missing ownership handshake.
- Focused unconditional-resume mutation was rejected after the fix.
- Root, external-directory, and hosted canonical checks are required.

### Bugs / findings
- P1: cancellation could reject a newly created attribution session while the
  caller still resumed its task without an active operation owner.

## 2026-06-25 08:28 PDT - P1 - Keep attribution tokens on Apple's endpoint

### Summary
Attribution requests now reject every HTTP redirect so URLSession cannot forward the short-lived token to another origin.

### Work completed
- Added mocked URLProtocol coverage for a `307` redirect to a non-Apple origin.
- Added a deterministic token-bearing redirect-policy XCTest and delegate-owned rejection.
- Added portable source contracts, a hostile mutation, and maintained privacy documentation.

### Threads
- None; work completed directly in this maintenance cycle.

### Files changed
- `AttributionClient.swift` and native XCTest — redirect ownership and regression coverage.
- `scripts/`, `tests/`, maintained docs, and `docs/plans/` — portable policy and evidence.

### Validation
- Portable baseline before implementation — failed because redirect rejection was absent.
- Root and external-directory portable baseline plus 35 Python tests — passed.
- Hostile redirect-following mutation — rejected by the portable baseline suite.
- Full local `make check` — reached the documented native-test boundary and stopped because Xcode is unavailable.
- First hosted native XCTest — exposed that URLProtocol redirect simulation never completed the task; replaced with a direct policy test.
- Updated hosted native XCTest and unsigned simulator build — passed on the exact PR head after replacing the incomplete URLProtocol harness.
- CodeQL for Actions and Python — passed.

### Bugs / findings
- P1: default URLSession redirect handling could move the attribution POST beyond Apple's fixed endpoint.

### Blockers
- None; hosted Xcode verification is available on the PR.

### Next action
- Merge the exact reviewed head, persist repository intelligence, and continue to the next unexplored project.

## 2026-06-21

- Made the portable attribution baseline explicitly skip Xcode project parsing
  when `xcodebuild` is unavailable while keeping full native XCTest mandatory.
- Added a regression proving Linux lint does not attempt an unavailable Xcode
  subprocess while hosted macOS remains responsible for full `make check`.

## 2026-06-19

- Replaced the retired iAd callback with the current AdServices token and Apple
  attribution REST flow while retaining safe unsupported behavior before iOS 14.3.
- Added an ephemeral, credential-free URL session with fixed endpoint ownership,
  10-second request and 20-second resource timeouts, and a streamed 64 KiB cap.
- Added strict JSON/MIME/status/Boolean validation, fixed 404 intervals, bounded
  500 backoff, and three total attempts.
- Added generation-owned cancellation across timeout, navigation, backgrounding,
  duplicate starts, and late completions without caching, persistence, or logging.
- Added native XCTest with mocked networking, location-independent Make gates,
  hosted Xcode validation, and compatibility with the enabled default CodeQL setup.

## 2026-06-18

- Added a generation-owned attribution request timeout so a missing ADClient
  completion restores retry state and any late completion remains unable to
  overwrite newer work.

## 2026-06-13

- Made every Make verification target derive the checkout root so the static
  attribution baseline works from external directories.
- Kept malformed attribution responses retryable unless the required
  `Version3.1` dictionary and `iad-attribution` field are present.
- Required `iad-attribution` to decode as Boolean before completion while
  preserving both `true` and `false` as valid local-only outcomes.

## 2026-06-10

- Migrated the project setting and app launch signature from Swift 3 to Swift 5.
- Replaced the obsolete global accessibility announcement API with the Swift 5
  `UIAccessibility.post` API.
- Raised the deployment target from iOS 10 to iOS 12, the minimum supported by
  the hosted Xcode 16.4 SDK.
- Added the missing iAd framework build-phase linkage required by ADClient.
- Upgraded Xcode-enabled validation to parse the project and type-check both
  Swift sources against the iOS device SDK. Current iOS SDKs no longer provide
  a linkable ADClient implementation.
- Added pinned, read-only macOS GitHub Actions CI for the canonical `make check`
  baseline.
- Pinned Python 3.12 setup, disabled checkout credential persistence, and added
  a static guard requiring the CI workflow and completed CI plans to remain.
- Kept hosted validation from launching ADClient or handling attribution
  responses.
- Guarded attribution completion with a request generation so a stale completion
  from an earlier retry or a duplicate result cannot overwrite active state.

## 2026-06-09

- Added accessibility announcements for user-triggered attribution state changes.
- Added local `make lint`, `make test`, and `make build` gate aliases for the
  static attribution baseline.
- Added state-specific accessibility text for requesting, completed, and retry
  attribution states.
- Centralized button state updates for attribution titles, enabled state, and
  accessibility text.

## 2026-06-08

- Removed raw attribution debug logging and the sample segment update from launch handling.
- Made attribution requests user-triggered instead of running automatically during app launch.
- Moved attribution completion state and button updates onto the main queue.
- Added an in-flight disabled button title while the attribution request is running.
- Kept the attribution button disabled in the completed state after a successful request.
- Added accessibility text that describes the local-only attribution request.
- Added `make check` and a static iOS attribution baseline for plist/storyboard XML, Xcode metadata, source inventory, and privacy guardrails.
- Documented the legacy Xcode, Swift 3, ADClient, and local-only attribution response expectations.
