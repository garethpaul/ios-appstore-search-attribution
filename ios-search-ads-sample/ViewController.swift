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

    @objc private func requestAttribution(_: UIButton) {
        if attributionRequestInProgress || attributionRequestCompleted {
            return
        }

        attributionRequestInProgress = true
        attributionRequestGeneration += 1
        let requestGeneration = attributionRequestGeneration
        applyAttributionButtonState(.requesting, announce: true)

        ADClient.shared().requestAttributionDetails { [weak self] attributeDetails, error in
            DispatchQueue.main.async { [weak self] in
                guard let strongSelf = self else {
                    return
                }
                guard requestGeneration == strongSelf.attributionRequestGeneration,
                      strongSelf.attributionRequestInProgress else {
                    return
                }

                strongSelf.attributionRequestInProgress = false
                guard error == nil,
                      let attributionDict = attributeDetails?["Version3.1"] as? [String: AnyObject],
                      let searchAttribution = attributionDict["iad-attribution"] as? Bool else {
                    strongSelf.applyAttributionButtonState(.retry, announce: true)
                    return
                }

                // Keep the attribution result local to this sample.
                _ = searchAttribution

                strongSelf.attributionRequestCompleted = true
                strongSelf.applyAttributionButtonState(.completed, announce: true)
            }
        }
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }


}
