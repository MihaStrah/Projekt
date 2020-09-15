//
//  letApiToken.swift
//  FlightTracker
//
//  Created by Miha Strah on 10/07/2020.
//  Copyright © 2020 Miha Strah. All rights reserved.
//

import Foundation

struct letApiTokenResponse : Codable {
    var token : String?
    var expires : Date?
    
    enum CodingKeys: String, CodingKey {
        case token = "token"
        case expires = "expires"
    }
    
    init(from decoder: Decoder) throws {
        let values = try decoder.container(keyedBy: CodingKeys.self)
        token = try values.decodeIfPresent(String.self, forKey: .token)
        expires = try values.decodeIfPresent(Date.self, forKey: .expires)
    }
    
    init(){
        token = nil
        expires = nil
    }
}

func getLetApiToken(completion: @escaping (String) -> () ) {
    //Dev
    //print("force expire")
    //DAKeychain.shared["LetApiTokenExpires"] = "2000-01-01T00:00:00.000000"
    
    if let keychainTokenExpires = DAKeychain.shared["LetApiTokenExpires"] {
        if let keychainToken = DAKeychain.shared["LetApiToken"] {
            var existingToken = letApiTokenResponse()
            existingToken.token = keychainToken
            let dateFormatter = DateFormatter()
            dateFormatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"
            dateFormatter.timeZone = TimeZone(abbreviation: "UTC")
            existingToken.expires = dateFormatter.date(from: keychainTokenExpires)
//            print("EXISTING TOKEN")
//            print(existingToken.token)
//            print(existingToken.expires)
//            print(Date())
            if existingToken.expires! > Date().addingTimeInterval(1*60)   {
                completion(existingToken.token!)
            }
            else {
                DAKeychain.shared["LetApiToken"] = nil
                DAKeychain.shared["LetApiTokenExpires"] = nil
            }
        }
//        print("?2")
    }
    if DAKeychain.shared["LetApiTokenExpires"] == nil {
//        print("GETTING NEW TOKEN")
        getNewLetApiToken { (received) in
            if received.token == nil {
                ///TO DO !!!
//                print("RECEIVED TOKEN NIL what to do, try again?")
            }
            else {
//                print("HAVE NEW TOKEN")
//                print(received.token)
//                print(received.expires)
                let newToken = received
                DAKeychain.shared["LetApiToken"] = newToken.token
                let dateFormatter = DateFormatter()
                dateFormatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"
                dateFormatter.timeZone = TimeZone(abbreviation: "UTC")
                DAKeychain.shared["LetApiTokenExpires"] = dateFormatter.string(from: newToken.expires!)
//                print("keychain")
//                print(DAKeychain.shared["LetApiToken"])
                completion(newToken.token!)
            }
        }
    }
}


func getNewLetApiToken(completion: @escaping (letApiTokenResponse) -> ()){
    let configuration = URLSessionConfiguration.default
    configuration.timeoutIntervalForRequest = 4.0;
    
    let username = ApiConf.user
    let password = ApiConf.pass
    let loginString = "\(username):\(password)"
    
    
    
    let loginData = loginString.data(using: String.Encoding.utf8)
    let base64LoginString = loginData!.base64EncodedString()
    
    var request = URLRequest(url: URL(string: "https://letinfo.duckdns.org/login")!)
    request.httpMethod = "POST"
    request.setValue("Basic \(base64LoginString)", forHTTPHeaderField: "Authorization")
    let session = URLSession(configuration: configuration)
    var responseModel = letApiTokenResponse()
    let task = session.dataTask(with: request, completionHandler: { (data, response, error) in
        do {
            if error != nil {
                if error?._code == -1001 {
//                    print("status code -1001 timeout")
                    completion(responseModel)
                }
            } else {
                if let httpRes = response as? HTTPURLResponse {
                    if httpRes.statusCode == 200 {
                        let jsonDecoder = JSONDecoder()
                        //date decoding
                        let dateFormatter = DateFormatter()
                        dateFormatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"
                        dateFormatter.timeZone = TimeZone(abbreviation: "UTC")
                        jsonDecoder.dateDecodingStrategy = .formatted(dateFormatter)
                        responseModel = try jsonDecoder.decode(letApiTokenResponse.self, from: data!)
//                        print("status code 200 OK")
                        completion(responseModel)
                    }
                    else {
                        //Other code 404,....
//                        print("other status code")
                        completion(responseModel)
                    }
                }
            }
            
        } catch {
//            print("error:")
//            print(error)
            completion(responseModel)
        }
        
    })
    task.resume()
}


