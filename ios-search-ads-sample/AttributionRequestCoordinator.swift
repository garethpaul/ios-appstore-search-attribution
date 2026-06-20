import Foundation

final class AttributionRequestCoordinator {
    enum State: Equatable {
        case idle
        case requesting
        case failed
        case completed
    }

    var onStateChange: ((State) -> Void)?
    private(set) var state: State = .idle

    private let client: AttributionRequesting
    private let scheduler: AttributionScheduling
    private let timeout: TimeInterval
    private var generation = 0
    private var activeRequest: AttributionCancellable?
    private var timeoutTask: AttributionCancellable?

    init(
        client: AttributionRequesting,
        scheduler: AttributionScheduling = DispatchAttributionScheduler(),
        timeout: TimeInterval = 30
    ) {
        self.client = client
        self.scheduler = scheduler
        self.timeout = timeout
    }

    func start() {
        dispatchPrecondition(condition: .onQueue(.main))
        guard state == .idle || state == .failed else { return }

        generation += 1
        let requestGeneration = generation
        transition(to: .requesting)
        timeoutTask = scheduler.schedule(after: timeout) { [weak self] in
            self?.finish(generation: requestGeneration, result: .failure(.network))
        }
        activeRequest = client.request { [weak self] result in
            if Thread.isMainThread {
                self?.finish(generation: requestGeneration, result: result)
            } else {
                DispatchQueue.main.async {
                    self?.finish(generation: requestGeneration, result: result)
                }
            }
        }
    }

    func cancel() {
        dispatchPrecondition(condition: .onQueue(.main))
        generation += 1
        activeRequest?.cancel()
        timeoutTask?.cancel()
        activeRequest = nil
        timeoutTask = nil
        if state != .idle {
            transition(to: .idle)
        }
    }

    private func finish(generation requestGeneration: Int, result: Result<Void, AttributionClientError>) {
        dispatchPrecondition(condition: .onQueue(.main))
        guard requestGeneration == generation, state == .requesting else { return }

        activeRequest?.cancel()
        timeoutTask?.cancel()
        activeRequest = nil
        timeoutTask = nil
        switch result {
        case .success:
            transition(to: .completed)
        case .failure:
            transition(to: .failed)
        }
    }

    private func transition(to newState: State) {
        state = newState
        onStateChange?(newState)
    }
}
