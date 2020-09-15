//
//  FlightStatus.swift
//  FlightTracker
//
//  Created by Miha Strah on 13/07/2020.
//  Copyright © 2020 Miha Strah. All rights reserved.
//

import Foundation
import Combine
import SwiftUI

let queue = DispatchQueue(label: "getting-data")

class UserSavedFlights: ObservableObject {
    @Published var userSavedFlightStatusObjects: [FlightStatusObject] = []
    
    @Published var selectedItem: UUID?
    
    func reset() {
        let ifreturn = self.userSavedFlightStatusObjects
        self.userSavedFlightStatusObjects.removeAll()
        
        if (DAKeychain.shared["ApplePushToken"] != nil) {
        self.unregisterALLForNotifications(completion: { status in
            if status == "OK" {
                self.save()
                //                print("unregister all ok")
            }
            else {
                DispatchQueue.main.async { self.userSavedFlightStatusObjects = ifreturn }
                self.save()
                //                print("unregister all NOT ok")
            }
        })
        }
            
        
        
        
    }
    
    func remove(object: FlightStatusObject) {
        DispatchQueue.global(qos: .userInteractive).async {
            let ifreturn = self.userSavedFlightStatusObjects[(self.userSavedFlightStatusObjects.firstIndex(of: object)!)]
            self.userSavedFlightStatusObjects.remove(at: self.userSavedFlightStatusObjects.firstIndex(of: object)!)
            ifreturn.unregisterForNotifications(completion: { status in
                if status == "OK" {
                    self.save()
                    //                print("unregister ok")
                }
                else {
                    DispatchQueue.main.async { self.userSavedFlightStatusObjects.append(ifreturn) }
                    self.save()
                    //                print("unregister NOT ok")
                }
            })
        }
        
    }
    
    func removeOnIndexSet(atOffsets: IndexSet) {
        DispatchQueue.global(qos: .userInteractive).async {
            let indexes = Array(atOffsets)
            for index in indexes {
                let ifreturn = self.userSavedFlightStatusObjects[index]
                
                DispatchQueue.main.async { self.userSavedFlightStatusObjects.remove(at: index) }
                ifreturn.unregisterForNotifications(completion: { status in
                    if status == "OK" {
                        self.save()
                        //                print("unregister ok")
                    }
                    else {
                        DispatchQueue.main.async { self.userSavedFlightStatusObjects.append(ifreturn) }
                        self.save()
                        //                print("unregister NOT ok")
                    }
                })
            }
        }
    }
    
    
    func add(flightStatusObject: FlightStatusObject) {
        userSavedFlightStatusObjects.insert(flightStatusObject, at: 0)
        //        userSavedFlightStatusObjects.append(flightStatusObject)
        self.save()
        //flightStatusObject.getStatus()
    }
    
    func refresh() {
        for object in userSavedFlightStatusObjects {
            if object.lastUpdated == nil {
                object.getStatus(update: true)
            }
            else {
                if (object.flightStatus?.depscheduled)! > Date().addingTimeInterval(-86400) {
                    if (object.lastUpdated!.addingTimeInterval(55) < Date()) {
                        object.getStatus(update: true)
                    }
                }
                else {
                    if (object.lastUpdated!.addingTimeInterval(3595) < Date()) {
                        object.getStatus(update: true)
                    }
                }
            }
        }
    }
    
    
    func search(flightString: String, dateString: String, update: Bool) -> UUID? {
        //        print(flightString)
        //        print(dateString)
        for object in userSavedFlightStatusObjects {
            let searchString = "\(object.flightStatus?.airlineid ?? "")\(object.flightStatus?.flightnumber ?? "")"
            //            print(searchString)
            if (searchString.lowercased() == flightString.lowercased()) {
                let searchDateString = object.flightStatus?.depscheduledDateString
                //                print(dateString)
                //                print(searchDateString)
                if (dateString == searchDateString) {
                    if update {
                        object.getStatus(update: true)
                    }
                    return object.id
                }
            }
        }
        return nil
        
    }
    
    
    func save() {
        DispatchQueue.global(qos: .background).async {
            let encoder = JSONEncoder()
            
            encoder.dateEncodingStrategy = .custom({ (date, encoder) in
                let formatter = DateFormatter()
                formatter.dateFormat = "yyyy-MM-dd'T'HH:mm"
                let stringData = formatter.string(from: date)
                var container = encoder.singleValueContainer()
                try container.encode(stringData)
            })
            if let encoded = try? encoder.encode(self.userSavedFlightStatusObjects) {
                UserDefaults.standard.set(encoded, forKey: "userSavedFlightStatusObjects")
                //            print("saved")
                //            print(encoded)
            }
        }
    }
    
    func load() {
        //        self.reset()
        //        self.save()
        if let data = UserDefaults.standard.data(forKey: "userSavedFlightStatusObjects") {
//            let dataString =  String(data: data, encoding: String.Encoding.utf8)
            //            print(dataString)
            
            let decoder = JSONDecoder()
            let dateFormatter1 = DateFormatter()
            dateFormatter1.dateFormat = "yyyy-MM-dd'T'HH:mm"
            decoder.dateDecodingStrategyFormatters = [dateFormatter1]
            
            do {
                let decoded = try decoder.decode([FlightStatusObject].self, from: data)
                self.userSavedFlightStatusObjects = decoded
                //                    print("loaded")
            } catch {
                //                print(error)
                self.userSavedFlightStatusObjects = []
                //                        print("NOT loaded")
            }
            
            
            
        }
        
    }
    
    func unregisterALLForNotifications( completion: @escaping (String) -> () ) {
        getLetApiToken { (tokenString) in
            guard let url = URL(string: "https://letinfo.duckdns.org/notifications/unregister") else { return }
            //            print(url)
            var request = URLRequest(url: url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 5.0)
            request.httpMethod = "POST"
            request.addValue((tokenString), forHTTPHeaderField: "x-access-tokens")
            
            let dateFormatter1 = DateFormatter()
            dateFormatter1.dateFormat = "yyyy-MM-dd'"
            
            if let token = DAKeychain.shared["ApplePushToken"] {
                
                let parameters: [String: Any] = [
                    "token": token,
                    "date": dateFormatter1.string(from: Date()),
                    "flightnumber": "000",
                    "airline": "ALL"
                ]
                
                request.httpBody = parameters.percentEncoded()
                
                //            print(parameters)
                
                let jsonDecoder = JSONDecoder()
                
                URLSession.shared.dataTask(with: request) { (data, response, error) in
                    
                    
                    if error != nil {
                        if error?._code == -1001 {
                            //                            print("notificationunregisterALL status code -1001 timeout")
                            DispatchQueue.main.async { completion("ERROR") }
                        }
                    } else {
                        if let httpRes = response as? HTTPURLResponse {
                            if httpRes.statusCode == 200 {
                                //                                print("notificationunregisterALL status ok ...")
                                let apiResponse = try! jsonDecoder.decode(NotificationApiResponse.self, from: data!)
                                //                                let dataString =  String(data: data!, encoding: String.Encoding.utf8)
                                //                                print(dataString)
                                //                                print("notificationunregisterALL status code 200 OK")
                                
                                if apiResponse.info == "OK" {
                                    //                                    print("notificationunregisterALL OK")
                                    DispatchQueue.main.async { completion("OK") }
                                }
                                else {
                                    DispatchQueue.main.async { completion("ERROR") }
                                    //                                    print("notificationunregisterALL NOT OK: \(apiResponse.info)")
                                }
                                
                                
                            }
                            else {
                                //Other code 404,....
                                //                                print("notificationunregisterALL other status code")
                                DispatchQueue.main.async { completion("ERROR") }
                            }
                        }
                        //                        print("notificationunregisterALL smo tu?")
                    }
                    
                    
                }.resume()
            }
            else {
                print("getting token from keychain error")
                completion("ERROR")
            }
        }
    }
    
    
    
    
    
}

