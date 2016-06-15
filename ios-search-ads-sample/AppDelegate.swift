//
//  AppDelegate.swift
//  ios-search-ads-sample
//
//  Created by Gareth on 6/15/16.
//

import UIKit
import iAd

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {

    var window: UIWindow?

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [NSObject: AnyObject]?) -> Bool {
        // Override point for customization after application launch.
        
        // Iterate through request attribution details
        //
        ADClient.shared().requestAttributionDetails {
            (attributeDetails:[NSObject:AnyObject]?, error: NSError?) in
            //
            if error == nil {
                // process attribute details
                // v3
                // TBD: Details on the spec
                if let v3: AnyObject = attributeDetails?["Version3.1"] {
                    if let attributionDict = v3 as? [String : AnyObject]{
                        // iterate through protocol
                        if let searchAttribution: AnyObject = attributionDict["iad-attribution"] {
                            // take the bool value and store somewhere or provide different experience
                            print(searchAttribution)
                        }
                    }
                }
            }
        }
        
        ADClient.shared().add(toSegments: ["installed"], replaceExisting: true)
        return true
    }
}

