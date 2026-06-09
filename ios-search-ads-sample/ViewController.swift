//
//  ViewController.swift
//  ios-search-ads-sample
//
//  Created by Gareth on 6/15/16.
//

import UIKit
import iAd

class ViewController: UIViewController {

    private let attributionButton = UIButton(type: .system)
    private var attributionRequestInProgress = false
    private var attributionRequestCompleted = false

    override func viewDidLoad() {
        super.viewDidLoad()
        configureAttributionButton()
    }

    private func configureAttributionButton() {
        attributionButton.setTitle("Request Attribution", for: .normal)
        attributionButton.addTarget(self, action: #selector(requestAttribution(_:)), for: .touchUpInside)
        attributionButton.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(attributionButton)

        NSLayoutConstraint.activate([
            attributionButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            attributionButton.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }

    @objc private func requestAttribution(_: UIButton) {
        if attributionRequestInProgress || attributionRequestCompleted {
            return
        }

        attributionRequestInProgress = true
        attributionButton.setTitle("Requesting Attribution...", for: .disabled)
        attributionButton.isEnabled = false

        ADClient.shared().requestAttributionDetails { [weak self] attributeDetails, error in
            DispatchQueue.main.async { [weak self] in
                guard let strongSelf = self else {
                    return
                }

                strongSelf.attributionRequestInProgress = false
                if error != nil {
                    strongSelf.attributionButton.isEnabled = true
                    strongSelf.attributionButton.setTitle("Try Again", for: .normal)
                    return
                }

                if let attributionDict = attributeDetails?["Version3.1"] as? [String: AnyObject] {
                    if let searchAttribution = attributionDict["iad-attribution"] {
                        // Keep the attribution result local to this sample.
                        _ = searchAttribution
                    }
                }

                strongSelf.attributionRequestCompleted = true
                strongSelf.attributionButton.setTitle("Attribution Requested", for: .disabled)
            }
        }
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }


}
