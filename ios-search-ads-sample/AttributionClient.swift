import AdServices
import Foundation

enum AttributionClientError: Error, Equatable {
    case unsupportedOperatingSystem
    case tokenGenerationFailed
    case invalidToken
    case invalidResponse
    case unexpectedStatus(Int)
    case invalidContentType
    case responseTooLarge
    case invalidPayload
    case network
    case retryExhausted
}

protocol AttributionCancellable: AnyObject {
    func cancel()
}

protocol AttributionScheduling {
    @discardableResult
    func schedule(after delay: TimeInterval, execute: @escaping () -> Void) -> AttributionCancellable
}

protocol AttributionRequesting {
    @discardableResult
    func request(completion: @escaping (Result<Void, AttributionClientError>) -> Void) -> AttributionCancellable
}

final class DispatchAttributionScheduler: AttributionScheduling {
    private let queue: DispatchQueue

    init(queue: DispatchQueue = .main) {
        self.queue = queue
    }

    @discardableResult
    func schedule(after delay: TimeInterval, execute: @escaping () -> Void) -> AttributionCancellable {
        let workItem = DispatchWorkItem(block: execute)
        queue.asyncAfter(deadline: .now() + delay, execute: workItem)
        return workItem
    }
}

extension DispatchWorkItem: AttributionCancellable {}

enum AttributionRedirectPolicy {
    static func redirectedRequest(_ request: URLRequest) -> URLRequest? {
        return nil
    }
}

enum AttributionResponseParser {
    private struct Payload: Decodable {
        let attribution: Bool
    }

    static func parse(
        data: Data,
        response: HTTPURLResponse,
        maximumResponseBytes: Int
    ) throws -> Bool {
        guard response.statusCode == 200 else {
            throw AttributionClientError.unexpectedStatus(response.statusCode)
        }
        guard response.mimeType?.lowercased() == "application/json" else {
            throw AttributionClientError.invalidContentType
        }
        guard data.count <= maximumResponseBytes else {
            throw AttributionClientError.responseTooLarge
        }

        do {
            return try JSONDecoder().decode(Payload.self, from: data).attribution
        } catch {
            throw AttributionClientError.invalidPayload
        }
    }
}

final class AdServicesAttributionClient: AttributionRequesting {
    private static let endpoint = URL(string: "https://api-adservices.apple.com/api/v1/")!

    private let configuration: URLSessionConfiguration
    private let tokenProvider: () throws -> String
    private let scheduler: AttributionScheduling
    private let completionQueue: DispatchQueue
    private let maximumAttempts: Int
    private let retryDelay: TimeInterval
    private let maximumResponseBytes: Int

    init(
        configuration: URLSessionConfiguration = .ephemeral,
        tokenProvider: @escaping () throws -> String = AdServicesAttributionClient.systemToken,
        scheduler: AttributionScheduling = DispatchAttributionScheduler(),
        completionQueue: DispatchQueue = .main,
        maximumAttempts: Int = 3,
        retryDelay: TimeInterval = 5,
        maximumResponseBytes: Int = 64 * 1_024
    ) {
        let privateConfiguration = configuration.copy() as! URLSessionConfiguration
        privateConfiguration.requestCachePolicy = .reloadIgnoringLocalCacheData
        privateConfiguration.urlCache = nil
        privateConfiguration.httpCookieStorage = nil
        privateConfiguration.urlCredentialStorage = nil
        privateConfiguration.httpShouldSetCookies = false
        privateConfiguration.waitsForConnectivity = false
        privateConfiguration.timeoutIntervalForRequest = 10
        privateConfiguration.timeoutIntervalForResource = 20
        privateConfiguration.httpMaximumConnectionsPerHost = 1

        self.configuration = privateConfiguration
        self.tokenProvider = tokenProvider
        self.scheduler = scheduler
        self.completionQueue = completionQueue
        self.maximumAttempts = maximumAttempts
        self.retryDelay = retryDelay
        self.maximumResponseBytes = maximumResponseBytes
    }

