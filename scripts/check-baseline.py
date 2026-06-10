#!/usr/bin/env python3
from pathlib import Path
import plistlib
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
BASELINE_PLAN = ROOT / "docs/plans/2026-06-08-attribution-baseline.md"
MAKE_GATES_PLAN = ROOT / "docs/plans/2026-06-09-make-gate-aliases.md"
EXPLICIT_REQUEST_PLAN = ROOT / "docs/plans/2026-06-08-explicit-attribution-request.md"
MAIN_THREAD_PLAN = ROOT / "docs/plans/2026-06-08-main-thread-attribution-completion.md"
IN_FLIGHT_PLAN = ROOT / "docs/plans/2026-06-08-in-flight-attribution-button.md"
COMPLETED_STATE_PLAN = ROOT / "docs/plans/2026-06-09-attribution-completed-state.md"
ACCESSIBILITY_PLAN = ROOT / "docs/plans/2026-06-09-attribution-accessibility-affordance.md"
ACCESSIBILITY_STATE_PLAN = ROOT / "docs/plans/2026-06-09-attribution-accessibility-state.md"
BUTTON_STATE_HELPER_PLAN = ROOT / "docs/plans/2026-06-09-attribution-button-state-helper.md"
ACCESSIBILITY_ANNOUNCEMENT_PLAN = ROOT / "docs/plans/2026-06-09-attribution-accessibility-announcements.md"
HOSTED_VALIDATION_PLAN = ROOT / "docs/plans/2026-06-10-hosted-project-validation.md"
SWIFT_5_BUILD_PLAN = ROOT / "docs/plans/2026-06-10-swift-5-device-sdk-typecheck.md"


def require(condition, message, failures):
    if not condition:
        failures.append(message)


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


def strip_swift_line_comments(text):
    return "\n".join(line.split("//", 1)[0] for line in text.splitlines())


def swift_function_body(text, signature):
    start = text.find(signature)
    if start == -1:
        return ""

    body_start = text.find("{", start)
    if body_start == -1:
        return ""

    depth = 0
    for index in range(body_start, len(text)):
        character = text[index]
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return text[body_start + 1:index]
    return ""


def parse_xml(relative_path, failures):
    try:
        ET.parse(str(ROOT / relative_path))
    except ET.ParseError as error:
        failures.append(f"{relative_path} is not well-formed XML: {error}")


def parse_plist(relative_path, failures):
    try:
        with (ROOT / relative_path).open("rb") as file:
            return plistlib.load(file)
    except Exception as error:
        failures.append(f"{relative_path} is not a readable plist: {error}")
        return {}