class FlightStatusObject: ObservableObject, Identifiable, Codable, Equatable {
    static func == (lhs: FlightStatusObject, rhs: FlightStatusObject) -> Bool {
        lhs.savedFlight?.airlineid == rhs.savedFlight?.airlineid && lhs.savedFlight?.flightnumber == rhs.savedFlight?.flightnumber && lhs.savedFlight?.date == rhs.savedFlight?.date
    }
    
    
    enum CodingKeys: CodingKey {
        case savedFlight, flightStatus, imageData, codeshareData, airportInfo, airlineInfo, aircraftInfo, stat7Day, stat30Day, statDays, lastUpdated, notifications, aircraftLocation
    }
    
    required init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        
        savedFlight = try container.decodeIfPresent(SavedFlightDataModel.self, forKey: .savedFlight)
        flightStatus = try container.decodeIfPresent(FlightStatusDataModel.self, forKey: .flightStatus)
        imageData = try container.decodeIfPresent(ImageData.self, forKey: .imageData)
        codeshareData = try container.decodeIfPresent(CodeshareDataModel.self, forKey: .codeshareData)
        airportInfo = try container.decodeIfPresent(AirportInfoModel.self, forKey: .airportInfo)
        airlineInfo = try container.decodeIfPresent(AirlineInfoModel.self, forKey: .airlineInfo)
        aircraftInfo = try container.decodeIfPresent(AircraftInfoModel.self, forKey: .aircraftInfo)
        stat7Day = try container.decodeIfPresent(StatModel.self, forKey: .stat7Day)
        stat30Day = try container.decodeIfPresent(StatModel.self, forKey: .stat30Day)
        statDays = try container.decodeIfPresent(StatDaysModel.self, forKey: .statDays)
        
        aircraftLocation = try container.decodeIfPresent(AircraftLocationModel.self, forKey: .aircraftLocation)
        
