//
//  ExistingFlightView.swift
//  FlightTracker
//
//  Created by Miha Strah on 24/07/2020.
//  Copyright © 2020 Miha Strah. All rights reserved.
//

import SwiftUI

struct ExistingFlightView: View {
    
    @ObservedObject var flightStatusObject: FlightStatusObject
    
    
    
    init(flightStatusObject: FlightStatusObject){
        self.flightStatusObject = flightStatusObject
    }
    
    var body: some View {
        ScrollView() {
            VStack(spacing: 0) {
                
                ExistingFlightInfoView(flightStatusObject: flightStatusObject)
                    //                    .clipped() //PERFORMANCE PROBLEMS!
                    //                    .shadow(color: Color("ColorShadow"), radius: 5, x: 0, y: 0)
                    //.shadow(color: Color(.red), radius: 35, x: 0, y: 0)
                    //                    .padding(.top, 10)
                    .padding(.horizontal, 10)
                
            }.animation(.none)
        }.offset(x: 0, y: 0)
        .background(Color("ColorGray1"))
        
        //
        //        .navigationBarColor(flightViewUIColor(flightStatusObject: self.flightStatusObject))
        .navigationBarTitle("Flight \(self.flightStatusObject.savedFlight?.airlineid ?? "")\(self.flightStatusObject.savedFlight?.flightnumber ?? "")", displayMode: .automatic)
        
        
        
    }
}

