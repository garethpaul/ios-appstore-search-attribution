#!/usr/bin/env python3
from pathlib import Path
import plistlib
import re
import shutil
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
BASELINE_PLAN = ROOT / "docs/plans/2026-06-08-attribution-baseline.md"
EXPLICIT_REQUEST_PLAN = ROOT / "docs/plans/2026-06-08-explicit-attribution-request.md"
MAIN_THREAD_PLAN = ROOT / "docs/plans/2026-06-08-main-thread-attribution-completion.md"
IN_FLIGHT_PLAN = ROOT / "docs/plans/2026-06-08-in-flight-attribution-button.md"
COMPLETED_STATE_PLAN = ROOT / "docs/plans/2026-06-09-attribution-completed-state.md"
ACCESSIBILITY_PLAN = ROOT / "docs/plans/2026-06-09-attribution-accessibility-affordance.md"
ACCESSIBILITY_STATE_PLAN = ROOT / "docs/plans/2026-06-09-attribution-accessibility-state.md"


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
        "docs/plans/2026-06-08-explicit-attribution-request.md",
        "docs/plans/2026-06-08-main-thread-attribution-completion.md",
        "docs/plans/2026-06-08-in-flight-attribution-button.md",
        "docs/plans/2026-06-09-attribution-completed-state.md",
        "docs/plans/2026-06-09-attribution-accessibility-affordance.md",
        "docs/plans/2026-06-09-attribution-accessibility-state.md",
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
    baseline_plan = BASELINE_PLAN.read_text(encoding="utf-8") if BASELINE_PLAN.exists() else ""
    explicit_request_plan = EXPLICIT_REQUEST_PLAN.read_text(encoding="utf-8") if EXPLICIT_REQUEST_PLAN.exists() else ""
    main_thread_plan = MAIN_THREAD_PLAN.read_text(encoding="utf-8") if MAIN_THREAD_PLAN.exists() else ""
    in_flight_plan = IN_FLIGHT_PLAN.read_text(encoding="utf-8") if IN_FLIGHT_PLAN.exists() else ""
    completed_state_plan = COMPLETED_STATE_PLAN.read_text(encoding="utf-8") if COMPLETED_STATE_PLAN.exists() else ""
    accessibility_plan = ACCESSIBILITY_PLAN.read_text(encoding="utf-8") if ACCESSIBILITY_PLAN.exists() else ""
    accessibility_state_plan = ACCESSIBILITY_STATE_PLAN.read_text(encoding="utf-8") if ACCESSIBILITY_STATE_PLAN.exists() else ""
    launch_body = swift_function_body(active_app_delegate, "func application")
    view_did_load = swift_function_body(active_view_controller, "override func viewDidLoad")
    request_action = swift_function_body(active_view_controller, "func requestAttribution")
    attribution_request_index = request_action.find("ADClient.shared().requestAttributionDetails")
    main_dispatch_index = request_action.find("DispatchQueue.main.async")
    requesting_title_index = request_action.find('attributionButton.setTitle("Requesting Attribution...", for: .disabled)')
    disable_button_index = request_action.find("attributionButton.isEnabled = false")

    require(app_plist.get("CFBundleIdentifier") == "$(PRODUCT_BUNDLE_IDENTIFIER)",
            "Info.plist must keep PRODUCT_BUNDLE_IDENTIFIER indirection",
            failures)
    require(app_plist.get("UILaunchStoryboardName") == "LaunchScreen" and app_plist.get("UIMainStoryboardFile") == "Main",
            "Info.plist must keep storyboard configuration",
            failures)
    require("SWIFT_VERSION = 3.0" in project and "IPHONEOS_DEPLOYMENT_TARGET = 10.0" in project,
            "Xcode project must keep the Swift 3 / iOS 10 sample context",
            failures)
    require("ios-search-ads-sample/Info.plist" in project and "AppDelegate.swift in Sources" in project,
            "Xcode project must keep app plist and Swift source wiring",
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
        require(accessibility_text in request_action,
                f"ViewController must keep state-specific accessibility text: {accessibility_text}",
                failures)
    require("private var attributionRequestInProgress = false" in active_view_controller and
            "private var attributionRequestCompleted = false" in active_view_controller and
            "attributionRequestInProgress || attributionRequestCompleted" in request_action,
            "ViewController must guard duplicate attribution requests",
            failures)
    require("attributionButton.isEnabled = false" in request_action and
            "attributionButton.isEnabled = true" in request_action and
            "attributionRequestCompleted = true" in request_action,
            "ViewController must disable attribution while running and re-enable it on failure",
            failures)
    require(request_action.count("attributionButton.isEnabled = false") >= 2,
            "ViewController must keep the attribution button disabled after completed success",
            failures)
    require(requesting_title_index != -1 and requesting_title_index < disable_button_index,
            "ViewController must show an in-flight disabled title before disabling attribution",
            failures)
    require(attribution_request_index != -1 and main_dispatch_index > attribution_request_index,
            "ViewController must dispatch attribution completion handling to the main queue",
            failures)
    require(main_dispatch_index != -1 and
            request_action.find("attributionRequestInProgress = false", main_dispatch_index) != -1 and
            request_action.find("attributionButton.setTitle", main_dispatch_index) != -1 and
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
    require("make check" in readme and "ADClient" in readme and "local-only" in readme.lower() and
            "button" in readme.lower() and "main queue" in readme.lower() and "in-flight" in readme.lower() and "completed state" in readme.lower() and "state-specific accessibility" in readme.lower(),
            "README must document static verification and local-only, user-triggered ADClient handling",
            failures)
    require("scripts/check-baseline.py" in vision and "local-only" in vision.lower() and
            "main queue" in vision.lower() and "in-flight" in vision.lower() and "completed state" in vision.lower() and "state-specific accessibility" in vision.lower(),
            "VISION must describe the current static privacy baseline",
            failures)
    require("attribution" in security.lower() and "make check" in security and "in-flight" in security.lower() and "completed state" in security.lower() and "state-specific accessibility" in security.lower(),
            "SECURITY must document attribution privacy and the static baseline",
            failures)
    require("debug logging" in changes and "segment" in changes and "make check" in changes and
            "user-triggered" in changes and "main queue" in changes and "in-flight" in changes.lower() and "completed state" in changes.lower() and "state-specific accessibility" in changes.lower(),
            "CHANGES must record logging, segment, user-triggered attribution, in-flight UI, main-queue completion, and baseline updates",
            failures)
    require("status: completed" in baseline_plan and "status: completed" in explicit_request_plan and
            "status: completed" in main_thread_plan and "status: completed" in in_flight_plan,
            "plans must be marked completed",
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

    if shutil.which("xcodebuild"):
        print("xcodebuild is available; run a scheme-specific Xcode test on macOS before release.")
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
