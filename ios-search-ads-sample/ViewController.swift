//
//  ViewController.swift
//  ios-search-ads-sample
//
//  Created by Gareth on 6/15/16.
//

import UIKit

class ViewController: UIViewController {

    private enum AttributionButtonState {
        case ready
        case requesting
        case retry
        case completed
    }

    private let attributionButton = UIButton(type: .system)
    private lazy var attributionCoordinator = AttributionRequestCoordinator(
        client: AdServicesAttributionClient())
    private var lifecycleObservers: [NSObjectProtocol] = []

    override func viewDidLoad() {
        super.viewDidLoad()
        configureAttributionButton()
        attributionCoordinator.onStateChange = { [weak self] state in
            self?.applyAttributionButtonState(for: state, announce: true)
        }
        observeApplicationLifecycle()
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        attributionCoordinator.cancel()
    }

    deinit {
        attributionCoordinator.cancel()
        lifecycleObservers.forEach(NotificationCenter.default.removeObserver)
    }

    private func configureAttributionButton() {
        applyAttributionButtonState(.ready)
        attributionButton.addTarget(self, action: #selector(requestAttribution(_:)), for: .touchUpInside)
        attributionButton.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(attributionButton)

        NSLayoutConstraint.activate([
            attributionButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            attributionButton.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }

    private func applyAttributionButtonState(_ state: AttributionButtonState, announce: Bool = false) {
        switch state {
        case .ready:
            attributionButton.setTitle("Request Attribution", for: .normal)
            attributionButton.accessibilityLabel = "Request Attribution"
            attributionButton.accessibilityHint = "Requests local Search Ads attribution without storing results"
            attributionButton.isEnabled = true
        case .requesting:
            attributionButton.setTitle("Requesting Attribution...", for: .disabled)
            attributionButton.accessibilityLabel = "Requesting Attribution"
            attributionButton.accessibilityHint = "Attribution request is running locally without storing results"
            attributionButton.isEnabled = false
        case .retry:
            attributionButton.setTitle("Try Again", for: .normal)
            attributionButton.accessibilityLabel = "Try Attribution Again"
            attributionButton.accessibilityHint = "Previous local attribution request failed; double tap to retry"
            attributionButton.isEnabled = true
        case .completed:
            attributionButton.setTitle("Attribution Requested", for: .disabled)
            attributionButton.accessibilityLabel = "Attribution Requested"
            attributionButton.accessibilityHint = "Attribution request completed locally and the button is disabled"
            attributionButton.isEnabled = false
        }

        if announce {
            UIAccessibility.post(notification: .announcement, argument: attributionButton.accessibilityLabel)
        }
    }

    private func applyAttributionButtonState(
        for state: AttributionRequestCoordinator.State,
        announce: Bool
    ) {
        switch state {
        case .idle:
            applyAttributionButtonState(.ready, announce: announce)
        case .requesting:
            applyAttributionButtonState(.requesting, announce: announce)
        case .failed:
            applyAttributionButtonState(.retry, announce: announce)
        case .completed:
            applyAttributionButtonState(.completed, announce: true)
        }
    }

    private func observeApplicationLifecycle() {
        let center = NotificationCenter.default
        lifecycleObservers.append(center.addObserver(
            forName: UIApplication.didEnterBackgroundNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            self?.attributionCoordinator.cancel()
        })
        lifecycleObservers.append(center.addObserver(
            forName: UIApplication.willTerminateNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            self?.attributionCoordinator.cancel()
        })
    }

    @objc private func requestAttribution(_: UIButton) {
        attributionCoordinator.start()
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        if viewIfLoaded?.window == nil {
            attributionCoordinator.cancel()
        }
    }
}
