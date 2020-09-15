//
//  AsyncImageLoader.swift
//  FlightTracker
//
//https://schwiftyui.com/swiftui/downloading-and-caching-images-in-swiftui/

import SwiftUI
import Foundation


//not used yet ->
//struct UrlImageView: View {
//    @ObservedObject var urlImageModel: UrlImageModel
//
//    var defaultImage: UIImage
//
//    init(urlString: String?, defaultImage: String?) {
//        self.urlImageModel = UrlImageModel(urlString: urlString)
//        self.defaultImage = UIImage(named: defaultImage!)!
//    }
//
//    var body: some View {
//        Image(uiImage: urlImageModel.image ?? self.defaultImage)
//            .resizable()
//            .scaledToFit()
//            .frame(width: 100, height: 100)
//    }
//}
//<- not used yet

class UrlImageModel: ObservableObject {
    @Published var image: UIImage?
    var urlString: String?
    
    
    var imageCache = ImageCache.getImageCache()
    
    init(urlString: String?) {
        self.urlString = urlString
        loadImage()
    }
    
    func loadImage() {
        DispatchQueue.global(qos: .userInitiated).async() {
            if self.loadImageFromCache() {
                return
            }
            self.loadImageFromUrl()
        }
        
    }
    
    func loadImageFromCache() -> Bool {
        guard let urlString = urlString else {
            return false
        }
        
        guard let cacheImage = imageCache.get(forKey: urlString) else {
            return false
        }
        withAnimation(.spring()){
            DispatchQueue.main.async() {
                withAnimation(.spring()){
                    self.image = cacheImage
                }
            }
        }
        return true
    }
    
    func loadImageFromUrl() {
        guard let urlString = urlString else {
            return
        }
        
        let url = URL(string: urlString)!
//        print("!!!!!!!! getting new image")
        let task = URLSession.shared.dataTask(with: url, completionHandler: getImageFromResponse(data:response:error:))
        task.resume()
    }
    
    
    func getImageFromResponse(data: Data?, response: URLResponse?, error: Error?) {
        
        guard error == nil else {
//            print("Error: \(error!)")
            return
        }
        guard let data = data else {
//            print("No data found")
            return
        }
        
        
        guard let loadedImage = UIImage(data: data) else {
            return
        }
        self.imageCache.set(forKey: self.urlString!, image: loadedImage)
        DispatchQueue.main.async() {
            withAnimation(.spring()){
                self.image = loadedImage
            }
        }
    }
    
}


class ImageCache {
    var cache = NSCache<NSString, UIImage>()
    
    func get(forKey: String) -> UIImage? {
        return cache.object(forKey: NSString(string: forKey))
    }
    
    func set(forKey: String, image: UIImage) {
        cache.setObject(image, forKey: NSString(string: forKey))
    }
}

extension ImageCache {
    private static var imageCache = ImageCache()
    static func getImageCache() -> ImageCache {
        return imageCache
    }
}