        lastUpdated = try container.decodeIfPresent(Date.self, forKey: .lastUpdated)
        notifications = try container.decodeIfPresent(Bool.self, forKey: .notifications) ?? false
        
        
        searchEnded = true
        searchOK = true
        
        
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        
        try container.encode(savedFlight, forKey: .savedFlight)
        try container.encode(flightStatus, forKey: .flightStatus)
        try container.encode(imageData, forKey: .imageData)
        try container.encode(codeshareData, forKey: .codeshareData)
        try container.encode(airportInfo, forKey: .airportInfo)
        try container.encode(airlineInfo, forKey: .airlineInfo)
        try container.encode(aircraftInfo, forKey: .aircraftInfo)
        try container.encode(stat7Day, forKey: .stat7Day)
        try container.encode(stat30Day, forKey: .stat30Day)
        try container.encode(statDays, forKey: .statDays)
        try container.encode(lastUpdated, forKey: .lastUpdated)
        try container.encode(notifications, forKey: .notifications)
        try container.encode(aircraftLocation, forKey: .aircraftLocation)
        
    }
    
    init() {
        //        nothing
    }
    
    
    //for object changing detection (for urlImageModel = actual image)
    private var cancellables = Set<AnyCancellable>()
    
    
    let id = UUID()
    @Published var savedFlight: SavedFlightDataModel?
    @Published var flightStatus: FlightStatusDataModel?
    
    
    
    @Published var searchInProgress = false
    @Published var searchEnded = false
    @Published var searchOK = false
    
    
    @Published var lastUpdated: Date?
    
    @Published var imageData: ImageData?
    @Published var urlImageModel: UrlImageModel?
    
    @Published var codeshareData: CodeshareDataModel?
    
    
    
    @Published var airportInfo: AirportInfoModel?
    @Published var airlineInfo: AirlineInfoModel?
    @Published var aircraftInfo: AircraftInfoModel?
    
    
    @Published var stat7Day: StatModel?
    @Published var stat30Day: StatModel?
    @Published var statDays: StatDaysModel?
    
    @Published var aircraftLocation: AircraftLocationModel?
    
    @Published var notifications = false
    
    
    func notificationToggle() {
        notifications.toggle()
        if notifications {
            self.registerForNotifications(completion: {
                //                print("this is ended")
            })
        }
        else {
            self.unregisterForNotifications(completion: { status in
                //                print("status: \(status)")
                //                print("this is ended")
            })
        }
    }
    
    
    
    
    func reset() {
        self.searchInProgress = false
        self.searchEnded = false
        self.searchOK = false
        self.flightStatus = nil
        self.imageData = nil
        self.urlImageModel = nil
        self.codeshareData = nil
        self.airportInfo = nil
        self.airlineInfo = nil
        self.aircraftInfo = nil
        self.stat7Day = nil
        self.stat30Day = nil
        self.statDays = nil
        self.notifications = false
        self.aircraftLocation = nil
    }
    
    func getStatus(update: Bool) {
        
        
        self.searchInProgress = true
        self.searchEnded = false
        
        if !(update) {
            self.searchOK = false
        }
        
        let oldRegistration = self.flightStatus?.aircraftreg

        self.getFlightStatus() { response in
            DispatchQueue.main.async {
                self.searchInProgress = false
                self.searchEnded = true
                
                if response.depscheduledUTC != nil {
                    self.flightStatus = response
                    self.searchOK = true
                    self.lastUpdated = Date()
                    
                    //                    print(self.lastUpdated)
                    
                    self.getFlightCodeshares() { () in
                        //                        print("CODESHARE OK")
                    }
                    
                    
                    self.getAirportNames() { () in
                        //                        print("airport names OK")
                    }
                    self.getAirlineName() { () in
                        //                        print("airline name OK")
                    }
                    self.getAircraftName() { () in
                        //                        print("aircraft name OK")
                    }
                    
                    
                    
                    if (self.flightStatus?.aircraftreg != nil && self.flightStatus?.aircraftreg != "") {
                        
                        self.getAircraftLocation() { () in
                            
                        }
                        
                        if ((oldRegistration != self.flightStatus?.aircraftreg) || self.urlImageModel == nil) {
                            DispatchQueue.main.async {
                                self.urlImageModel = nil
                            }
                        
                        self.getImageURL() { () in

                            DispatchQueue.main.async {
                                let urlImageModel = UrlImageModel(urlString: self.imageData?.aircraftimage)
                                self.urlImageModel = urlImageModel
                                //added objectwillchange so urlImageModel changes when there is a change in the actual object (image is received)
                                self.urlImageModel!.objectWillChange
                                    .sink { _ in
                                        self.objectWillChange.send()
                                    }
                                    .store(in: &self.cancellables)
                            }
//                            }
                        }
                    }
                    }
                    
                    self.getStat7Day() { () in
                        //                        print("stat7day OK")
                    }
                    self.getStat30Day() { () in
                        //                        print("stat30day OK")
                    }
                    
                    self.getStatDays () { () in
                        //                        print("statday OK")
                    }
                }
                
                
            }
        }
        
        
    }
    
    
    
    
    
    
    func getImageURL(completion: @escaping () -> () ) {
        getLetApiToken { (tokenString) in
            //            print("tokenstring?")
            //after getting token string
            //            print("test")
            //            print(self.flightStatus?.aircraftreg)
            guard let url = URL(string: "https://letinfo.duckdns.org/aircraftimage/\(String((self.flightStatus?.aircraftreg)!))") else { return }
            //            print(url)
            let configuration = URLSessionConfiguration.default
            configuration.timeoutIntervalForRequest = 10.0;
            var request = URLRequest(url: url, cachePolicy: .returnCacheDataElseLoad)
            request.httpMethod = "GET"
            request.addValue((tokenString), forHTTPHeaderField: "x-access-tokens")
            let jsonDecoder = JSONDecoder()
            //            print("session1")
            URLSession.shared.dataTask(with: request) { (data, resp, error) in
                
                if error != nil {
                    if error?._code == -1001 {
                        //                        print("f status code -1001 timeout")
                        completion()
                    }
                } else {
                let imageDataResponse = try! jsonDecoder.decode(ImageData.self, from: data!)
                
                DispatchQueue.main.async {
//                    self.imageData = nil
                    self.imageData = imageDataResponse
                }
                //                    print(self.imageData)
                //                    print("IMAGE OK")
                completion()
                }
                
            }.resume()
        }
    }
    
    
    func getFlightStatus(completion: @escaping (FlightStatusDataModel) -> () ) {
        getLetApiToken { (tokenString) in
            //            print("tokenstring?")
            //after getting token string
            let dateFormatter = DateFormatter()
            dateFormatter.dateFormat = "yyyy-MM-dd"
            //dateFormatter.timeZone = TimeZone(abbreviation: "UTC")
            let dateString = dateFormatter.string(from: self.savedFlight?.date ?? Date())
            let flightString = self.savedFlight?.flightAirlineAndNumber() ?? ""
            let compareDate = Date().addingTimeInterval(-259200)
            var version = "live/flight"
            if (self.savedFlight!.date < compareDate) {
                version = "flight"
            }
            guard let url = URL(string: "https://letinfo.duckdns.org/\(version)/\(dateString)/\(flightString)") else { return }
            var request = URLRequest(url: url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 10.0)
            request.httpMethod = "GET"
            request.addValue((tokenString), forHTTPHeaderField: "x-access-tokens")
            
            let dateFormatter1 = DateFormatter()
            dateFormatter1.dateFormat = "yyyy-MM-dd'T'HH:mm"
            let dateFormatter2 = DateFormatter()
            dateFormatter2.dateFormat = "yyyy-MM-dd'T'HH:mmZ"
            let jsonDecoder = JSONDecoder()
            jsonDecoder.dateDecodingStrategyFormatters = [dateFormatter1, dateFormatter2]
            URLSession.shared.dataTask(with: request) { (data, response, error) in
                var flightStatusResponse = FlightStatusDataModel()
                if error != nil {
                        //                        print("f status code -1001 timeout")
                        completion(flightStatusResponse)
                    
                    
                } else {
                    if let httpRes = response as? HTTPURLResponse {
                        if httpRes.statusCode == 200 {
                            //                            print("f status ok ...")
                            
                            flightStatusResponse = try! jsonDecoder.decode(FlightStatusDataModel.self, from: data!)
//                            print("f status code 200 OK")
//                            let dataString =  String(data: data!, encoding: String.Encoding.utf8)
//                                                            print(dataString)
//                            print(flightStatusResponse)
                            completion(flightStatusResponse)
                        }
                        else {
                            //Other code 404,....
                            //                            print("f other status code")
                            completion(flightStatusResponse)
                        }
                    }
                    //                    print("f smo tu?")
                }
                
                
            }.resume()
        }
    }
    
    func getFlightCodeshares(completion: @escaping () -> () ) {
        getLetApiToken { (tokenString) in
            //            print("tokenstring?")
            //after getting token string
            let dateFormatter = DateFormatter()
            dateFormatter.dateFormat = "yyyy-MM-dd"
            dateFormatter.timeZone = TimeZone(abbreviation: "UTC")
            let dateString = dateFormatter.string(from: self.savedFlight?.date ?? Date())
            let flightString = self.savedFlight?.flightAirlineAndNumber() ?? ""
            
            let compareDate = Date().addingTimeInterval(-2592000)
            var version = "live/codeshares"
            if (self.savedFlight!.date < compareDate) {
                version = "codeshares"
            }
            
            guard let url = URL(string: "https://letinfo.duckdns.org/\(version)/\(dateString)/\(flightString)") else { return }
            var request = URLRequest(url: url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 10.0)
            request.httpMethod = "GET"
            request.addValue((tokenString), forHTTPHeaderField: "x-access-tokens")
            
            URLSession.shared.dataTask(with: request) { (data, response, error) in
                
                
                if error != nil {
                    if error?._code == -1001 {
                        //                            print("c status code -1001 timeout")
                        completion()
                    }
                } else {
                    if let httpRes = response as? HTTPURLResponse {
                        if httpRes.statusCode == 200 {
                            //                                print("c status ok ...")
                            
                            let codeshareDataResponse = try! JSONDecoder().decode(CodeshareDataModel.self, from: data!)
                            DispatchQueue.main.async {
//                                self.codeshareData = nil
                                self.codeshareData = codeshareDataResponse
                            }
                            //                                print("c status code 200 OK")
                            //                                print(self.codeshareData)
                            completion()
                        }
                        else {
                            //Other code 404,....
                            //                                print("c other status code")
                            completion()
                        }
                    }
                    //                        print("c smo tu?")
                }
                
                
            }.resume()
        }
    }
    
    func getAirportNames( completion: @escaping () -> () ) {
        let oldDepAirport = self.airportInfo?.depAirport?.airportName
        let oldArrAirport = self.airportInfo?.arrAirport?.airportName
        
        getAirportName(airportCode: (self.flightStatus?.depairport)!) { (depAirport) in
            self.getAirportName(airportCode: (self.flightStatus?.arrairport)!) { (arrAirport) in
               
                if (oldArrAirport == arrAirport.airportName && oldDepAirport == depAirport.airportName) {
                    return
                }
                else {
                DispatchQueue.main.async {
                    self.airportInfo = AirportInfoModel(depAirport: depAirport, arrAirport: arrAirport)
                }
                }
            
            }
        }
    }
    
    
    
    
    //V TEH FUNKCIJAH RAJŠI UPORABI ERROR NAMESTO COMPLETION
    func getAirportName(airportCode: String, completion: @escaping (AirportNameModel) -> () ) {
        getLetApiToken { (tokenString) in
            //            print("tokenstring?")
            //after getting token string
            
            guard let url = URL(string: "https://letinfo.duckdns.org/info/airportname/\(airportCode)") else { return }
            var request = URLRequest(url: url, cachePolicy: .returnCacheDataElseLoad, timeoutInterval: 10.0)
            request.httpMethod = "GET"
            request.addValue((tokenString), forHTTPHeaderField: "x-access-tokens")
            
            URLSession.shared.dataTask(with: request) { (data, response, error) in
                var airportName = AirportNameModel(airportName: "")
                if error != nil {
                    if error?._code == -1001 {
                        //                            print("c status code -1001 timeout")
                        completion(airportName)
                    }
                } else {
                    if let httpRes = response as? HTTPURLResponse {
                        if httpRes.statusCode == 200 {
                            //                                print("c status ok ...")
                            airportName = try! JSONDecoder().decode(AirportNameModel.self, from: data!)
                            //                                print("c status code 200 OK")
                            //                                print("AIRPORT NAME: ")
                            //                                let dataString =  String(data: data!, encoding: String.Encoding.utf8)
                            //                                print(dataString)
                            //                                print(airportName.airportName)
                            //                                print(airportName.longitude)
                            //                                print(airportName.latitude)
                            completion(airportName)
                        }
                        else {
                            //Other code 404,....
                            //                                print("c other status code")
                            completion(airportName)
                        }
                    }
                    //                        print("c smo tu?")
                }
                
                
            }.resume()
        }
    }
    
    func getAirlineName( completion: @escaping () -> () ) {
        getLetApiToken { (tokenString) in
            //            print("tokenstring?")
            //after getting token string
            //            print("\(String(describing: self.flightStatus?.airlineid!))")
            //            print("$#%liejnei)#")
            //            print(String((self.flightStatus?.airlineid!)!))
            guard let url = URL(string: "https://letinfo.duckdns.org/info/airlinename/\(String((self.flightStatus?.airlineid!)!))") else { return }
            //            print(url)
            var request = URLRequest(url: url, cachePolicy: .returnCacheDataElseLoad, timeoutInterval: 10.0)
            request.httpMethod = "GET"
            request.addValue((tokenString), forHTTPHeaderField: "x-access-tokens")
            
            URLSession.shared.dataTask(with: request) { (data, response, error) in
                
                if error != nil {
                    if error?._code == -1001 {
                        //                            print("c status code -1001 timeout")
                        completion()
                    }
                } else {
                    if let httpRes = response as? HTTPURLResponse {
                        if httpRes.statusCode == 200 {
                            //                                print("c status ok ...")
                            let airlineInfoResponse = try! JSONDecoder().decode(AirlineInfoModel.self, from: data!)
                            DispatchQueue.main.async {
//                                self.airlineInfo = nil
                                self.airlineInfo = airlineInfoResponse
                            }
                            //                                print("c status code 200 OK")
                            //                                print("AIRLINE NAME: ")
                            //                                print(self.airlineInfo?.airlineName)
                            completion()
                        }
                        else {
                            //Other code 404,....
                            //                                print("c other status code")
                            completion()
                        }
                    }
                    //                        print("c smo tu?")
                }
                
                
            }.resume()
        }
    }
    
    func getAircraftName( completion: @escaping () -> () ) {
        getLetApiToken { (tokenString) in
            //            print("tokenstring?")
            //after getting token string
            
            guard let url = URL(string: "https://letinfo.duckdns.org/info/aircraftname/\(String((self.flightStatus?.aircraftcode!)!))") else { return }
            //            print(url)
            var request = URLRequest(url: url, cachePolicy: .returnCacheDataElseLoad, timeoutInterval: 10.0)
            request.httpMethod = "GET"
            request.addValue((tokenString), forHTTPHeaderField: "x-access-tokens")
            
            URLSession.shared.dataTask(with: request) { (data, response, error) in
                
                if error != nil {
                    if error?._code == -1001 {
                        //                            print("c status code -1001 timeout")
                        completion()
                    }
                } else {
                    if let httpRes = response as? HTTPURLResponse {
                        if httpRes.statusCode == 200 {
                            //                                print("c status ok ...")
                            let aircraftInfoResponse = try! JSONDecoder().decode(AircraftInfoModel.self, from: data!)
                            
                            DispatchQueue.main.async {
//                                self.aircraftInfo = nil
                                self.aircraftInfo = aircraftInfoResponse
                            }
                            //                                print("c status code 200 OK")
                            //                                print("AIRCRAFT NAME: ")
                            //                                print(self.aircraftInfo?.aircraftName)
                            completion()
                        }
                        else {
                            //Other code 404,....
                            //                                print("c other status code")
                            completion()
                        }
                    }
                    //                        print("c smo tu?")
                }
                
                
            }.resume()
        }
    }
    
    func getStat7Day( completion: @escaping () -> () ) {
        getLetApiToken { (tokenString) in
            //            print("tokenstring? stat")
            //after getting token string
            let flightString = self.savedFlight?.flightAirlineAndNumber() ?? ""
            guard let url = URL(string: "https://letinfo.duckdns.org/stat7/\(flightString)") else { return }
            //            print(url)
            var request = URLRequest(url: url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 10.0)
            request.httpMethod = "GET"
            request.addValue((tokenString), forHTTPHeaderField: "x-access-tokens")
            
            URLSession.shared.dataTask(with: request) { (data, response, error) in
                
                if error != nil {
                    if error?._code == -1001 {
                        //                            print("stat status code -1001 timeout")
                        completion()
                    }
                } else {
                    if let httpRes = response as? HTTPURLResponse {
                        if httpRes.statusCode == 200 {
                            //                                print("stat status ok ...")
                            
                            let stat7DayResponse = try! JSONDecoder().decode(StatModel.self, from: data!)
                            
                            DispatchQueue.main.async {
//                                self.stat7Day = nil
                                self.stat7Day = stat7DayResponse
                            }
                            //                                let dataString =  String(data: data!, encoding: String.Encoding.utf8)
                            //                                print(dataString)
                            //                                print("stat status code 200 OK")
                            //                                print(self.stat7Day)
                            completion()
                        }
                        else {
                            //Other code 404,....
                            //                                print("stat other status code")
                            completion()
                        }
                    }
                    //                        print("stat smo tu?")
                }
                
                
            }.resume()
        }
    }
    
    func getStat30Day( completion: @escaping () -> () ) {
        getLetApiToken { (tokenString) in
            //            print("tokenstring? stat")
            //after getting token string
            let flightString = self.savedFlight?.flightAirlineAndNumber() ?? ""
            guard let url = URL(string: "https://letinfo.duckdns.org/stat30/\(flightString)") else { return }
            //            print(url)
            var request = URLRequest(url: url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 10.0)
            request.httpMethod = "GET"
            request.addValue((tokenString), forHTTPHeaderField: "x-access-tokens")
            
            URLSession.shared.dataTask(with: request) { (data, response, error) in
                
                if error != nil {
                    if error?._code == -1001 {
                        //                            print("stat status code -1001 timeout")
                        completion()
                    }
                } else {
                    if let httpRes = response as? HTTPURLResponse {
                        if httpRes.statusCode == 200 {
                            //                                print("stat status ok ...")
                            let stat30DayResponse = try! JSONDecoder().decode(StatModel.self, from: data!)
                            
                            DispatchQueue.main.async {
//                                self.stat30Day = nil
                                self.stat30Day = stat30DayResponse
                            }
                            //                                let dataString =  String(data: data!, encoding: String.Encoding.utf8)
                            //                                print(dataString)
                            //                                print("stat status code 200 OK")
                            //                                print(self.stat30Day)
                            completion()
                        }
                        else {
                            //Other code 404,....
                            //                                print("stat other status code")
                            completion()
                        }
                    }
                    //                        print("stat smo tu?")
                }
                
                
            }.resume()
        }
    }
    
    func getStatDays( completion: @escaping () -> () ) {
        getLetApiToken { (tokenString) in
            //            print("tokenstring? stat")
            //after getting token string
            let flightString = self.savedFlight?.flightAirlineAndNumber() ?? ""
            guard let url = URL(string: "https://letinfo.duckdns.org/statday/\(flightString)") else { return }
            //            print(url)
            var request = URLRequest(url: url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 10.0)
            request.httpMethod = "GET"
            request.addValue((tokenString), forHTTPHeaderField: "x-access-tokens")
            
            let dateFormatter1 = DateFormatter()
            dateFormatter1.dateFormat = "yyyy-MM-dd'T'HH:mm"
            let jsonDecoder = JSONDecoder()
            jsonDecoder.dateDecodingStrategyFormatters = [dateFormatter1]
            
            URLSession.shared.dataTask(with: request) { (data, response, error) in
                
                if error != nil {
                    if error?._code == -1001 {
                        //                            print("statday status code -1001 timeout")
                        completion()
                    }
                } else {
                    if let httpRes = response as? HTTPURLResponse {
                        if httpRes.statusCode == 200 {
                            //                                print("statday status ok ...")
                            let statDaysResponse = try! jsonDecoder.decode(StatDaysModel.self, from: data!)
                            DispatchQueue.main.async {
//                                self.statDays = nil
                                self.statDays = statDaysResponse
                            }
                            //let dataString =  String(data: data!, encoding: String.Encoding.utf8)
                            //                                print(dataString)
                            //                                print("statday status code 200 OK")
                            //print(self.statDays)
                            completion()
                        }
                        else {
                            //Other code 404,....
                            //                                print("statday other status code")
                            completion()
                        }
                    }
                    //                        print("statday smo tu?")
                }
                
                
            }.resume()
        }
    }
    
    func getAircraftLocation( completion: @escaping () -> () ) {
        getLetApiToken { (tokenString) in
            //            print("tokenstring? stat")
            //after getting token string
            let registrationString = self.flightStatus?.aircraftreg ?? ""
            guard let url = URL(string: "https://letinfo.duckdns.org/aircraftlocation/\(registrationString)") else { return }
            //            print(url)
            var request = URLRequest(url: url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 10.0)
            request.httpMethod = "GET"
            request.addValue((tokenString), forHTTPHeaderField: "x-access-tokens")
            
            let dateFormatter1 = DateFormatter()
            dateFormatter1.dateFormat = "yyyy-MM-dd'T'HH:mm"
            let jsonDecoder = JSONDecoder()
            jsonDecoder.dateDecodingStrategyFormatters = [dateFormatter1]
            
            URLSession.shared.dataTask(with: request) { (data, response, error) in
                
                if error != nil {
                    if error?._code == -1001 {
//                                                    print("statday status code -1001 timeout")
                        completion()
                    }
                } else {
                    if let httpRes = response as? HTTPURLResponse {
                        if httpRes.statusCode == 200 {
                            //                                print("statday status ok ...")
//                            let dataString =  String(data: data!, encoding: String.Encoding.utf8)
//                            print(dataString)
                            let locationResponse = try! jsonDecoder.decode(AircraftLocationModel.self, from: data!)
                            
                            if (locationResponse.latitude != nil) {
                            DispatchQueue.main.async {
//                                self.statDays = nil
                                self.aircraftLocation = locationResponse
                            }
                            }
                            
                            //                                print("statday status code 200 OK")
                            //print(self.statDays)
                            completion()
                        }
                        else {
//                            Other code 404,....
//                                                            print("statday other status code")
                            completion()
                        }
                    }
                    //                        print("statday smo tu?")
                }
                
                
            }.resume()
        }
    }
    
    func registerForNotifications( completion: @escaping () -> () ) {
        getLetApiToken { (tokenString) in
            guard let url = URL(string: "https://letinfo.duckdns.org/notifications/register") else { return }
            //            print(url)
            var request = URLRequest(url: url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 5.0)
            request.httpMethod = "POST"
            request.addValue((tokenString), forHTTPHeaderField: "x-access-tokens")
            
            let dateFormatter1 = DateFormatter()
            dateFormatter1.dateFormat = "yyyy-MM-dd'"
            
            if let token = DAKeychain.shared["ApplePushToken"] {
                
                let parameters: [String: Any] = [
                    "token": token,
                    "date": dateFormatter1.string(from: (self.flightStatus?.depscheduled)!),
                    "flightnumber":(self.flightStatus?.flightnumber ?? ""),
                    "airline": (self.flightStatus?.airlineid ?? "")
                ]
                
                request.httpBody = parameters.percentEncoded()
                
                //            print(parameters)
                
                let jsonDecoder = JSONDecoder()
                
                URLSession.shared.dataTask(with: request) { (data, response, error) in
                    
                    if error != nil {
                        if error?._code == -1001 {
                            //                            print("notificationregister status code -1001 timeout")
                            DispatchQueue.main.async { self.notifications = false }
                            completion()
                        }
                    } else {
                        if let httpRes = response as? HTTPURLResponse {
                            if httpRes.statusCode == 200 {
                                //                                print("notificationregister status ok ...")
                                let apiResponse = try! jsonDecoder.decode(NotificationApiResponse.self, from: data!)
//                                let dataString =  String(data: data!, encoding: String.Encoding.utf8)
                                //                                print(dataString)
                                //                                print("notificationregister status code 200 OK")
                                
                                if apiResponse.info == "OK" {
                                    //                                    print("notificationregister OK")
                                }
                                else {
                                    //                                    print("notificationregister NOT OK: \(apiResponse.info)")
                                    DispatchQueue.main.async { self.notifications = false }
                                }
                                
                                completion()
                            }
                            else {
                                //Other code 404,....
                                //                                print("notificationregister other status code")
                                DispatchQueue.main.async { self.notifications = false }
                                completion()
                            }
                        }
                        //                        print("notificationregister smo tu?")
                    }
                    
                    
                }.resume()
            }
            else {
                DispatchQueue.main.async { self.notifications = false }
                //                print("getting token from keychain error")
                completion()
            }
        }
    }
    
    func unregisterForNotifications( completion: @escaping (String) -> () ) {
        getLetApiToken { (tokenString) in
            guard let url = URL(string: "https://letinfo.duckdns.org/notifications/unregister") else { return }
            //            print(url)
            var request = URLRequest(url: url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 5.0)
            request.httpMethod = "POST"
            request.addValue((tokenString), forHTTPHeaderField: "x-access-tokens")
            
            let dateFormatter1 = DateFormatter()
            dateFormatter1.dateFormat = "yyyy-MM-dd'"
            
            if let token = DAKeychain.shared["ApplePushToken"] {
                //                print(token)
                
                let parameters: [String: Any] = [
                    "token": token,
                    "date": dateFormatter1.string(from: (self.flightStatus?.depscheduled)!),
                    "flightnumber":(self.flightStatus?.flightnumber ?? ""),
                    "airline": (self.flightStatus?.airlineid ?? "")
                ]
                
                request.httpBody = parameters.percentEncoded()
                
                //            print(parameters)
                
                let jsonDecoder = JSONDecoder()
                
                URLSession.shared.dataTask(with: request) { (data, response, error) in
                    
                    if error != nil {
                        if error?._code == -1001 {
                            //                            print("notificationunregister status code -1001 timeout")
                            DispatchQueue.main.async { self.notifications = true }
                            completion("ERROR")
                        }
                    } else {
                        if let httpRes = response as? HTTPURLResponse {
                            if httpRes.statusCode == 200 {
                                //
                                let apiResponse = try! jsonDecoder.decode(NotificationApiResponse.self, from: data!)
//                                let dataString =  String(data: data!, encoding: String.Encoding.utf8)
                                //                                print(dataString)
                                //                                print("notificationunregister status code 200 OK")
                                
                                if apiResponse.info == "OK" {
                                    //                                    print("notificationunregister OK")
                                }
                                else {
                                    //                                    print("notificationunregister NOT OK: \(apiResponse.info)")
                                    
                                    DispatchQueue.main.async { self.notifications = true }
                                }
                                
                                completion("OK")
                            }
                            else {
                                //Other code 404,....
                                //                                print("notificationunregister other status code")
                                DispatchQueue.main.async { self.notifications = true }
                                completion("ERROR")
                            }
                        }
                        //                        print("notificationunregister smo tu?")
                    }
                    
                    
                }.resume()
                
                
            }
            else {
                DispatchQueue.main.async { self.notifications = true }
                //                print("getting token from keychain error")
                completion("ERROR")
            }
        }
    }
    
    
    
    
    
    
    
}


