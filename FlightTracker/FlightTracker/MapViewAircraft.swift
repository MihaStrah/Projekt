//
//  MapViewAircraft.swift
//  FlightTracker
//
//  Created by Miha Strah on 28/08/2020.
//  Copyright © 2020 Miha Strah. All rights reserved.
//
import MapKit
import SwiftUI

struct MapViewAircraft: UIViewRepresentable {
    var annotations: [MKPointAnnotation]
    
    
    func updateUIView(_ mapView: MKMapView, context: Context){
        
        //assigning delegate
        mapView.delegate = context.coordinator
        
        //If you changing the Map Annotation then you have to remove old Annotations
        mapView.removeAnnotations(mapView.annotations)
                
        if annotations.count == 1 {
            mapView.addAnnotations(annotations)
        }
        
    }
    
    func makeUIView(context: Context) -> MKMapView{
        let mapView = MKMapView(frame: .zero)
        mapView.setRegion(mapView.regionThatFits(calculateRegion()), animated: true)
        return mapView
    }
    
    func makeCoordinator() -> MapViewCoordinatorAircraft{
        MapViewCoordinatorAircraft(self)
    }
    
    
    func calculateRegion() -> MKCoordinateRegion {
        let coordinates = (annotations.map{$0.coordinate})
        let span = MKCoordinateSpan(latitudeDelta: 10, longitudeDelta: 10)
        let center = coordinates[0]
        let region = MKCoordinateRegion(center: center, span: span)
        return region
    }
    
}


class MapViewCoordinatorAircraft: NSObject, MKMapViewDelegate {
    var mapViewController: MapViewAircraft
    
    init(_ control: MapViewAircraft) {
        self.mapViewController = control
    }
    
    //MKMarkerAnnotationView
    internal func mapView(_ mapView: MKMapView, viewFor
                            annotation: MKAnnotation) -> MKAnnotationView?{


        if annotation.title == "Aircraft" {
            let annotationView = MKAnnotationView(annotation: annotation, reuseIdentifier: nil)
            guard let trackString = annotation.subtitle! else { return annotationView }
            let track = Double(trackString)!
            let image = UIImage(systemName: "airplane")!.rotate(radians: ((Float(track) - 90) * .pi / 180))!.imageWithColor(color: UIColor(named: "ColorAircraft")!)
            annotationView.image = image
            annotationView.contentMode = .scaleAspectFill
            annotationView.displayPriority = .required
            annotationView.setSelected(true, animated: true)
            if #available(iOS 14.0, *) {
                annotationView.zPriority = .max
            } else {
                // Fallback on earlier versions
            }
            annotationView.canShowCallout = false
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




//image rotate
extension UIImage {
    func rotate(radians: Float) -> UIImage? {
        var newSize = CGRect(origin: CGPoint.zero, size: self.size).applying(CGAffineTransform(rotationAngle: CGFloat(radians))).size
        // Trim off the extremely small float value to prevent core graphics from rounding it up
        newSize.width = floor(newSize.width)
        newSize.height = floor(newSize.height)

        UIGraphicsBeginImageContextWithOptions(newSize, false, self.scale)
        let context = UIGraphicsGetCurrentContext()!

        // Move origin to middle
        context.translateBy(x: newSize.width/2, y: newSize.height/2)
        // Rotate around middle
        context.rotate(by: CGFloat(radians))
        
        // Draw the image at its center
        self.draw(in: CGRect(x: -self.size.width/2, y: -self.size.height/2, width: self.size.width, height: self.size.height))

        let newImage = UIGraphicsGetImageFromCurrentImageContext()
        UIGraphicsEndImageContext()

        return newImage
    }
    
    
        func imageWithColor(color: UIColor) -> UIImage {
            UIGraphicsBeginImageContextWithOptions(self.size, false, self.scale)
            color.setFill()

            let context = UIGraphicsGetCurrentContext()
            context?.translateBy(x: 0, y: self.size.height)
            context?.scaleBy(x: 1.0, y: -1.0)
            context?.setBlendMode(CGBlendMode.normal)

            let rect = CGRect(origin: .zero, size: CGSize(width: self.size.width, height: self.size.height))
            context?.clip(to: rect, mask: self.cgImage!)
            context?.fill(rect)

            let newImage = UIGraphicsGetImageFromCurrentImageContext()
            UIGraphicsEndImageContext()

            return newImage!
        }
    


}


