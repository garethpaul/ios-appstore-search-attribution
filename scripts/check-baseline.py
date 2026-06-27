#!/usr/bin/env python3

from __future__ import annotations

import plistlib
import re
import shutil
import stat
import subprocess
import sys
from xml.parsers import expat
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAX_STORYBOARD_XML_BYTES = 1024 * 1024
MAX_STORYBOARD_XML_DEPTH = 256
MAX_STORYBOARD_XML_ELEMENTS = 50_000
MAX_STORYBOARD_XML_ATTRIBUTES = 1_024
XML_CHUNK_BYTES = 64 * 1024


class SafeXMLParseError(ValueError):
    pass


def repo_file_safety_error(path: Path) -> str | None:
    try:
        relative_path = path.relative_to(ROOT)
    except ValueError:
        return "path escapes the checkout"

    if any(part in {"", ".", ".."} for part in relative_path.parts):
        return "path escapes the checkout"

    current = ROOT
    for part in relative_path.parts:
        current /= part
        try:
            mode = current.lstat().st_mode
        except OSError as error:
            return str(error)
        if stat.S_ISLNK(mode):
            return f"path traverses symlink: {current.relative_to(ROOT)}"

    if not stat.S_ISREG(mode):
        return "path is not a regular file"
    return None


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def validate_storyboard_xml(path: Path) -> None:
    safety_error = repo_file_safety_error(path)
    if safety_error is not None:
        raise SafeXMLParseError(safety_error)

    parser = expat.ParserCreate(namespace_separator="\x1f")
    depth = 0
    element_count = 0
    saw_root = False

    def reject(message: str) -> None:
        raise SafeXMLParseError(message)

    def start_element(_name: str, _attrs: dict[str, str]) -> None:
        nonlocal depth, element_count, saw_root
        saw_root = True
        depth += 1
        element_count += 1
        if depth > MAX_STORYBOARD_XML_DEPTH:
            reject(f"XML nesting exceeds {MAX_STORYBOARD_XML_DEPTH} elements")
        if element_count > MAX_STORYBOARD_XML_ELEMENTS:
            reject(f"XML contains more than {MAX_STORYBOARD_XML_ELEMENTS} elements")
        if len(_attrs) > MAX_STORYBOARD_XML_ATTRIBUTES:
            reject(f"XML element contains more than {MAX_STORYBOARD_XML_ATTRIBUTES} attributes")

    def end_element(_name: str) -> None:
        nonlocal depth
        depth -= 1

    def reject_doctype(
        _doctype_name: str,
        _system_id: str | None,
        _public_id: str | None,
        _has_internal_subset: int,
    ) -> None:
        reject("DOCTYPE declarations are not allowed")

    parser.StartElementHandler = start_element
    parser.EndElementHandler = end_element
    parser.StartDoctypeDeclHandler = reject_doctype
    parser.EntityDeclHandler = lambda *_args: reject("Entity declarations are not allowed")
    parser.UnparsedEntityDeclHandler = lambda *_args: reject("Entity declarations are not allowed")
    parser.ExternalEntityRefHandler = lambda *_args: reject("External entities are not allowed")
    parser.SkippedEntityHandler = lambda *_args: reject("Entity references are not allowed")
    parser.SetParamEntityParsing(expat.XML_PARAM_ENTITY_PARSING_NEVER)

    try:
        total_bytes = 0
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(XML_CHUNK_BYTES), b""):
                total_bytes += len(chunk)
                if total_bytes > MAX_STORYBOARD_XML_BYTES:
                    reject(f"XML file exceeds {MAX_STORYBOARD_XML_BYTES} bytes")
                parser.Parse(chunk, False)
        parser.Parse(b"", True)
    except (expat.ExpatError, LookupError) as error:
        raise SafeXMLParseError(str(error)) from error

    if not saw_root:
        reject("XML document must contain a root element")


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
        "docs/plans/2026-06-25-attribution-redirect-rejection.md",
        "docs/plans/2026-06-27-synchronous-startup-ownership.md",
        "scripts/select-simulator.py",
        "scripts/run-xcode-tests.sh",
        "tests/test_check_baseline_xml_security.py",
        "tests/test_simulator_selection.py",
    ]
    for relative_path in required_files:
        path = ROOT / relative_path
        safety_error = repo_file_safety_error(path)
        require(safety_error is None, f"Required file is unsafe: {relative_path}: {safety_error}", failures)

    if failures:
        return report(failures)

    try:
        with (ROOT / "ios-search-ads-sample/Info.plist").open("rb") as handle:
            plist = plistlib.load(handle)
        validate_storyboard_xml(ROOT / "ios-search-ads-sample/Base.lproj/Main.storyboard")
    except (OSError, plistlib.InvalidFileException, SafeXMLParseError) as error:
        failures.append(f"Project metadata must parse safely: {error}")
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
    xcode_test_runner = read("scripts/run-xcode-tests.sh")
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
    require("let scheduledTimeout = scheduler.schedule(after: timeout)" in coordinator and
            "guard ownsRequest(generation: requestGeneration) else {" in coordinator and
            "scheduledTimeout.cancel()" in coordinator and
            "let request = client.request" in coordinator and
            "request.cancel()" in coordinator and
            coordinator.count("guard ownsRequest(generation: requestGeneration) else {") == 2,
            "Coordinator startup must reject synchronously terminal timeout and request handles", failures)

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
        "AttributionRedirectPolicy.redirectedRequest(newRequest)",
        "willPerformHTTPRedirection",
        "return nil",
    ]:
        require(evidence in client, f"Attribution client invariant missing: {evidence}", failures)
    require("URLSession.shared" not in client and "cachedResponse" not in client,
            "Attribution client must not use shared or cached sessions", failures)
    require("statusCode == 500" in client and "pow(2, Double(number - 1))" in client,
            "Server errors must use bounded exponential backoff", failures)
    require("statusCode == 404" in client and "retryDelay" in client,
            "Not-found retries must retain Apple's five-second interval", failures)
    set_active_start = client.index("    func setActive(")
    set_active_end = client.index("    func setScheduledRetry", set_active_start)
    set_active = client[set_active_start:set_active_end]
    require(") -> Bool {" in set_active and
            "return false" in set_active and "return true" in set_active and
            "guard operation.setActive(session: session, task: task, delegate: delegate) else" in client and
            client.index("guard operation.setActive(session: session, task: task, delegate: delegate) else") < client.index("task.resume()"),
            "A request task must resume only after its operation accepts exact ownership", failures)

    for evidence in [
        "private var generation = 0",
        "requestGeneration == generation",
        "state == .requesting",
        "activeRequest?.cancel()",
        "timeoutTask?.cancel()",
        "DispatchQueue.main.async",
    ]:
        require(evidence in coordinator, f"Coordinator ownership invariant missing: {evidence}", failures)

    require(network_tests.count("func test") >= 7 and "MockURLProtocol" in network_tests and
            "testRedirectPolicyRejectsTokenBearingRequest" in network_tests,
            "Network tests must cover request, redirect, retry, cancellation, and resource boundaries with URLProtocol", failures)
    require(coordinator_tests.count("func test") >= 5 and
            "testSynchronousTimeoutPreventsRequestStartup" in coordinator_tests and
            "testSynchronousCompletionCancelsReturnedRequestHandle" in coordinator_tests and
            "late completion" not in coordinator_tests.lower(),
            "Coordinator tests must cover duplicate, timeout, generation, and synchronous startup ownership", failures)
    require(parser_tests.count("func test") >= 4 and '"attribution":1' in parser_tests and
            '"attribution":"true"' in parser_tests,
            "Parser tests must reject non-Boolean attribution lookalikes", failures)

    require("override MAKEFILE_ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))" in makefile and
            'cd "$(MAKEFILE_ROOT)"' in makefile and
            "python3 -m unittest discover -s tests -p 'test_*.py'" in makefile and
            "scripts/run-xcode-tests.sh" in makefile,
            "Make targets must derive the checkout root and run Python security tests plus native XCTest", failures)
    require('xcrun simctl list devices available -j | python3 -I "$ROOT/scripts/select-simulator.py"'
            in xcode_test_runner,
            "Simulator selection must use the isolated helper", failures)
    require("permissions:\n  contents: read" in check_workflow and
            "persist-credentials: false" in check_workflow and
            "run: make check" in check_workflow,
            "Check workflow must be read-only, credential-free, and canonical", failures)
    require("AdServices" in documentation and "64 KiB" in documentation and
            "three total attempts" in documentation and "not persisted" in documentation.lower(),
            "Documentation must describe current API, bounds, retry exhaustion, and no persistence", failures)
    synchronous_startup_guidance = (
        "Coordinator startup rejects and cancels timeout or request handles returned after a synchronous terminal callback."
    )
    require(documentation.count(synchronous_startup_guidance) == 3,
            "Maintained documentation must preserve synchronous startup ownership guidance", failures)

    xcodebuild = shutil.which("xcodebuild")
    if xcodebuild is None:
        print("Skipping xcodebuild project parse: xcodebuild is not installed.")
    else:
        project_result = subprocess.run(
            [xcodebuild, "-project", "ios-search-ads-sample.xcodeproj", "-list"],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        require(
            project_result.returncode == 0
            and "ios-search-ads-sampleTests" in project_result.stdout,
            "xcodebuild must load the app and XCTest targets",
            failures,
        )

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