struct SavedFlightDataModel: Codable, Identifiable {
    let id = UUID()
    var airlineid: String
    var flightnumber: String
    var date: Date
    
    init(airlineid: String, flightnumber: String, date: Date) {
        self.airlineid = airlineid
        self.flightnumber = flightnumber
        self.date = date
    }
    
    func flightAirlineAndNumber() -> String {
        let flightAirlineAndNumberString = (String(self.airlineid) + String(self.flightnumber))
        return flightAirlineAndNumberString
    }
}


struct FlightStatusDataModel: Codable, Identifiable, Equatable {
    
    let id = UUID()
    var depairport: String?
    var depscheduled: Date?
    var depscheduledUTC: Date?
    var depestimated: Date?
    var depestimatedUTC: Date?
    var depactual: Date?
    var depactualUTC: Date?
    var depterminal: String?
    var depgate: String?
    var deptimestatus: String?
    var arrairport: String?
    var arrscheduled: Date?
    var arrscheduledUTC: Date?
    var arrestimated: Date?
    var arrestimatedUTC: Date?
    var arractual: Date?
    var arractualUTC: Date?
    var arrterminal: String?
    var arrgate: String?
    var arrtimestatus: String?
    var aircraftcode: String?
    var aircraftreg: String?
    var airlineid: String?
    var flightnumber: String?
    var flightstatus: String?
    
    
    var depscheduledDateString: String?
    var depscheduledString: String?
    var depestimatedString: String?
    var depactualString: String?
    var arrscheduledString: String?
    var arrestimatedString: String?
    var arractualString: String?
    var arrtimestatusString: String?
    var deptimestatusString: String?
    var flightstatusString: String?
    
    
    init() {
        //        print("bla")
    }
    
