#!/usr/bin/env python3

from __future__ import annotations

import plistlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    required_files = [
        ".github/workflows/check.yml",
        "Makefile",
        "README.md",
        "SECURITY.md",
        "VISION.md",
        "ios-search-ads-sample.xcodeproj/project.pbxproj",
        "ios-search-ads-sample/AppDelegate.swift",
        "ios-search-ads-sample/AttributionClient.swift",
        "ios-search-ads-sample/AttributionRequestCoordinator.swift",
        "ios-search-ads-sample/ViewController.swift",
        "ios-search-ads-sample/Info.plist",
        "ios-search-ads-sample/Base.lproj/Main.storyboard",
        "ios-search-ads-sampleTests/AdServicesAttributionClientTests.swift",
        "ios-search-ads-sampleTests/AttributionRequestCoordinatorTests.swift",
        "ios-search-ads-sampleTests/AttributionResponseParserTests.swift",
        "scripts/run-xcode-tests.sh",
    ]
    for relative_path in required_files:
        path = ROOT / relative_path
        require(path.is_file(), f"Required file missing: {relative_path}", failures)
        require(not path.is_symlink(), f"Required file must not be a symlink: {relative_path}", failures)

    if failures:
        return report(failures)

    try:
        with (ROOT / "ios-search-ads-sample/Info.plist").open("rb") as handle:
            plist = plistlib.load(handle)
        ET.parse(ROOT / "ios-search-ads-sample/Base.lproj/Main.storyboard")
    except (OSError, plistlib.InvalidFileException, ET.ParseError) as error:
        failures.append(f"Project metadata must parse: {error}")
        return report(failures)

    project = read("ios-search-ads-sample.xcodeproj/project.pbxproj")
    app_delegate = read("ios-search-ads-sample/AppDelegate.swift")
    view_controller = read("ios-search-ads-sample/ViewController.swift")
    client = read("ios-search-ads-sample/AttributionClient.swift")
    coordinator = read("ios-search-ads-sample/AttributionRequestCoordinator.swift")
    network_tests = read("ios-search-ads-sampleTests/AdServicesAttributionClientTests.swift")
    coordinator_tests = read("ios-search-ads-sampleTests/AttributionRequestCoordinatorTests.swift")
    parser_tests = read("ios-search-ads-sampleTests/AttributionResponseParserTests.swift")
    makefile = read("Makefile")
    check_workflow = read(".github/workflows/check.yml")
    documentation = "\n".join([read("README.md"), read("SECURITY.md"), read("VISION.md")])

    require(plist.get("CFBundleIdentifier") == "$(PRODUCT_BUNDLE_IDENTIFIER)",
            "Info.plist must retain bundle identifier indirection", failures)
    require("AdServices.framework" in project and "iAd.framework" not in project,
            "Xcode project must link AdServices and remove retired iAd", failures)
    require("ios-search-ads-sampleTests" in project and project.count("product-type.bundle.unit-test") == 1,
            "Xcode project must contain one native XCTest target", failures)
    for source in ["AttributionClient.swift", "AttributionRequestCoordinator.swift"]:
        require(project.count(f"{source} in Sources") == 2,
                f"App source must be wired exactly once: {source}", failures)
    for source in [
        "AdServicesAttributionClientTests.swift",
        "AttributionRequestCoordinatorTests.swift",
        "AttributionResponseParserTests.swift",
    ]:
        require(project.count(f"{source} in Sources") == 2,
                f"Test source must be wired exactly once: {source}", failures)
    require("SWIFT_VERSION = 5.0" in project and "IPHONEOS_DEPLOYMENT_TARGET = 12.0" in project,
            "Project must preserve Swift 5 and iOS 12 compatibility settings", failures)

    require("requestAttribution" not in app_delegate and "AAAttribution" not in app_delegate,
            "App launch must not request or generate attribution", failures)
    require("AttributionRequestCoordinator" in view_controller and
            "AdServicesAttributionClient" in view_controller and
            "viewWillDisappear" in view_controller and
            "didEnterBackgroundNotification" in view_controller,
            "ViewController must use the coordinator and cancel across lifecycle transitions", failures)
    require("UserDefaults" not in view_controller + client + coordinator and
            not re.search(r"\b(?:print|debugPrint|NSLog|os_log)\s*\(", view_controller + client + coordinator),
            "Attribution token and response data must not be persisted or logged", failures)
    require("ADClient" not in view_controller + client + coordinator and "import iAd" not in view_controller,
            "Runtime source must not use retired iAd attribution", failures)

    for evidence in [
        'URL(string: "https://api-adservices.apple.com/api/v1/")',
        'request.httpMethod = "POST"',
        'request.setValue("text/plain; charset=utf-8", forHTTPHeaderField: "Content-Type")',
        'request.setValue("application/json", forHTTPHeaderField: "Accept")',
        "URLSessionConfiguration = .ephemeral",
        "privateConfiguration.urlCache = nil",
        "privateConfiguration.httpCookieStorage = nil",
        "privateConfiguration.urlCredentialStorage = nil",
        "privateConfiguration.httpShouldSetCookies = false",
        "timeoutIntervalForRequest = 10",
        "timeoutIntervalForResource = 20",
        "maximumAttempts: Int = 3",
        "retryDelay: TimeInterval = 5",
        "maximumResponseBytes: Int = 64 * 1_024",
        "response.statusCode == 404 || response.statusCode == 500",
        "JSONDecoder().decode(Payload.self",
        "let attribution: Bool",
        "URLSessionDataDelegate",
    ]:
        require(evidence in client, f"Attribution client invariant missing: {evidence}", failures)
    require("URLSession.shared" not in client and "cachedResponse" not in client,
            "Attribution client must not use shared or cached sessions", failures)
    require("statusCode == 500" in client and "pow(2, Double(number - 1))" in client,
            "Server errors must use bounded exponential backoff", failures)
    require("statusCode == 404" in client and "retryDelay" in client,
            "Not-found retries must retain Apple's five-second interval", failures)

    for evidence in [
        "private var generation = 0",
        "requestGeneration == generation",
        "state == .requesting",
        "activeRequest?.cancel()",
        "timeoutTask?.cancel()",
        "DispatchQueue.main.async",
    ]:
        require(evidence in coordinator, f"Coordinator ownership invariant missing: {evidence}", failures)

    require(network_tests.count("func test") >= 6 and "MockURLProtocol" in network_tests,
            "Network tests must cover request, retry, cancellation, and resource boundaries with URLProtocol", failures)
    require(coordinator_tests.count("func test") >= 3 and "late completion" not in coordinator_tests.lower(),
            "Coordinator tests must cover duplicate, timeout, and generation ownership", failures)
    require(parser_tests.count("func test") >= 4 and '"attribution":1' in parser_tests and
            '"attribution":"true"' in parser_tests,
            "Parser tests must reject non-Boolean attribution lookalikes", failures)

    require("MAKEFILE_ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))" in makefile and
            'cd "$(MAKEFILE_ROOT)"' in makefile and
            "scripts/run-xcode-tests.sh" in makefile,
            "Make targets must derive the checkout root and run native XCTest", failures)
    require("permissions:\n  contents: read" in check_workflow and
            "persist-credentials: false" in check_workflow and
            "run: make check" in check_workflow,
            "Check workflow must be read-only, credential-free, and canonical", failures)
    require("AdServices" in documentation and "64 KiB" in documentation and
            "three total attempts" in documentation and "not persisted" in documentation.lower(),
            "Documentation must describe current API, bounds, retry exhaustion, and no persistence", failures)

    project_result = subprocess.run(
        ["xcodebuild", "-project", "ios-search-ads-sample.xcodeproj", "-list"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    require(project_result.returncode == 0 and "ios-search-ads-sampleTests" in project_result.stdout,
            "xcodebuild must load the app and XCTest targets", failures)

    return report(failures)


def report(failures: list[str]) -> int:
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print("Attribution baseline passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
