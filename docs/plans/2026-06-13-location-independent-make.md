# Location-Independent Attribution Verification

status: completed

## Context

Absolute Makefile invocations resolve the checker relative to the caller. GNU
Make also splits a loaded absolute Makefile path containing spaces before
deriving the checkout root.

## Scope

1. Derive the checkout root from an encoded `MAKEFILE_LIST` that preserves spaces.
2. Invoke the Python checker through its rooted path.
3. Add completed-plan, external-run, recursive spaced-path, guidance, and mutation contracts.
4. Preserve attribution behavior, Swift source, tests, project, and workflow files.

## Verification Plan

- Run all four Make gates from the checkout and a temporary directory.
- Run checker compilation, project metadata parsing, and diff checks.
- Reject root, checker, plan status/evidence, and documentation mutations.
- Inspect intended paths, secrets, and generated artifacts.

## Work Completed

- Derived the checkout root from the loaded Makefile and invoked the checker through its absolute path.
- Added a recursive-safe static-baseline regression against a copied checkout
  whose absolute path contains spaces without recursively duplicating XCTest.
- Added rooted invocation, completed-plan evidence, and synchronized guidance.
- Preserved attribution behavior, Swift source, tests, project, and workflow files.

## Verification Completed

- Root and external-directory Make gates passed for all four aliases.
- GNU Make 4.2 and 4.4 space-containing absolute Makefile paths passed.
- The root-derivation mutation failed.
- The checker-invocation mutation failed.
- The plan-status mutation failed.
- The plan-evidence mutation failed.
- The documentation mutation failed.
- Checker compilation, project metadata parsing, diff hygiene, intended-path
  review, secret scanning, and artifact inspection passed.

## Risk And Rollback

Verification path resolution only; rollback restores the relative recipe.