    init(from decoder: Decoder) throws {
        let values = try decoder.container(keyedBy: CodingKeys.self)
        depairport = try values.decodeIfPresent(String.self, forKey: .depairport)
        depscheduled = try values.decodeIfPresent(Date.self, forKey: .depscheduled)
        depscheduledUTC = try values.decodeIfPresent(Date.self, forKey: .depscheduledUTC)
        
        //we check if string is empty instead of valid date
        if let string = try values.decodeIfPresent(String.self, forKey: .depestimated), !string.isEmpty {
            depestimated = try values.decode(Date.self, forKey: .depestimated)
        } else {
            depestimated = nil
        }
        
        if let string = try values.decodeIfPresent(String.self, forKey: .depestimatedUTC), !string.isEmpty {
            depestimatedUTC = try values.decode(Date.self, forKey: .depestimatedUTC)
        } else {
            depestimatedUTC = nil
        }
        
        if let string = try values.decodeIfPresent(String.self, forKey: .depactual), !string.isEmpty {
            depactual = try values.decode(Date.self, forKey: .depactual)
        } else {
            depactual = nil
        }
        
        if let string = try values.decodeIfPresent(String.self, forKey: .arrestimated), !string.isEmpty {
            arrestimated = try values.decode(Date.self, forKey: .arrestimated)
        } else {
            arrestimated = nil
        }
        
        if let string = try values.decodeIfPresent(String.self, forKey: .arrestimatedUTC), !string.isEmpty {
            arrestimatedUTC = try values.decode(Date.self, forKey: .arrestimatedUTC)
        } else {
            arrestimatedUTC = nil
        }
        
        if let string = try values.decodeIfPresent(String.self, forKey: .depactualUTC), !string.isEmpty {
            depactualUTC = try values.decode(Date.self, forKey: .depactualUTC)
        } else {
            depactualUTC = nil
        }
        //we check if string is empty instead of valid date
        if let string = try values.decodeIfPresent(String.self, forKey: .arractual), !string.isEmpty {
            arractual = try values.decode(Date.self, forKey: .arractual)
        } else {
            arractual = nil
        }
        //we check if string is empty instead of valid date
        if let string = try values.decodeIfPresent(String.self, forKey: .arractualUTC), !string.isEmpty {
            arractualUTC = try values.decode(Date.self, forKey: .arractualUTC)
        } else {
            arractualUTC = nil
        }
        
        //depactual = try values.decodeIfPresent(Date.self, forKey: .depactual)
        //depactualUTC = try values.decodeIfPresent(Date.self, forKey: .depactualUTC)
        depterminal = try values.decodeIfPresent(String.self, forKey: .depterminal)
        depgate = try values.decodeIfPresent(String.self, forKey: .depgate)
        deptimestatus = try values.decodeIfPresent(String.self, forKey: .deptimestatus)
        arrairport = try values.decodeIfPresent(String.self, forKey: .arrairport)
        arrscheduled = try values.decodeIfPresent(Date.self, forKey: .arrscheduled)
        arrscheduledUTC = try values.decodeIfPresent(Date.self, forKey: .arrscheduledUTC)
        //arractual = try values.decodeIfPresent(Date.self, forKey: .arractual)
        //arractualUTC = try values.decodeIfPresent(Date.self, forKey: .arractualUTC)
        arrterminal = try values.decodeIfPresent(String.self, forKey: .arrterminal)
        arrgate = try values.decodeIfPresent(String.self, forKey: .arrgate)
        arrtimestatus = try values.decodeIfPresent(String.self, forKey: .arrtimestatus)
        aircraftcode = try values.decodeIfPresent(String.self, forKey: .aircraftcode)
        aircraftreg = try values.decodeIfPresent(String.self, forKey: .aircraftreg)
        airlineid = try values.decodeIfPresent(String.self, forKey: .airlineid)
        flightnumber = try values.decodeIfPresent(String.self, forKey: .flightnumber)
        flightstatus = try values.decodeIfPresent(String.self, forKey: .flightstatus)
        
        if (flightstatus != nil) {
            flightstatusString = flightstatusDecodeString(status: flightstatus!)
        }
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd"
        if (depscheduled != nil) {
            depscheduledDateString = dateFormatter.string(from: depscheduled!)
        }
        dateFormatter.dateFormat = "HH:mm"
        if (depscheduled != nil) {
            depscheduledString = dateFormatter.string(from: depscheduled!)
        }
        if (depestimated != nil) {
            depestimatedString = dateFormatter.string(from: depestimated!) + dateDifferenceString(scheduled: depscheduledUTC!, actual: depestimatedUTC!)
        }
        if (depactual != nil) {
            depactualString = dateFormatter.string(from: depactual!) + dateDifferenceString(scheduled: depscheduledUTC!, actual: depactualUTC!)
        }
        if (deptimestatus != nil) {
            deptimestatusString = flightstatusDecodeString(status: deptimestatus!)
        }
        if (arrscheduled != nil) {
            arrscheduledString = dateFormatter.string(from: arrscheduled!)
        }
        if (arrestimated != nil) {
            arrestimatedString = dateFormatter.string(from: arrestimated!) + dateDifferenceString(scheduled: arrscheduledUTC!, actual: arrestimatedUTC!)
        }
        if (arractual != nil) {
            arractualString = dateFormatter.string(from: arractual!) + dateDifferenceString(scheduled: arrscheduledUTC!, actual: arractualUTC!)
        }
        if (arrtimestatus != nil) {
            arrtimestatusString = flightstatusDecodeString(status: arrtimestatus!)
        }
    }
    
    
    func dateDifferenceString(scheduled: Date, actual: Date) -> String {
        let calendar = Calendar.current
        let difference = calendar.dateComponents([.day], from: calendar.startOfDay(for: scheduled), to: calendar.startOfDay(for: actual))
        let differenceString = String(difference.day!)
        if difference.day == 0 {
            return ""
        }
        else {
            return " \(differenceString)D"
        }
    }
    func flightstatusDecodeString(status: String) -> String {
        switch status {
        case "CD":
            return "Flight Cancelled"
        case "DP":
            return "Flight Departed"
        case "LD":
            return "Flight Landed"
        case "RT":
            return "Flight Rerouted"
        case "FE":
            return "Flight Early"
        case "NI":
            return "Next Information"
        case "OT":
            return "Flight On Time"
        case "DL":
            return "Flight Delayed"
        case "NO":
            return ""
        default:
            return ""
        }
    }
}


