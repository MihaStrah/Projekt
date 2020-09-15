//
//  AirportMapView.swift
//  FlightTracker
//
//  Created by Miha Strah on 06/08/2020.
//  Copyright © 2020 Miha Strah. All rights reserved.
//

import SwiftUI
import MapKit

struct AirportMapView: View {
    
    var flightStatusObject: FlightStatusObject
    var annotations: [MKPointAnnotation] = []
    
    init(flightStatusObject: FlightStatusObject) {
        self.flightStatusObject = flightStatusObject
        self.annotations = self.setAirports()
    }
    
    var body: some View {
        MapView(annotations: annotations).frame(minWidth: 50, maxWidth: .infinity, minHeight: 300, maxHeight: .infinity, alignment: .center)
    }
    
    func setAirports() -> [MKPointAnnotation] {
        var annotations: [MKPointAnnotation] = []
        var depAirport: MKPointAnnotation {
            let annotation = MKPointAnnotation()
            annotation.title = "\(flightStatusObject.flightStatus?.depairport ?? "") (\(flightStatusObject.airportInfo?.depAirport?.airportName ?? ""))"
            annotation.subtitle = "Departure Airport"
            let latitude = flightStatusObject.airportInfo?.depAirport?.latitude
            let longitude = flightStatusObject.airportInfo?.depAirport?.longitude
            annotation.coordinate = CLLocationCoordinate2D(latitude: latitude!, longitude: longitude!)
            return annotation
        }
        var arrAirport: MKPointAnnotation {
            let annotation = MKPointAnnotation()
            annotation.title = "\(flightStatusObject.flightStatus?.arrairport ?? "") (\(flightStatusObject.airportInfo?.arrAirport?.airportName ?? ""))"
            annotation.subtitle = "Arrival Airport"
            let latitude = flightStatusObject.airportInfo?.arrAirport?.latitude
            let longitude = flightStatusObject.airportInfo?.arrAirport?.longitude
            annotation.coordinate = CLLocationCoordinate2D(latitude: latitude!, longitude: longitude!)
            return annotation
        }
        annotations.append(depAirport)
        annotations.append(arrAirport)
        
        
        
        return annotations
    }
    
    
    
}

//struct AirportMapView_Previews: PreviewProvider {
//    static var previews: some View {
//        AirportMapView()
//    }
//}


