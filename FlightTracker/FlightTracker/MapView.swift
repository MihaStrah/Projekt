//
//  MapView.swift
//  FlightTracker
//
//  Created by Miha Strah on 06/08/2020.
//  Copyright © 2020 Miha Strah. All rights reserved.
//

import MapKit
import SwiftUI

struct MapView: UIViewRepresentable {
    var annotations: [MKPointAnnotation]
    
    func updateUIView(_ mapView: MKMapView, context: Context){
        
        //assigning delegate
        mapView.delegate = context.coordinator
        
        //If you changing the Map Annotation then you have to remove old Annotations
        mapView.removeAnnotations(mapView.annotations)
        
        //        print(annotations.count)
        if annotations.count == 2 {
            
            mapView.addAnnotations(annotations)
            
            let pointA = annotations[0].coordinate
            let pointB = annotations[1].coordinate
            
            mapView.addOverlay(makeArcOverlay(pointA: pointA, pointB: pointB))
            
        }
        
        else if annotations.count == 1 {
            
            mapView.addAnnotations(annotations)
            
        }

    }
    
    
    
    func makeUIView(context: Context) -> MKMapView{
        let mapView = MKMapView(frame: .zero)
        mapView.setRegion(mapView.regionThatFits(calculateRegion()), animated: true)
        return mapView
    }
    
    func makeCoordinator() -> MapViewCoordinator{
        MapViewCoordinator(self)
    }
    
    
    func calculateRegion() -> MKCoordinateRegion {
        let coordinates = (annotations.map{$0.coordinate})
        let ((minLatitude, maxLatitude), (minLongitude, maxLongitude)) = coordinates.reduce(((Double.greatestFiniteMagnitude, Double.leastNormalMagnitude),(Double.greatestFiniteMagnitude, Double.leastNormalMagnitude))) { r, c in
            (
                (min(c.latitude,r.0.0), max(c.latitude, r.0.1)),
                (min(c.longitude, r.1.0), max(c.longitude, r.1.1))
            )
        }
        let latitudeDelta = (((maxLatitude-minLatitude) < 0) ? (max((maxLatitude-minLatitude)*1.3, -85.0)) : (min((maxLatitude-minLatitude)*1.3, 85.0)))
        let longitudeDelta = (((maxLongitude-minLongitude) < 0) ? (max((maxLongitude-minLongitude)*1.3, -180.0)) : (min((maxLongitude-minLongitude)*1.3, 180.0)))
        let span = MKCoordinateSpan(latitudeDelta: latitudeDelta, longitudeDelta: longitudeDelta)
        //        let center = CLLocationCoordinate2D(latitude: ((maxLatitude+minLatitude)/2), longitude: ((maxLongitude-minLongitude)/2))
        //
        
        //middle location between airports
            let center = coordinates[0].middleLocationWith(location: coordinates[1])
        let region = MKCoordinateRegion(center: center, span: span)
        return region
    }
    
    func makeArcOverlay(pointA: CLLocationCoordinate2D, pointB: CLLocationCoordinate2D) -> ArcOverlay {
        let arc = ArcOverlay(origin: pointA, destination: pointB,
                             style: LineOverlayStyle(strokeColor: .systemTeal, lineWidth: 4, alpha: 1))
        arc.radiusMultiplier = 1.0
        return arc
    }
}


class MapViewCoordinator: NSObject, MKMapViewDelegate {
    var mapViewController: MapView
    
    init(_ control: MapView) {
        self.mapViewController = control
    }
    //MKMarkerAnnotationView
    internal func mapView(_ mapView: MKMapView, viewFor
                            annotation: MKAnnotation) -> MKAnnotationView?{


        
//        mapView.dequeueReusableAnnotationView(withIdentifier: "customView")
        
        
        if annotation.subtitle == "Arrival Airport" {
            let annotationView = MKMarkerAnnotationView(annotation: annotation, reuseIdentifier: "ArrAirportView")
            annotationView.displayPriority = .defaultHigh
            annotationView.glyphImage = UIImage(named: "arrival")
            annotationView.titleVisibility = .visible
            annotationView.subtitleVisibility = .hidden
            return annotationView
        }
        else if annotation.subtitle == "Departure Airport" {
            let annotationView = MKMarkerAnnotationView(annotation: annotation, reuseIdentifier: "DepAirportView")
            annotationView.displayPriority = .defaultHigh
            annotationView.glyphImage = UIImage(named: "departure")
            annotationView.titleVisibility = .visible
            annotationView.subtitleVisibility = .hidden
            return annotationView
        }
        
        
        //nothing
        else {
            let annotationView = MKAnnotationView(annotation: annotation, reuseIdentifier: nil)
            return annotationView
        }
           
    }
    
    
    
    func mapView(_: MKMapView, rendererFor overlay: MKOverlay) -> MKOverlayRenderer {
        //ArcOverlay
        if let lineOverlay = overlay as? LineOverlay {
            return MapLineOverlayRenderer(lineOverlay)
        }
        
        return MKOverlayRenderer(overlay: overlay)
    }

    
}


extension CLLocationCoordinate2D {
    // MARK: CLLocationCoordinate2D+MidPoint
    func middleLocationWith(location:CLLocationCoordinate2D) -> CLLocationCoordinate2D {
        
        let lon1 = longitude * Double.pi / 180
        let lon2 = location.longitude * Double.pi / 180
        let lat1 = latitude * Double.pi / 180
        let lat2 = location.latitude * Double.pi / 180
        let dLon = lon2 - lon1
        let x = cos(lat2) * cos(dLon)
        let y = cos(lat2) * sin(dLon)
        
        var lat3 = atan2( sin(lat1) + sin(lat2), sqrt((cos(lat1) + x) * (cos(lat1) + x) + y * y) )
        var lon3 = lon1 + atan2(y, cos(lat1) + x)
        
        lat3 = lat3 * 180 / Double.pi
        lon3 = (lon3 * 180 / Double.pi)
        //        print(lat3)
        //        print(lon3)
        
        if lat3 > 85.0 {
            lat3 = -85.0 - (85.0 - lat3)
        }
        if lat3 < -85.0 {
            lat3 = 85.0 - (-85.0 - lat3)
        }
        if lon3 > 180.0 {
            lon3 = -180 - (180.0 - lon3)
        }
        if lon3 < -180.0 {
            lon3 = 180 - (-180.0 - lon3)
        }
        //        print(lat3)
        //        print(lon3)
        let center:CLLocationCoordinate2D = CLLocationCoordinate2DMake(lat3, lon3)
        //        print(center)
        return center
    }
}