    @discardableResult
    func request(completion: @escaping (Result<Void, AttributionClientError>) -> Void) -> AttributionCancellable {
        let operation = RequestOperation(completionQueue: completionQueue, completion: completion)

        let token: String
        do {
            token = try tokenProvider()
        } catch let error as AttributionClientError {
            operation.finish(.failure(error))
            return operation
        } catch {
            operation.finish(.failure(.tokenGenerationFailed))
            return operation
        }

        guard isValid(token: token) else {
            operation.finish(.failure(.invalidToken))
            return operation
        }

        startAttempt(number: 1, token: token, operation: operation)
        return operation
    }

    private func startAttempt(number: Int, token: String, operation: RequestOperation) {
        guard !operation.isCancelled else { return }

        var request = URLRequest(
            url: Self.endpoint,
            cachePolicy: .reloadIgnoringLocalCacheData,
            timeoutInterval: configuration.timeoutIntervalForRequest)
        request.httpMethod = "POST"
        request.httpBody = Data(token.utf8)
        request.setValue("text/plain; charset=utf-8", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")

        let delegate = BoundedDataDelegate(maximumResponseBytes: maximumResponseBytes) { [weak self, operation] result in
            guard let self, !operation.isCancelled else { return }
            switch result {
            case let .success((response, data)):
                if response.statusCode == 404 || response.statusCode == 500 {
                    retryOrFinish(
                        number: number,
                        statusCode: response.statusCode,
                        token: token,
                        operation: operation)
                    return
                }
                do {
                    _ = try AttributionResponseParser.parse(
                        data: data,
                        response: response,
                        maximumResponseBytes: maximumResponseBytes)
                    operation.finish(.success(()))
                } catch let error as AttributionClientError {
                    operation.finish(.failure(error))
                } catch {
                    operation.finish(.failure(.invalidPayload))
                }
            case let .failure(error):
                operation.finish(.failure(error))
            }
        }
        let session = URLSession(configuration: configuration, delegate: delegate, delegateQueue: nil)
        let task = session.dataTask(with: request)
        operation.setActive(session: session, task: task, delegate: delegate)
        task.resume()
    }

    private func retryOrFinish(
        number: Int,
        statusCode: Int,
        token: String,
        operation: RequestOperation
    ) {
        guard number < maximumAttempts else {
            operation.finish(.failure(.retryExhausted))
            return
        }
        let delay = statusCode == 500
            ? retryDelay * pow(2, Double(number - 1))
            : retryDelay
        let retry = scheduler.schedule(after: delay) { [weak self, weak operation] in
            guard let self, let operation else { return }
            startAttempt(number: number + 1, token: token, operation: operation)
        }
        operation.setScheduledRetry(retry)
    }

    private func isValid(token: String) -> Bool {
        guard !token.isEmpty, token.utf8.count <= 16 * 1_024 else { return false }
        return token.unicodeScalars.allSatisfy { !CharacterSet.controlCharacters.contains($0) }
    }

    private static func systemToken() throws -> String {
        guard #available(iOS 14.3, *) else {
            throw AttributionClientError.unsupportedOperatingSystem
        }
        do {
            return try AAAttribution.attributionToken()
        } catch {
            throw AttributionClientError.tokenGenerationFailed
        }
    }
}

private final class RequestOperation: AttributionCancellable {
    private let lock = NSLock()
    private let completionQueue: DispatchQueue
    private var completion: ((Result<Void, AttributionClientError>) -> Void)?
    private var session: URLSession?
    private var task: URLSessionTask?
    private var delegate: BoundedDataDelegate?
    private var scheduledRetry: AttributionCancellable?
    private(set) var isCancelled = false

    init(
        completionQueue: DispatchQueue,
        completion: @escaping (Result<Void, AttributionClientError>) -> Void
    ) {
        self.completionQueue = completionQueue
        self.completion = completion
    }