struct ImageData: Codable, Identifiable {
    let id = UUID()
    var aircraftimage: String?
    var photographer: String?
    
    init(from decoder: Decoder) throws {
        let values = try decoder.container(keyedBy: CodingKeys.self)
        aircraftimage = try values.decodeIfPresent(String.self, forKey: .aircraftimage)
        photographer = try values.decodeIfPresent(String.self, forKey: .photographer)
    }
}



struct CodeshareDataModel: Codable, Identifiable {
    let id = UUID()
    var operating: CodeshareFlightModel?
    var codeshares: [CodeshareFlightModel]?
    
    
    init(){
        operating = CodeshareFlightModel.init()
        codeshares = []
    }
    
    func getString() -> String {
        var codesharesString = ""
        if (codeshares != nil) {
            for codeshare in self.codeshares! {
                codesharesString = codesharesString + "\(String(codeshare.airlineid!))\(String(codeshare.flightnumber!)) "
                //                print(codesharesString)
            }
        }
        return codesharesString
    }
}

struct CodeshareFlightModel: Codable, Identifiable {
    let id = UUID()
    var airlineid: String?
    var flightnumber: String?
    
    init() {
        airlineid = ""
        flightnumber = ""
    }
}


struct AirportNameModel: Codable, Identifiable {
    let id = UUID()
    var airportName: String?
    var latitude: Double?
    var longitude: Double?
    
