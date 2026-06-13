# Location-Independent Attribution Verification

status: completed

## Context

Absolute Makefile invocations resolve the checker relative to the caller.

## Scope

1. Derive the checkout root from `MAKEFILE_LIST`.
2. Invoke the Python checker through its rooted path.
3. Add completed-plan, external-run, guidance, and mutation contracts.
4. Preserve attribution behavior, Swift source, tests, project, and workflow files.

## Verification Plan

- Run all four Make gates from the checkout and a temporary directory.
- Run checker compilation, project metadata parsing, and diff checks.
- Reject root, checker, plan status/evidence, and documentation mutations.
- Inspect intended paths, secrets, and generated artifacts.

## Work Completed

- Derived the checkout root from the loaded Makefile and invoked the checker through its absolute path.
- Added rooted invocation, completed-plan evidence, and synchronized guidance.
- Preserved attribution behavior, Swift source, tests, project, and workflow files.

## Verification Completed

- Root and external-directory Make gates passed for all four aliases.
- The root-derivation mutation failed.
- The checker-invocation mutation failed.
- The plan-status mutation failed.
- The plan-evidence mutation failed.
- The documentation mutation failed.
- Checker compilation, project metadata parsing, diff hygiene, intended-path
  review, secret scanning, and artifact inspection passed.

## Risk And Rollback

Verification path resolution only; rollback restores the relative recipe.
