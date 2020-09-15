//
//  ContentView.swift
//  FlightTrackerAppClip
//
//  Created by Miha Strah on 01/09/2020.
//  Copyright © 2020 Miha Strah. All rights reserved.
//

import SwiftUI

struct ContentView: View {
    var body: some View {
        ZStack(){
        FlightSearchView()
        }.edgesIgnoringSafeArea(.bottom)
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
