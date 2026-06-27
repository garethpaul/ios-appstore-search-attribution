import XCTest
@testable import ios_search_ads_sample

final class AttributionRequestCoordinatorTests: XCTestCase {
    func testIgnoresDuplicateStartsAndCompletesOnceOnMainThread() {
        let client = StubAttributionClient()
        let scheduler = ManualScheduler()
        let coordinator = AttributionRequestCoordinator(client: client, scheduler: scheduler, timeout: 30)
        var states: [AttributionRequestCoordinator.State] = []
        coordinator.onStateChange = { state in
            XCTAssertTrue(Thread.isMainThread)
            states.append(state)
        }

        coordinator.start()
        coordinator.start()
        client.complete(.success(()), request: 0)
        client.complete(.failure(.network), request: 0)

        XCTAssertEqual(client.requestCount, 1)
        XCTAssertEqual(states, [.requesting, .completed])
    }

    func testTimeoutCancelsRequestAndLateCompletionCannotOverwriteFailure() {
        let client = StubAttributionClient()
        let scheduler = ManualScheduler()
        let coordinator = AttributionRequestCoordinator(client: client, scheduler: scheduler, timeout: 30)
        var states: [AttributionRequestCoordinator.State] = []
        coordinator.onStateChange = { states.append($0) }

        coordinator.start()
        scheduler.runNext()
        client.complete(.success(()), request: 0)

        XCTAssertTrue(client.cancellables[0].isCancelled)
        XCTAssertEqual(states, [.requesting, .failed])
    }

    func testCancelInvalidatesGenerationAndAllowsFreshRequest() {
        let client = StubAttributionClient()
        let scheduler = ManualScheduler()
        let coordinator = AttributionRequestCoordinator(client: client, scheduler: scheduler, timeout: 30)
        var states: [AttributionRequestCoordinator.State] = []
        coordinator.onStateChange = { states.append($0) }

        coordinator.start()
        coordinator.cancel()
        coordinator.start()
        client.complete(.success(()), request: 0)
        client.complete(.success(()), request: 1)

        XCTAssertTrue(client.cancellables[0].isCancelled)
        XCTAssertEqual(client.requestCount, 2)
        XCTAssertEqual(states, [.requesting, .idle, .requesting, .completed])
    }

    func testSynchronousTimeoutPreventsRequestStartup() {
        let client = StubAttributionClient()
        let coordinator = AttributionRequestCoordinator(
            client: client,
            scheduler: SynchronousScheduler(),
            timeout: 0)
        var states: [AttributionRequestCoordinator.State] = []
        coordinator.onStateChange = { states.append($0) }

        coordinator.start()

        XCTAssertEqual(client.requestCount, 0)
        XCTAssertEqual(states, [.requesting, .failed])
    }

    func testSynchronousCompletionCancelsReturnedRequestHandle() {
        let client = SynchronousAttributionClient(result: .success(()))
        let coordinator = AttributionRequestCoordinator(
            client: client,
            scheduler: ManualScheduler(),
            timeout: 30)
        var states: [AttributionRequestCoordinator.State] = []
        coordinator.onStateChange = { states.append($0) }

        coordinator.start()

        XCTAssertTrue(client.cancellable.isCancelled)
        XCTAssertEqual(states, [.requesting, .completed])
    }
}

private final class StubAttributionClient: AttributionRequesting {
    private(set) var completions: [(Result<Void, AttributionClientError>) -> Void] = []
    private(set) var cancellables: [TestCancellable] = []
    var requestCount: Int { completions.count }

    @discardableResult
    func request(completion: @escaping (Result<Void, AttributionClientError>) -> Void) -> AttributionCancellable {
        let cancellable = TestCancellable()
        completions.append(completion)
        cancellables.append(cancellable)
        return cancellable
    }

    func complete(_ result: Result<Void, AttributionClientError>, request: Int) {
        completions[request](result)
    }
}

private final class TestCancellable: AttributionCancellable {
    private(set) var isCancelled = false
    func cancel() { isCancelled = true }
}

private final class SynchronousAttributionClient: AttributionRequesting {
    let cancellable = TestCancellable()
    private let result: Result<Void, AttributionClientError>

    init(result: Result<Void, AttributionClientError>) {
        self.result = result
    }

    @discardableResult
    func request(completion: @escaping (Result<Void, AttributionClientError>) -> Void) -> AttributionCancellable {
        completion(result)
        return cancellable
    }
}

private final class SynchronousScheduler: AttributionScheduling {
    @discardableResult
    func schedule(after _: TimeInterval, execute: @escaping () -> Void) -> AttributionCancellable {
        let cancellable = TestCancellable()
        execute()
        return cancellable
    }
}

private final class ManualScheduler: AttributionScheduling {
    private var work: [() -> Void] = []

    @discardableResult
    func schedule(after _: TimeInterval, execute: @escaping () -> Void) -> AttributionCancellable {
        let cancellable = TestCancellable()
        work.append {
            guard !cancellable.isCancelled else { return }
            execute()
        }
        return cancellable
    }

    func runNext() {
        work.removeFirst()()
    }
}
