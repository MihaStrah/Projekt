//
//  ContentView.swift
//  FlightTracker
//
//  Created by Miha Strah on 10/07/2020.
//  Copyright © 2020 Miha Strah. All rights reserved.
//


//Color(#colorLiteral(red: 0, green: 0, blue: 0, alpha: 1))

import SwiftUI


struct ContentView: View {
    
    
    @State var showingFlightView = false
    @State public var showingNewFlightView = false
    @EnvironmentObject var userSavedFlights: UserSavedFlights
    @GestureState private var isTapped = false
    
    @State var currentTab: Tab
    
    var body: some View {
        ZStack() {
            MainView(currentTab: self.$currentTab)
        }
        
    }
    
    func setTab(tab: Tab) {
        self.currentTab = tab
    }
    
}