    init(airportName: String) {
        self.airportName = airportName
    }
    //    init(airportName: String, latitude: Double, longitude: Double) {
    //        self.airportName = airportName
    //        self.latitude = latitude
    //        self.longitude = longitude
    //    }
}


struct AirportInfoModel: Codable, Identifiable {
    let id = UUID()
    var depAirport: AirportNameModel?
    var arrAirport: AirportNameModel?
    
    init(depAirport: AirportNameModel, arrAirport: AirportNameModel) {
        self.depAirport = depAirport
        self.arrAirport = arrAirport
    }
}
struct AirlineInfoModel: Codable, Identifiable {
    let id = UUID()
    var airlineName: String?
    
    init(airlineName: String) {
        self.airlineName = airlineName
    }
}
struct AircraftInfoModel: Codable, Identifiable {
    let id = UUID()
    var aircraftName: String?
    
    init(aircraftName: String) {
        self.aircraftName = aircraftName
    }
}


//potrebno? preveri
struct SavedFlightModel: Codable, Identifiable {
    let id = UUID()
    var airlineid: String
    var flightnumber: String
    var date: Date
    
    init(airlineid: String, flightnumber: String, date: Date) {
        self.airlineid = airlineid
        self.flightnumber = flightnumber
        self.date = date
    }
    
    //        init() {
    //            self.airlineid = ""
    //            self.flightnumber = ""
    //            self.date = Date()
    //        }
    
    func flightAirlineAndNumber() -> String {
        let flightAirlineAndNumberString = (String(self.airlineid) + String(self.flightnumber))
        return flightAirlineAndNumberString
    }
}