def main():
    failures = []
    required_files = [
        ".gitignore",
        ".github/workflows/check.yml",
        "CHANGES.md",
        "Makefile",
        "README.md",
        "SECURITY.md",
        "VISION.md",
        "ios-search-ads-sample.xcodeproj/project.pbxproj",
        "ios-search-ads-sample.xcodeproj/project.xcworkspace/contents.xcworkspacedata",
        "ios-search-ads-sample/Info.plist",
        "ios-search-ads-sample/AppDelegate.swift",
        "ios-search-ads-sample/ViewController.swift",
        "ios-search-ads-sample/Base.lproj/Main.storyboard",
        "ios-search-ads-sample/Base.lproj/LaunchScreen.storyboard",
        "docs/readme-overview.svg",
        "docs/plans/2026-06-08-attribution-baseline.md",
        "docs/plans/2026-06-09-make-gate-aliases.md",
        "docs/plans/2026-06-08-explicit-attribution-request.md",
        "docs/plans/2026-06-08-main-thread-attribution-completion.md",
        "docs/plans/2026-06-08-in-flight-attribution-button.md",
        "docs/plans/2026-06-09-attribution-completed-state.md",
        "docs/plans/2026-06-09-attribution-accessibility-affordance.md",
        "docs/plans/2026-06-09-attribution-accessibility-state.md",
        "docs/plans/2026-06-09-attribution-button-state-helper.md",
        "docs/plans/2026-06-09-attribution-accessibility-announcements.md",
        "docs/plans/2026-06-10-hosted-project-validation.md",
        "docs/plans/2026-06-10-swift-5-device-sdk-typecheck.md",
    ]

    for relative_path in required_files:
        require((ROOT / relative_path).is_file(), f"Required file missing: {relative_path}", failures)

    for xml_file in [
        "ios-search-ads-sample.xcodeproj/project.xcworkspace/contents.xcworkspacedata",
        "ios-search-ads-sample/Base.lproj/Main.storyboard",
        "ios-search-ads-sample/Base.lproj/LaunchScreen.storyboard",
        "docs/readme-overview.svg",
    ]:
        parse_xml(xml_file, failures)

    app_plist = parse_plist("ios-search-ads-sample/Info.plist", failures)
    project = read("ios-search-ads-sample.xcodeproj/project.pbxproj")
    app_delegate = read("ios-search-ads-sample/AppDelegate.swift")
    view_controller = read("ios-search-ads-sample/ViewController.swift")
    active_app_delegate = strip_swift_line_comments(app_delegate)
    active_view_controller = strip_swift_line_comments(view_controller)
    readme = read("README.md")
    vision = read("VISION.md")
    security = read("SECURITY.md")
    changes = read("CHANGES.md")
    gitignore = read(".gitignore")
    makefile = read("Makefile")
    baseline_plan = BASELINE_PLAN.read_text(encoding="utf-8") if BASELINE_PLAN.exists() else ""
    make_gates_plan = MAKE_GATES_PLAN.read_text(encoding="utf-8") if MAKE_GATES_PLAN.exists() else ""
    explicit_request_plan = EXPLICIT_REQUEST_PLAN.read_text(encoding="utf-8") if EXPLICIT_REQUEST_PLAN.exists() else ""
    main_thread_plan = MAIN_THREAD_PLAN.read_text(encoding="utf-8") if MAIN_THREAD_PLAN.exists() else ""
    in_flight_plan = IN_FLIGHT_PLAN.read_text(encoding="utf-8") if IN_FLIGHT_PLAN.exists() else ""
    completed_state_plan = COMPLETED_STATE_PLAN.read_text(encoding="utf-8") if COMPLETED_STATE_PLAN.exists() else ""
    accessibility_plan = ACCESSIBILITY_PLAN.read_text(encoding="utf-8") if ACCESSIBILITY_PLAN.exists() else ""
    accessibility_state_plan = ACCESSIBILITY_STATE_PLAN.read_text(encoding="utf-8") if ACCESSIBILITY_STATE_PLAN.exists() else ""
    button_state_helper_plan = BUTTON_STATE_HELPER_PLAN.read_text(encoding="utf-8") if BUTTON_STATE_HELPER_PLAN.exists() else ""
    accessibility_announcement_plan = ACCESSIBILITY_ANNOUNCEMENT_PLAN.read_text(encoding="utf-8") if ACCESSIBILITY_ANNOUNCEMENT_PLAN.exists() else ""
    hosted_validation_plan = HOSTED_VALIDATION_PLAN.read_text(encoding="utf-8") if HOSTED_VALIDATION_PLAN.exists() else ""
    swift_5_build_plan = SWIFT_5_BUILD_PLAN.read_text(encoding="utf-8") if SWIFT_5_BUILD_PLAN.exists() else ""
    workflow = read(".github/workflows/check.yml")
    launch_body = swift_function_body(active_app_delegate, "func application")
    view_did_load = swift_function_body(active_view_controller, "override func viewDidLoad")
    configure_button = swift_function_body(active_view_controller, "func configureAttributionButton")
    button_state_helper = swift_function_body(active_view_controller, "func applyAttributionButtonState")
    request_action = swift_function_body(active_view_controller, "func requestAttribution")
    attribution_request_index = request_action.find("ADClient.shared().requestAttributionDetails")
    main_dispatch_index = request_action.find("DispatchQueue.main.async")
    requesting_title_index = button_state_helper.find('attributionButton.setTitle("Requesting Attribution...", for: .disabled)')
    disable_button_index = button_state_helper.find("attributionButton.isEnabled = false", requesting_title_index)

    require(app_plist.get("CFBundleIdentifier") == "$(PRODUCT_BUNDLE_IDENTIFIER)",
            "Info.plist must keep PRODUCT_BUNDLE_IDENTIFIER indirection",
            failures)
    require(app_plist.get("UILaunchStoryboardName") == "LaunchScreen" and app_plist.get("UIMainStoryboardFile") == "Main",
            "Info.plist must keep storyboard configuration",
            failures)
    require(project.count("SWIFT_VERSION = 5.0") == 2 and "SWIFT_VERSION = 3.0" not in project and
            project.count("IPHONEOS_DEPLOYMENT_TARGET = 12.0") == 2 and
            "IPHONEOS_DEPLOYMENT_TARGET = 10.0" not in project,
            "Xcode project must use Swift 5 with the iOS 12 deployment target",
            failures)
    require("[UIApplication.LaunchOptionsKey: Any]?" in active_app_delegate,
            "AppDelegate must use the Swift 5 launch-options signature",
            failures)
    require("ios-search-ads-sample/Info.plist" in project and "AppDelegate.swift in Sources" in project,
            "Xcode project must keep app plist and Swift source wiring",
            failures)
    require(project.count("iAd.framework in Frameworks") == 2 and
            "System/Library/Frameworks/iAd.framework" in project,
            "Xcode project must link the iAd framework used by ADClient",
            failures)

    require("ADClient.shared().requestAttributionDetails" not in launch_body,
            "AppDelegate must not request attribution at launch",
            failures)
    require("import iAd" in active_view_controller,
            "ViewController must keep the ADClient/iAd attribution sample import",
            failures)
    require("ADClient.shared().requestAttributionDetails" in request_action and
            active_view_controller.count("ADClient.shared().requestAttributionDetails") == 1,
            "ViewController must keep the attribution request behind the explicit action only",
            failures)
    require("configureAttributionButton()" in view_did_load and
            "ADClient.shared().requestAttributionDetails" not in view_did_load,
            "ViewController must configure UI without requesting attribution during view load",
            failures)
    require("private let attributionButton" in active_view_controller and
            "action: #selector(requestAttribution(_:))" in active_view_controller,
            "ViewController must expose an explicit user action for attribution",
            failures)
    require("private enum AttributionButtonState" in active_view_controller and
            all(f"case {state}" in active_view_controller for state in ["ready", "requesting", "retry", "completed"]) and
            "func applyAttributionButtonState" in active_view_controller,
            "ViewController must centralize attribution button states",
            failures)
    require("applyAttributionButtonState(.ready)" in configure_button,
            "ViewController must configure the initial attribution button state through the helper",
            failures)
    require('attributionButton.accessibilityLabel = "Request Attribution"' in active_view_controller and
            "attributionButton.accessibilityHint" in active_view_controller and
            "without storing results" in active_view_controller,
            "ViewController must describe the local-only attribution action for accessibility",
            failures)
    for accessibility_text in [
        "Requesting Attribution",
        "Attribution request is running locally without storing results",
        "Try Attribution Again",
        "Previous local attribution request failed; double tap to retry",
        "Attribution Requested",
        "Attribution request completed locally and the button is disabled",
    ]:
        require(accessibility_text in button_state_helper,
                f"ViewController must keep state-specific accessibility text: {accessibility_text}",
                failures)
    require("func applyAttributionButtonState(_ state: AttributionButtonState, announce: Bool = false)" in active_view_controller and
            "UIAccessibility.post(notification: .announcement, argument: attributionButton.accessibilityLabel)" in button_state_helper,
            "ViewController must announce attribution state changes to assistive technologies",
            failures)
    require(request_action.count("announce: true") >= 3 and "applyAttributionButtonState(.ready)" in configure_button,
            "ViewController must announce requesting, retry, and completed attribution states only after user-triggered changes",
            failures)
    require("private var attributionRequestInProgress = false" in active_view_controller and
            "private var attributionRequestCompleted = false" in active_view_controller and
            "attributionRequestInProgress || attributionRequestCompleted" in request_action,
            "ViewController must guard duplicate attribution requests",
            failures)
    require("attributionButton.isEnabled = false" in button_state_helper and
            "attributionButton.isEnabled = true" in button_state_helper and
            "attributionRequestCompleted = true" in request_action,
            "ViewController must disable attribution while running and re-enable it on failure",
            failures)
    require(button_state_helper.count("attributionButton.isEnabled = false") >= 2,
            "ViewController must keep the attribution button disabled after completed success",
            failures)
    require(requesting_title_index != -1 and requesting_title_index < disable_button_index,
            "ViewController must show an in-flight disabled title before disabling attribution",
            failures)
    require(request_action.count("applyAttributionButtonState(") == 3 and
            "applyAttributionButtonState(.requesting, announce: true)" in request_action and
            "applyAttributionButtonState(.retry, announce: true)" in request_action and
            "applyAttributionButtonState(.completed, announce: true)" in request_action,
            "ViewController must drive request, retry, and completed button states through the helper",
            failures)
    require("attributionButton.setTitle" not in request_action and
            "attributionButton.accessibility" not in request_action and
            "attributionButton.isEnabled" not in request_action,
            "ViewController must keep request callback button mutations centralized",
            failures)
    require(attribution_request_index != -1 and main_dispatch_index > attribution_request_index,
            "ViewController must dispatch attribution completion handling to the main queue",
            failures)
    require(main_dispatch_index != -1 and
            request_action.find("attributionRequestInProgress = false", main_dispatch_index) != -1 and
            request_action.find("applyAttributionButtonState(.retry, announce: true)", main_dispatch_index) != -1 and
            request_action.find("applyAttributionButtonState(.completed, announce: true)", main_dispatch_index) != -1 and
            request_action.find("attributionRequestCompleted = true", main_dispatch_index) != -1,
            "ViewController must keep attribution completion state and UI updates inside the main-queue block",
            failures)
    require('"Version3.1"' in request_action and '"iad-attribution"' in request_action,
            "ViewController must keep the documented attribution response lookup",
            failures)
    active_attribution_sources = active_app_delegate + "\n" + active_view_controller
    require(not re.search(r"\b(?:print|println|NSLog)\s*\(", active_attribution_sources),
            "Attribution callback must not log attribution data",
            failures)
    for forbidden in ["add(toSegments", "URLSession", "NSURLConnection", "NSURL", "http://", "https://", "upload", "UserDefaults"]:
        require(forbidden not in active_attribution_sources,
                f"App source must not add storage, network, or segment behavior for attribution data: {forbidden}",
                failures)

    swift_files = sorted((ROOT / "ios-search-ads-sample").rglob("*.swift"))
    require(len(swift_files) == 2,
            "expected Swift source inventory is missing",
            failures)
    require("*.local.xcconfig" in gitignore and ".env" in gitignore,
            ".gitignore must exclude local secret/config files",
            failures)
    require(".PHONY: build check lint test" in makefile and "lint test build: check" in makefile,
            "Makefile must expose lint, test, and build aliases for the local baseline",
            failures)
    require("make lint" in readme and "make test" in readme and "make build" in readme and "make check" in readme and "ADClient" in readme and "local-only" in readme.lower() and
            "button" in readme.lower() and "main queue" in readme.lower() and "in-flight" in readme.lower() and "completed state" in readme.lower() and "state-specific accessibility" in readme.lower() and "accessibility announcements" in readme.lower() and "centralized button state" in readme.lower(),
            "README must document static verification and local-only, user-triggered ADClient handling",
            failures)
    require("scripts/check-baseline.py" in vision and "make lint" in vision and "make test" in vision and "make build" in vision and "local-only" in vision.lower() and
            "main queue" in vision.lower() and "in-flight" in vision.lower() and "completed state" in vision.lower() and "state-specific accessibility" in vision.lower() and "accessibility announcements" in vision.lower() and "centralized button state" in vision.lower(),
            "VISION must describe the current static privacy baseline",
            failures)
    require("attribution" in security.lower() and "make check" in security and "in-flight" in security.lower() and "completed state" in security.lower() and "state-specific accessibility" in security.lower() and "accessibility announcements" in security.lower() and "centralized button state" in security.lower(),
            "SECURITY must document attribution privacy and the static baseline",
            failures)
    require("debug logging" in changes and "segment" in changes and "make check" in changes and "make lint" in changes and "make test" in changes and "make build" in changes and
            "user-triggered" in changes and "main queue" in changes and "in-flight" in changes.lower() and "completed state" in changes.lower() and "state-specific accessibility" in changes.lower() and "accessibility announcements" in changes.lower() and "centralized button state" in changes.lower(),
            "CHANGES must record logging, segment, user-triggered attribution, in-flight UI, main-queue completion, and baseline updates",
            failures)
    require("status: completed" in baseline_plan and "status: completed" in explicit_request_plan and
            "status: completed" in main_thread_plan and "status: completed" in in_flight_plan,
            "plans must be marked completed",
            failures)
    require("status: completed" in make_gates_plan,
            "make gate aliases plan must be marked completed",
            failures)
    require("status: completed" in completed_state_plan,
            "attribution completed state plan must be marked completed",
            failures)
    require("status: completed" in accessibility_plan,
            "attribution accessibility affordance plan must be marked completed",
            failures)
    require("status: completed" in accessibility_state_plan,
            "attribution accessibility state plan must be marked completed",
            failures)
    require("status: completed" in button_state_helper_plan,
            "attribution button state helper plan must be marked completed",
            failures)
    require("status: completed" in accessibility_announcement_plan,
            "attribution accessibility announcements plan must be marked completed",
            failures)
    require("status: completed" in hosted_validation_plan and "make check" in hosted_validation_plan,
            "hosted project validation plan must be completed and document make check",
            failures)
    require("status: completed" in swift_5_build_plan and "device sdk" in swift_5_build_plan.lower(),
            "Swift 5 build plan must be completed and document device SDK verification",
            failures)
    require("permissions:\n  contents: read" in workflow,
            "Check workflow must use read-only repository permissions",
            failures)
    require("cancel-in-progress: true" in workflow and "runs-on: macos-15" in workflow and
            "timeout-minutes: 10" in workflow,
            "Check workflow must bound duplicate and long-running macOS jobs",
            failures)
    require("actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10" in workflow and
            "run: make check" in workflow,
            "Check workflow must pin checkout and run the canonical baseline",
            failures)

    if shutil.which("xcodebuild"):
        project_result = subprocess.run(
            ["xcodebuild", "-list", "-project", "ios-search-ads-sample.xcodeproj"],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        require(project_result.returncode == 0,
                "xcodebuild could not parse ios-search-ads-sample.xcodeproj: " + project_result.stdout.strip(),
                failures)

        sdk_result = subprocess.run(
            ["xcrun", "--sdk", "iphoneos", "--show-sdk-path"],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        require(sdk_result.returncode == 0,
                "xcrun could not locate the iOS device SDK: " + sdk_result.stdout.strip(),
                failures)
        if sdk_result.returncode == 0:
            typecheck_result = subprocess.run(
                [
                    "xcrun", "--sdk", "iphoneos", "swiftc",
                    "-typecheck",
                    "-swift-version", "5",
                    "-target", "arm64-apple-ios12.0",
                    "-sdk", sdk_result.stdout.strip(),
                    "ios-search-ads-sample/AppDelegate.swift",
                    "ios-search-ads-sample/ViewController.swift",
                ],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            require(typecheck_result.returncode == 0,
                    "swiftc could not type-check the app against the iOS device SDK: " + typecheck_result.stdout.strip(),
                    failures)
    else:
        print("xcodebuild unavailable; static iOS baseline only.")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("ios search attribution baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
