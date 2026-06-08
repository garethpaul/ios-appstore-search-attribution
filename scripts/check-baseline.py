#!/usr/bin/env python3
from pathlib import Path
import plistlib
import re
import shutil
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/plans/2026-06-08-attribution-baseline.md"


def require(condition, message, failures):
    if not condition:
        failures.append(message)


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


def strip_swift_line_comments(text):
    return "\n".join(line.split("//", 1)[0] for line in text.splitlines())


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
    active_app_delegate = strip_swift_line_comments(app_delegate)
    readme = read("README.md")
    vision = read("VISION.md")
    security = read("SECURITY.md")
    changes = read("CHANGES.md")
    gitignore = read(".gitignore")
    plan = PLAN.read_text(encoding="utf-8") if PLAN.exists() else ""

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

    require("import iAd" in active_app_delegate,
            "AppDelegate must keep the ADClient/iAd attribution sample import",
            failures)
    require("ADClient.shared().requestAttributionDetails" in active_app_delegate,
            "AppDelegate must keep the attribution request example",
            failures)
    require('"Version3.1"' in active_app_delegate and '"iad-attribution"' in active_app_delegate,
            "AppDelegate must keep the documented attribution response lookup",
            failures)
    require(not re.search(r"\b(?:print|println|NSLog)\s*\(", active_app_delegate),
            "Attribution callback must not log attribution data",
            failures)
    for forbidden in ["add(toSegments", "URLSession", "NSURLConnection", "NSURL", "http://", "https://", "upload", "UserDefaults"]:
        require(forbidden not in active_app_delegate,
                f"AppDelegate must not add storage, network, or segment behavior for attribution data: {forbidden}",
                failures)

    swift_files = sorted((ROOT / "ios-search-ads-sample").rglob("*.swift"))
    require(len(swift_files) == 2,
            "expected Swift source inventory is missing",
            failures)
    require("*.local.xcconfig" in gitignore and ".env" in gitignore,
            ".gitignore must exclude local secret/config files",
            failures)
    require("make check" in readme and "ADClient" in readme and "local-only" in readme.lower(),
            "README must document static verification and local-only ADClient handling",
            failures)
    require("scripts/check-baseline.py" in vision and "local-only" in vision.lower(),
            "VISION must describe the current static privacy baseline",
            failures)
    require("attribution" in security.lower() and "make check" in security,
            "SECURITY must document attribution privacy and the static baseline",
            failures)
    require("debug logging" in changes and "segment" in changes and "make check" in changes,
            "CHANGES must record logging, segment, and baseline updates",
            failures)
    require("status: completed" in plan,
            "plan must be marked completed",
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
