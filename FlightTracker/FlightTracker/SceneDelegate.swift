//
//  SceneDelegate.swift
//  FlightTracker
//
//  Created by Miha Strah on 10/07/2020.
//  Copyright © 2020 Miha Strah. All rights reserved.
//

import UIKit
import SwiftUI

class SceneDelegate: UIResponder, UIWindowSceneDelegate, UNUserNotificationCenterDelegate {
    
    
    //availible everywhere
    var userSavedFlights: UserSavedFlights = UserSavedFlights()
    
    var window: UIWindow?
    
    
    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {
        // Use this method to optionally configure and attach the UIWindow `window` to the provided UIWindowScene `scene`.
        // If using a storyboard, the `window` property will automatically be initialized and attached to the scene.
        // This delegate does not imply the connecting scene or session are new (see `application:configurationForConnectingSceneSession` instead).
        
        UNUserNotificationCenter.current().delegate = self
        //        load saved flights
        userSavedFlights.load()
        userSavedFlights.refresh()
        
        Timer.scheduledTimer(withTimeInterval: 61, repeats: true, block: { (timer) in
            self.userSavedFlights.refresh()
        })
        
        // Create the SwiftUI view that provides the window contents.
        let contentView = ContentView(currentTab: .savedFlights)
        
        
        // Use a UIHostingController as window root view controller.
        if let windowScene = scene as? UIWindowScene {
            let window = UIWindow(windowScene: windowScene)
            window.rootViewController = UIHostingController(rootView: contentView.environmentObject(userSavedFlights)) //we pass monitoredCodeshare environmental object to views
            self.window = window
            window.makeKeyAndVisible()
        }
        
    }
    
    func sceneDidDisconnect(_ scene: UIScene) {
        // Called as the scene is being released by the system.
        // This occurs shortly after the scene enters the background, or when its session is discarded.
        // Release any resources associated with this scene that can be re-created the next time the scene connects.
        // The scene may re-connect later, as its session was not neccessarily discarded (see `application:didDiscardSceneSessions` instead).
        userSavedFlights.save()
    }
    
    func sceneDidBecomeActive(_ scene: UIScene) {
        // Called when the scene has moved from an inactive state to an active state.
        // Use this method to restart any tasks that were paused (or not yet started) when the scene was inactive.
        
    }
    
    func sceneWillResignActive(_ scene: UIScene) {
        // Called when the scene will move from an active state to an inactive state.
        // This may occur due to temporary interruptions (ex. an incoming phone call).
        userSavedFlights.save()
    }
    
    func sceneWillEnterForeground(_ scene: UIScene) {
        // Called as the scene transitions from the background to the foreground.
        // Use this method to undo the changes made on entering the background.
    }
    
    func sceneDidEnterBackground(_ scene: UIScene) {
        // Called as the scene transitions from the foreground to the background.
        // Use this method to save data, release shared resources, and store enough scene-specific state information
        // to restore the scene back to its current state.
        userSavedFlights.save()
    }
    
    
    
    
    
    
    
    
    
    
    
    
    
    //    handling of received notification
    func userNotificationCenter(_ center: UNUserNotificationCenter, willPresent notification: UNNotification, withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void) {
        
        //refresh all flights
        userSavedFlights.refresh()
        
        // show the notification alert (banner), and with sound
        completionHandler([.alert, .sound])
    }
    
    // This function will be called right after user tap on the notification
    func userNotificationCenter(_ center: UNUserNotificationCenter, didReceive response: UNNotificationResponse, withCompletionHandler completionHandler: @escaping () -> Void) {
//        print("NOTIFICATION!")
//        print(response.notification)
        
        let userInfo = response.notification.request.content.userInfo
        
        guard
            let aps = userInfo["aps"] as? NSDictionary,
            let alert = aps["alert"] as? NSDictionary,
            let body = alert["body"] as? String,
            let title = alert["title"] as? String,
            let flightString = userInfo["flightString"] as? String,
            let dateString = userInfo["dateString"] as? String
        else {
//            print("notification error")
            return
        }
        
//        print("Title: \(title) \nBody:\(body)")
        
        
        userSavedFlights.selectedItem = userSavedFlights.search(flightString: flightString, dateString: dateString, update: true)
        
        
        userSavedFlights.refresh()
        
        window?.rootViewController?.dismiss(animated: true, completion: {
            let vc = ContentView.init(currentTab: .savedFlights)
            self.window?.rootViewController = UIHostingController(rootView:vc.environmentObject(self.userSavedFlights))
        })
        
        completionHandler()
    }
    
    
}

