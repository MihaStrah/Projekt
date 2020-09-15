//
//  AircraftMapView.swift
//  FlightTracker
//
//  Created by Miha Strah on 28/08/2020.
//  Copyright © 2020 Miha Strah. All rights reserved.
//

import SwiftUI
import MapKit

struct AircraftMapView: View {
    
    static let taskDateFormat: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateStyle = .long
        formatter.timeStyle = .long
        return formatter
    }()
    
    var flightStatusObject: FlightStatusObject
    var annotations: [MKPointAnnotation] = []
    
    
    init(flightStatusObject: FlightStatusObject) {
        self.flightStatusObject = flightStatusObject
        self.annotations = self.setAirplane()
    }
    
    
    @State var timer: Timer?
    
    var body: some View {
        
        VStack(alignment: .leading) {
            VStack(alignment: .leading, spacing: 5){
            Text("Current Aircraft Location")
                .font(.headline)
                .foregroundColor(/*@START_MENU_TOKEN@*/.blue/*@END_MENU_TOKEN@*/)
            Text("Registration: \(flightStatusObject.flightStatus?.aircraftreg ?? "/")")
                .font(.caption)
                .foregroundColor(Color("ColorText1"))
                if ((flightStatusObject.aircraftLocation?.updated != nil && flightStatusObject.aircraftLocation?.latitude != nil && ((flightStatusObject.aircraftLocation?.updated)! > Date().addingTimeInterval(-120)))) {
                Text("Last updated \(flightStatusObject.aircraftLocation!.updated, formatter: Self.taskDateFormat)")
                .font(.caption)
                    .foregroundColor(Color("ColorText1"))
                }
                else {
                    Text("Flight not found")
                        .foregroundColor(Color("ColorText1"))
                        .font(.caption)
                }
            }.padding(.top, 15)
            .padding(.leading, 15)
        
        MapViewAircraft(annotations: annotations).frame(minWidth: 50, maxWidth: .infinity, minHeight: 300, maxHeight: .infinity, alignment: .center)
        }.edgesIgnoringSafeArea(.bottom)
        .onAppear {
            guard timer == nil else { return }
            self.timer =  Timer.scheduledTimer(withTimeInterval: 10, repeats: true, block: { (timer) in
                self.flightStatusObject.getAircraftLocation { () in
                    //
                }
            })
            
        }
        .onDisappear(){
            timer?.invalidate()
            self.timer = nil
        }
                    
    }
    
    func setAirplane() -> [MKPointAnnotation] {
        var annotations: [MKPointAnnotation] = []
        
        if ((flightStatusObject.aircraftLocation != nil) && ((flightStatusObject.aircraftLocation?.updated)! > Date().addingTimeInterval(-120)) && (flightStatusObject.aircraftLocation?.latitude != nil) && (flightStatusObject.aircraftLocation?.longitude != nil)) {
            var aircraft: MKPointAnnotation {
                let annotation = MKPointAnnotation()
                annotation.title = "Aircraft"
                annotation.subtitle = String((flightStatusObject.aircraftLocation?.truetrack ?? 0))
                let latitude = (flightStatusObject.aircraftLocation?.latitude)
                let longitude = (flightStatusObject.aircraftLocation?.longitude)
                annotation.coordinate = CLLocationCoordinate2D(latitude: latitude!, longitude: longitude!)
                return annotation
            }
        annotations.append(aircraft)
        }
        
        return annotations
    }
    
    
    
}

//struct AirportMapView_Previews: PreviewProvider {
//    static var previews: some View {
//        AirportMapView()
//    }
//}