struct StatModel: Codable, Identifiable {
    let id = UUID()
    var allflights: Int?
    var cancelled: Int?
    var dep_OT: Int?
    var dep_FE: Int?
    var dep_DL: Int?
    var averageTimeDep: Int?
    var averageTimeDep_OT: Int?
    var averageTimeDep_FE: Int?
    var averageTimeDep_DL: Int?
    var arr_OT: Int?
    var arr_FE: Int?
    var arr_DL: Int?
    var averageTimeArr: Int?
    var averageTimeArr_OT: Int?
    var averageTimeArr_FE: Int?
    var averageTimeArr_DL: Int?
    
    
    init(allflights: Int?, cancelled: Int?, dep_OT: Int?, dep_FE: Int?, dep_DL: Int?, averageTimeDep: Int?, averageTimeDep_OT: Int?, averageTimeDep_FE: Int?, averageTimeDep_DL: Int?, arr_OT: Int?, arr_FE: Int?, arr_DL: Int?, averageTimeArr: Int?, averageTimeArr_OT: Int?, averageTimeArr_FE: Int?, averageTimeArr_DL: Int?) {
        self.allflights = allflights
        self.cancelled = cancelled
        self.dep_OT = dep_OT
        self.dep_FE = dep_FE
        self.dep_DL = dep_DL
        self.averageTimeDep = averageTimeDep
        self.averageTimeDep_OT = averageTimeDep_OT
        self.averageTimeDep_FE = averageTimeDep_FE
        self.averageTimeDep_DL = averageTimeDep_DL
        self.arr_OT = arr_OT
        self.arr_FE = arr_FE
        self.arr_DL = arr_DL
        self.averageTimeArr = averageTimeArr
        self.averageTimeArr_OT = averageTimeArr_OT
        self.averageTimeArr_FE = averageTimeArr_FE
        self.averageTimeArr_DL = averageTimeArr_DL
    }
    
    //
    //    enum CodingKeys: String, CodingKey {
    //            case allflights = "allflights"
    //            case cancelled = "cancelled"
    //            case depOT = "dep_OT"
    //            case depFE = "dep_FE"
    //            case depDL = "dep_DL"
    //            case averageTimeDep
    //            case averageTimeDepOT = "averageTimeDep_OT"
    //            case averageTimeDepFE = "averageTimeDep_FE"
    //            case averageTimeDepDL = "averageTimeDep_DL"
    //            case arrOT = "arr_OT"
    //            case arrFE = "arr_FE"
    //            case arrDL = "arr_DL"
    //            case averageTimeArr
    //            case averageTimeArrOT = "averageTimeArr_OT"
    //            case averageTimeArrFE = "averageTimeArr_FE"
    //            case averageTimeArrDL = "averageTimeArr_DL"
    //        }
}

struct StatDayModel: Codable, Identifiable {
    let id = UUID()
    var depscheduled: Date?
    var deptimestatus: String?
    var arrtimestatus: String?
    var flightstatus: String?
    
    
    init() {
        self.depscheduled = nil
        self.deptimestatus = ""
        self.arrtimestatus = ""
        self.flightstatus = ""
    }
}
struct StatDaysModel: Codable, Identifiable {
    let id = UUID()
    var flightDayArray: [StatDayModel]?
    var statDayDates: StatDayDatesModel?
    
    init() {
        self.flightDayArray = []
    }
    
    init(from decoder: Decoder) throws {
        let values = try decoder.container(keyedBy: CodingKeys.self)
        flightDayArray = try values.decodeIfPresent([StatDayModel].self, forKey: .flightDayArray)
        statDayDates = self.getDates()
    }
    
    func getDates() -> StatDayDatesModel {
        var statDayDates = StatDayDatesModel()
        if flightDayArray != nil {
            for date in flightDayArray! {
                if date.flightstatus == "CD" {
                    statDayDates.cancelledDates.append(date.depscheduled!)
                }
                else if (date.arrtimestatus == "OT" ||  date.arrtimestatus == "FE") {
                    statDayDates.ontimeDates.append(date.depscheduled!)
                }
                else if (date.arrtimestatus == "DL") {
                    statDayDates.delayedDates.append(date.depscheduled!)
                }
            }
        }
        return statDayDates
    }
}

struct StatDayDatesModel: Codable, Identifiable {
    let id = UUID()
    var cancelledDates: [Date]
    var delayedDates: [Date]
    var ontimeDates: [Date]
    
    init() {
        self.cancelledDates = []
        self.delayedDates = []
        self.ontimeDates = []
    }
}



struct NotificationApiResponse : Codable {
    var info : String?
    
    enum CodingKeys: String, CodingKey {
        case info = "info"
    }
    
    init(from decoder: Decoder) throws {
        let values = try decoder.container(keyedBy: CodingKeys.self)
        info = try values.decodeIfPresent(String.self, forKey: .info)
    }
    
    init(){
        info = nil
    }
}

struct AircraftLocationModel: Codable, Identifiable {
    let id = UUID()
    var longitude: Double?
    var latitude: Double?
    var baroaltitude: Double?
    var velocity: Double?
    var truetrack: Double?
    var updated = Date()
    
    enum CodingKeys: String, CodingKey {
        case longitude = "longitude"
        case latitude = "latitude"
        case baroaltitude = "baro_altitude"
        case velocity = "velocity"
        case truetrack = "true_track"
    }
    
    init(from decoder: Decoder) throws {
        let values = try decoder.container(keyedBy: CodingKeys.self)
        longitude = try values.decodeIfPresent(Double.self, forKey: .longitude)
        latitude = try values.decodeIfPresent(Double.self, forKey: .latitude)
        baroaltitude = try values.decodeIfPresent(Double.self, forKey: .baroaltitude)
        velocity = try values.decodeIfPresent(Double.self, forKey: .velocity)
        truetrack = try values.decodeIfPresent(Double.self, forKey: .truetrack)
        updated = Date()
    }
    
}


//razširitev za dekodiranje json z več formati datumov hkrati
extension JSONDecoder {
    var dateDecodingStrategyFormatters: [DateFormatter]? {
        @available(*, unavailable, message: "This variable is meant to be set only")
        get { return nil }
        set {
            guard let formatters = newValue else { return }
            self.dateDecodingStrategy = .custom { decoder in
                
                let container = try decoder.singleValueContainer()
                let dateString = try container.decode(String.self)
                
                for formatter in formatters {
                    if let date = formatter.date(from: dateString) {
                        return date
                    }
                }
                
                throw DecodingError.dataCorruptedError(in: container, debugDescription: "Cannot decode date string \(dateString)")
            }
        }
    }
}

//encoding for http body
extension Dictionary {
    func percentEncoded() -> Data? {
        return map { key, value in
            let escapedKey = "\(key)".addingPercentEncoding(withAllowedCharacters: .urlQueryValueAllowed) ?? ""
            let escapedValue = "\(value)".addingPercentEncoding(withAllowedCharacters: .urlQueryValueAllowed) ?? ""
            return escapedKey + "=" + escapedValue
        }
        .joined(separator: "&")
        .data(using: .utf8)
    }
}
extension CharacterSet {
    static let urlQueryValueAllowed: CharacterSet = {
        let generalDelimitersToEncode = ":#[]@" // does not include "?" or "/" due to RFC 3986 - Section 3.4
        let subDelimitersToEncode = "!$&'()*+,;="
        
        var allowed = CharacterSet.urlQueryAllowed
        allowed.remove(charactersIn: "\(generalDelimitersToEncode)\(subDelimitersToEncode)")
        return allowed
    }()
}





