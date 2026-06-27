# AGENTS.md

## Repository purpose

`garethpaul/ios-appstore-search-attribution` is an Apple platform application or Swift sample. iOS Appstore Search Attribution Sample App

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `ios-search-ads-sample.xcodeproj` - Xcode project
- `ios-search-ads-sample` - repository source or sample assets

## Development commands

- Install dependencies: no repository-specific install command is documented.
- Full baseline: `make check`
- Local Apple development: `open ios-search-ads-sample.xcodeproj`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: Swift (2).
- Preserve legacy Xcode project settings and signing assumptions unless the change is explicitly about modernization.

## Testing guidance

- No dedicated test files were detected; treat `make check` as the minimum baseline.
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.
- Attribution responses can contain sensitive device and campaign context. Keep attribution response handling local-only, user-triggered, and documented.
- Reject every attribution HTTP redirect so the token stays bound to Apple's fixed endpoint.
- Keep attribution button state-specific accessibility text aligned with the local-only privacy boundary through the centralized button state helper.
- Keep attribution completion generation-guarded so stale retry completions
  cannot overwrite active request state.
- Keep attribution request timeout work weakly captured and generation-owned;
  cancel it before accepted terminal state and reuse the centralized retry path.
- Resume URLSession tasks only after `RequestOperation` accepts exact session,
  task, and delegate ownership; rejected activation must remain unresumed.
- Coordinator startup rejects and cancels timeout or request handles returned after a synchronous terminal callback.
- This looks like an Apple platform project or sample. Xcode, Swift, CocoaPods, and deployment target versions may need to match the original project era.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
