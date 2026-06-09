# In-Flight Attribution Button Plan

status: completed

## Context

The sample disables the attribution button while `ADClient` is requesting Search
Ads attribution. A disabled control without an explicit in-flight title can look
like a permanently unavailable action instead of a running request.

## Objectives

- Set a disabled-state title before disabling the attribution button.
- Keep duplicate-request, retry, success, and local-only attribution behavior unchanged.
- Extend the static baseline so the in-flight title is checked with the existing
  user-triggered request flow.
- Document the in-flight state alongside the existing attribution privacy and UI
  guardrails.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