    func setActive(session: URLSession, task: URLSessionTask, delegate: BoundedDataDelegate) {
        lock.lock()
        defer { lock.unlock() }
        guard !isCancelled, completion != nil else {
            session.invalidateAndCancel()
            return
        }
        self.session?.invalidateAndCancel()
        self.session = session
        self.task = task
        self.delegate = delegate
    }

    func setScheduledRetry(_ retry: AttributionCancellable) {
        lock.lock()
        defer { lock.unlock() }
        guard !isCancelled, completion != nil else {
            retry.cancel()
            return
        }
        scheduledRetry?.cancel()
        scheduledRetry = retry
    }

    func finish(_ result: Result<Void, AttributionClientError>) {
        let callback: ((Result<Void, AttributionClientError>) -> Void)?
        lock.lock()
        if isCancelled {
            callback = nil
        } else {
            callback = completion
            completion = nil
        }
        task = nil
        delegate = nil
        scheduledRetry?.cancel()
        scheduledRetry = nil
        let completedSession = session
        session = nil
        lock.unlock()

        completedSession?.finishTasksAndInvalidate()
        guard let callback else { return }
        completionQueue.async { callback(result) }
    }

    func cancel() {
        lock.lock()
        guard !isCancelled else {
            lock.unlock()
            return
        }
        isCancelled = true
        completion = nil
        let activeTask = task
        let activeSession = session
        let retry = scheduledRetry
        task = nil
        session = nil
        delegate = nil
        scheduledRetry = nil
        lock.unlock()

        retry?.cancel()
        activeTask?.cancel()
        activeSession?.invalidateAndCancel()
    }
}

private final class BoundedDataDelegate: NSObject, URLSessionDataDelegate {
    private let maximumResponseBytes: Int
    private let completion: (Result<(HTTPURLResponse, Data), AttributionClientError>) -> Void
    private var response: HTTPURLResponse?
    private var data = Data()
    private var terminalError: AttributionClientError?

    init(
        maximumResponseBytes: Int,
        completion: @escaping (Result<(HTTPURLResponse, Data), AttributionClientError>) -> Void
    ) {
        self.maximumResponseBytes = maximumResponseBytes
        self.completion = completion
    }

    func urlSession(
        _: URLSession,
        dataTask: URLSessionDataTask,
        didReceive response: URLResponse,
        completionHandler: @escaping (URLSession.ResponseDisposition) -> Void
    ) {
        guard let httpResponse = response as? HTTPURLResponse else {
            terminalError = .invalidResponse
            completionHandler(.cancel)
            return
        }
        if httpResponse.expectedContentLength > Int64(maximumResponseBytes) {
            terminalError = .responseTooLarge
            completionHandler(.cancel)
            return
        }
        self.response = httpResponse
        completionHandler(.allow)
    }

    func urlSession(
        _: URLSession,
        task _: URLSessionTask,
        willPerformHTTPRedirection response: HTTPURLResponse,
        newRequest: URLRequest,
        completionHandler: @escaping (URLRequest?) -> Void
    ) {
        self.response = response
        completionHandler(AttributionRedirectPolicy.redirectedRequest(newRequest))
    }

    func urlSession(_: URLSession, dataTask: URLSessionDataTask, didReceive newData: Data) {
        guard terminalError == nil else { return }
        guard data.count <= maximumResponseBytes - newData.count else {
            terminalError = .responseTooLarge
            dataTask.cancel()
            return
        }
        data.append(newData)
    }

    func urlSession(_: URLSession, task: URLSessionTask, didCompleteWithError error: Error?) {
        if let terminalError {
            completion(.failure(terminalError))
        } else if error != nil {
            completion(.failure(.network))
        } else if let response {
            completion(.success((response, data)))
        } else {
            completion(.failure(.invalidResponse))
        }
    }
}
