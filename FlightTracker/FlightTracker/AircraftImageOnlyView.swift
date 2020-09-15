//
//  AircraftImageOnlyView.swift
//  FlightTracker
//
//  Created by Miha Strah on 21/07/2020.
//  Copyright © 2020 Miha Strah. All rights reserved.
//

import SwiftUI

struct AircraftImageOnlyView: View {
    
    @ObservedObject var flightStatusObject: FlightStatusObject
    
    var body: some View {
        Image(uiImage: self.flightStatusObject.urlImageModel!.image ?? UIImage(imageLiteralResourceName: "airplane_stock"))
            .resizable()
            .aspectRatio(contentMode: .fit)
            .transition(/*@START_MENU_TOKEN@*/.identity/*@END_MENU_TOKEN@*/)
            .frame(width: (UIScreen.main.bounds.width), height: (UIScreen.main.bounds.width), alignment: .trailing)
            .clipped()
    }
}

struct AircraftImageOnlyView_Previews: PreviewProvider {
    static var previews: some View {
        AircraftImageOnlyView(flightStatusObject: FlightStatusObject())
    }
}
