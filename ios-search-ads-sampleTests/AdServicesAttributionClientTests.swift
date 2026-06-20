import XCTest
@testable import ios_search_ads_sample

final class AdServicesAttributionClientTests: XCTestCase {
    override func setUp() {
        super.setUp()
        MockURLProtocol.reset()
    }

    func testUsesPrivacyPreservingRequestConfigurationWithoutLoggingToken() {
        MockURLProtocol.setResponses([.init(statusCode: 200, contentType: "application/json", body: #"{"attribution":true}"#)])
        let client = makeClient(token: "private-token")
        let completed = expectation(description: "completed")

        _ = client.request { result in
            if case let .failure(error) = result {
                XCTFail("Unexpected failure: \(error)")
            }
            completed.fulfill()
        }

        wait(for: [completed], timeout: 1)
        let request = try! XCTUnwrap(MockURLProtocol.recordedRequests.first)
        XCTAssertEqual(request.url?.absoluteString, "https://api-adservices.apple.com/api/v1/")
        XCTAssertEqual(request.httpMethod, "POST")
        XCTAssertEqual(request.value(forHTTPHeaderField: "Content-Type"), "text/plain; charset=utf-8")
        XCTAssertEqual(request.value(forHTTPHeaderField: "Accept"), "application/json")
        XCTAssertEqual(requestBody(request), Data("private-token".utf8))
        XCTAssertEqual(request.cachePolicy, .reloadIgnoringLocalCacheData)
    }

    func testRetriesRetryableStatusesThreeTotalAttemptsThenExhausts() {
        MockURLProtocol.setResponses(Array(repeating: .init(statusCode: 404, contentType: "application/json", body: "{}"), count: 3))
        let scheduler = ImmediateScheduler()
        let client = makeClient(scheduler: scheduler)
        let completed = expectation(description: "completed")

        _ = client.request { result in
            XCTAssertEqual(result.failure, .retryExhausted)
            completed.fulfill()
        }

        wait(for: [completed], timeout: 1)
        XCTAssertEqual(MockURLProtocol.recordedRequests.count, 3)
        XCTAssertEqual(scheduler.delays, [5, 5])
    }

    func testBacksOffServerErrorsAcrossThreeTotalAttempts() {
        MockURLProtocol.setResponses(Array(repeating: .init(statusCode: 500, contentType: "application/json", body: "{}"), count: 3))
        let scheduler = ImmediateScheduler()
        let client = makeClient(scheduler: scheduler)
        let completed = expectation(description: "completed")

        _ = client.request { result in
            XCTAssertEqual(result.failure, .retryExhausted)
            completed.fulfill()
        }

        wait(for: [completed], timeout: 1)
        XCTAssertEqual(scheduler.delays, [5, 10])
    }

    func testRejectsOversizedStreamedResponseWithoutRetry() {
        MockURLProtocol.setResponses([.init(
            statusCode: 200,
            contentType: "application/json",
            body: String(repeating: " ", count: 65 * 1_024))])
        let scheduler = ImmediateScheduler()
        let client = makeClient(scheduler: scheduler)
        let completed = expectation(description: "completed")

        _ = client.request { result in
            XCTAssertEqual(result.failure, .responseTooLarge)
            completed.fulfill()
        }

        wait(for: [completed], timeout: 1)
        XCTAssertTrue(scheduler.delays.isEmpty)
    }

    func testDoesNotRetryInvalidTokenOrMalformedSuccessfulResponse() {
        for response in [
            MockURLProtocol.Response(statusCode: 400, contentType: "application/json", body: "{}"),
            MockURLProtocol.Response(statusCode: 200, contentType: "application/json", body: #"{"attribution":1}"#),
        ] {
            MockURLProtocol.reset()
            MockURLProtocol.setResponses([response])
            let scheduler = ImmediateScheduler()
            let client = makeClient(scheduler: scheduler)
            let completed = expectation(description: "completed \(response.statusCode)")

            _ = client.request { _ in completed.fulfill() }
            wait(for: [completed], timeout: 1)

            XCTAssertFalse(MockURLProtocol.recordedRequests.isEmpty)
            XCTAssertTrue(scheduler.delays.isEmpty)
        }
    }

    func testCancellationPreventsCompletionAndFurtherRetries() {
        MockURLProtocol.setResponses([.init(statusCode: 404, contentType: "application/json", body: "{}")])
        let scheduler = SuspendedScheduler()
        let client = makeClient(scheduler: scheduler)
        var completionCount = 0

        let request = client.request { _ in completionCount += 1 }
        request.cancel()
        scheduler.runAll()

        XCTAssertEqual(completionCount, 0)
        XCTAssertEqual(MockURLProtocol.recordedRequests.count, 0)
    }

    private func makeClient(
        token: String = "token",
        scheduler: AttributionScheduling = ImmediateScheduler()
    ) -> AdServicesAttributionClient {
        let configuration = URLSessionConfiguration.ephemeral
        configuration.protocolClasses = [MockURLProtocol.self]
        return AdServicesAttributionClient(
            configuration: configuration,
            tokenProvider: { token },
            scheduler: scheduler)
    }

    private func requestBody(_ request: URLRequest) -> Data? {
        if let body = request.httpBody { return body }
        guard let stream = request.httpBodyStream else { return nil }
        stream.open()
        defer { stream.close() }
        var data = Data()
        var buffer = [UInt8](repeating: 0, count: 1_024)
        while stream.hasBytesAvailable {
            let count = stream.read(&buffer, maxLength: buffer.count)
            guard count > 0 else { break }
            data.append(buffer, count: count)
        }
        return data
    }
}

private extension Result where Failure == AttributionClientError {
    var failure: AttributionClientError? {
        guard case let .failure(error) = self else { return nil }
        return error
    }
}

private final class ImmediateScheduler: AttributionScheduling {
    private(set) var delays: [TimeInterval] = []

    @discardableResult
    func schedule(after delay: TimeInterval, execute: @escaping () -> Void) -> AttributionCancellable {
        delays.append(delay)
        execute()
        return TestNetworkCancellable()
    }
}

private final class SuspendedScheduler: AttributionScheduling {
    private var work: [() -> Void] = []

    @discardableResult
    func schedule(after _: TimeInterval, execute: @escaping () -> Void) -> AttributionCancellable {
        let cancellable = TestNetworkCancellable()
        work.append {
            guard !cancellable.isCancelled else { return }
            execute()
        }
        return cancellable
    }

    func runAll() {
        let pending = work
        work.removeAll()
        pending.forEach { $0() }
    }
}

private final class TestNetworkCancellable: AttributionCancellable {
    private(set) var isCancelled = false
    func cancel() { isCancelled = true }
}

private final class MockURLProtocol: URLProtocol {
    struct Response {
        let statusCode: Int
        let contentType: String
        let body: String
    }

    private static let lock = NSLock()
    private static var responses: [Response] = []
    private static var requests: [URLRequest] = []

    static var recordedRequests: [URLRequest] {
        lock.lock()
        defer { lock.unlock() }
        return requests
    }

    static func setResponses(_ newResponses: [Response]) {
        lock.lock()
        responses = newResponses
        lock.unlock()
    }

    static func reset() {
        lock.lock()
        responses = []
        requests = []
        lock.unlock()
    }

    override class func canInit(with _: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }

    override func startLoading() {
        Self.lock.lock()
        Self.requests.append(request)
        let response = Self.responses.isEmpty ? nil : Self.responses.removeFirst()
        Self.lock.unlock()
        guard let response else {
            client?.urlProtocol(self, didFailWithError: URLError(.badServerResponse))
            return
        }
        let httpResponse = HTTPURLResponse(
            url: request.url!,
            statusCode: response.statusCode,
            httpVersion: "HTTP/1.1",
            headerFields: ["Content-Type": response.contentType])!
        client?.urlProtocol(self, didReceive: httpResponse, cacheStoragePolicy: .notAllowed)
        client?.urlProtocol(self, didLoad: Data(response.body.utf8))
        client?.urlProtocolDidFinishLoading(self)
    }

    override func stopLoading() {}
}
