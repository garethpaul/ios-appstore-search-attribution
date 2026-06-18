//
//  ViewController.swift
//  ios-search-ads-sample
//
//  Created by Gareth on 6/15/16.
//

import UIKit
import iAd

class ViewController: UIViewController {

    private enum AttributionButtonState {
        case ready
        case requesting
        case retry
        case completed
    }

    private let attributionButton = UIButton(type: .system)
    private var attributionRequestInProgress = false
    private var attributionRequestCompleted = false
    private var attributionRequestGeneration = 0
    private let attributionRequestTimeoutInterval: TimeInterval = 30.0
    private var attributionRequestTimeoutWorkItem: DispatchWorkItem?

    override func viewDidLoad() {
        super.viewDidLoad()
        configureAttributionButton()
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

    private func finishAttributionRequest(generation: Int, succeeded: Bool) {
        guard generation == attributionRequestGeneration,
              attributionRequestInProgress else {
            return
        }

        attributionRequestTimeoutWorkItem?.cancel()
        attributionRequestTimeoutWorkItem = nil
        attributionRequestInProgress = false

        if succeeded {
            attributionRequestCompleted = true
            applyAttributionButtonState(.completed, announce: true)
        } else {
            applyAttributionButtonState(.retry, announce: true)
        }
    }

    private func scheduleAttributionRequestTimeout(generation: Int) {
        let timeoutWorkItem = DispatchWorkItem { [weak self] in
            self?.finishAttributionRequest(generation: generation, succeeded: false)
        }
        attributionRequestTimeoutWorkItem = timeoutWorkItem
        DispatchQueue.main.asyncAfter(
            deadline: .now() + attributionRequestTimeoutInterval,
            execute: timeoutWorkItem)
    }

    @objc private func requestAttribution(_: UIButton) {
        if attributionRequestInProgress || attributionRequestCompleted {
            return
        }

        attributionRequestInProgress = true
        attributionRequestGeneration += 1
        let requestGeneration = attributionRequestGeneration
        applyAttributionButtonState(.requesting, announce: true)
        scheduleAttributionRequestTimeout(generation: requestGeneration)

        ADClient.shared().requestAttributionDetails { [weak self] attributeDetails, error in
            let requestSucceeded: Bool
            if error == nil,
               let attributionDict = attributeDetails?["Version3.1"] as? [String: AnyObject],
               let searchAttribution = attributionDict["iad-attribution"] as? Bool {
                // Keep the attribution result local to this sample.
                _ = searchAttribution
                requestSucceeded = true
            } else {
                requestSucceeded = false
            }

            DispatchQueue.main.async { [weak self] in
                self?.finishAttributionRequest(
                    generation: requestGeneration,
                    succeeded: requestSucceeded)
            }
        }
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }


}
