//
//  FlightCard.swift
//  FlightTracker
//
//  Created by Miha Strah on 14/08/2020.
//  Copyright © 2020 Miha Strah. All rights reserved.
//

import SwiftUI

//struct FlightCard: View {
//    @ObservedObject var flightStatusObject:FlightStatusObject
//    @State public var date = Date()
//
//    var body: some View {
//        //                LinearGradient(gradient: Gradient(colors: [Color(#colorLiteral(red: 1, green: 1, blue: 1, alpha: 1)),Color(#colorLiteral(red: 0.4980392157, green: 0.7215686275, blue: 0, alpha: 1))]), startPoint: .top, endPoint: .bottom)
//        //                Image("airplane_stock")
//        //                    .resizable()
//        //                    .aspectRatio(contentMode: .fit)
//        //                    .brightness(0.5)
//
//        ZStack(alignment: .topLeading) {
////            RoundedRectangle(cornerRadius: 10, style: .continuous)
//            LinearGradient(gradient: Gradient(colors: [Color(#colorLiteral(red: 1, green: 1, blue: 1, alpha: 1)),Color(#colorLiteral(red: 0.4980392157, green: 0.7215686275, blue: 0, alpha: 1))]), startPoint: .top, endPoint: .bottom)
//                .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
//
//
//            VStack(alignment: .leading, spacing: 4) {
//                Text("bla")
//                HStack() {
//                    Text("\(flightStatusObject.savedFlight?.airlineid ?? "XX")\(flightStatusObject.savedFlight?.flightnumber ?? "0000")")
//                        .font(.title)
//                    if (flightStatusObject.airlineInfo?.airlineName != nil) {
//                        Text("operated by \(flightStatusObject.airlineInfo?.airlineName ?? "XX")")
//                            .font(.subheadline)
//                    }
//                        if ((flightStatusObject.codeshareData?.operating?.airlineid != nil) && (flightStatusObject.savedFlight?.airlineid != flightStatusObject.codeshareData?.operating?.airlineid)) {
//                            Text("(\(flightStatusObject.codeshareData?.operating?.airlineid ?? "")\(flightStatusObject.codeshareData?.operating?.flightnumber ?? ""))")
//                                .font(.subheadline)
//                        }
//
//
//                    if ((Date().addingTimeInterval(-86399) ... Date().addingTimeInterval(259199)).contains((self.flightStatusObject.flightStatus?.depscheduled!)!)) {
//                        Spacer()
//                        Button(action: {
//                            print("bell me")
//                            self.flightStatusObject.notificationToggle()
//                        })
//                        {
//                            Image(systemName: (self.flightStatusObject.notifications ? "bell.fill" : "bell")).font(.title)
//                        }
//                    }
//
//                }
//                .foregroundColor(/*@START_MENU_TOKEN@*/.blue/*@END_MENU_TOKEN@*/)
//
//
//
//                HStack() {
//                    Text(flightStatusObject.flightStatus?.depscheduledDateString ?? "no date")
//                        .font(.subheadline)
//                    Spacer()
//                }
//
//
//                HStack(){
//                    Text(flightStatusObject.flightStatus?.depscheduledString ?? "00:00")
//                        .font(.title)
//                    if flightStatusObject.flightStatus?.depactualString != nil {
//                        VStack() {
//                            Text("Actual")
//                                .font(.caption)
//                            Text("(\(flightStatusObject.flightStatus?.depactualString ?? "00:00"))")
//                                .font(.body)
//                        }.foregroundColor((self.flightStatusObject.flightStatus?.deptimestatus == "DL") ? Color("DLColor1") : Color("TextColor"))
//                    }
//                    Spacer()
//
//                    if flightStatusObject.flightStatus?.arractualString != nil {
//                        VStack() {
//                            Text("Actual")
//                                .font(.caption)
//                            Text("(\(flightStatusObject.flightStatus?.arractualString ?? "00:00"))")
//                                .font(.body)
//                        }.foregroundColor((self.flightStatusObject.flightStatus?.arrtimestatus == "DL") ? Color("DLColor1") : Color("TextColor"))
//
//                    }
//
//                    Text(flightStatusObject.flightStatus?.arrscheduledString ?? "00:00")
//                        .font(.title)
//                }
//                .padding(.vertical, 5.0)
//                HStack(){
//                    if flightStatusObject.flightStatus?.deptimestatusString != "" {
//                        Text(flightStatusObject.flightStatus?.deptimestatusString?.replacingOccurrences(of: "Flight ", with: "") ?? "no time status")
//                            .font(.callout)
//                            .foregroundColor((self.flightStatusObject.flightStatus?.deptimestatus == "DL") ? Color("DLColor1") : Color("TextColor"))
//                    }
//                    Spacer()
//                    Text(flightStatusObject.flightStatus?.flightstatusString ?? "no flight status")
//                        .font(.headline)
//                        .foregroundColor(((self.flightStatusObject.flightStatus?.arrtimestatus == "OT" || self.flightStatusObject.flightStatus?.arrtimestatus == "FE") ? Color("OTColor2") : ((self.flightStatusObject.flightStatus?.arrtimestatus == "DL") ? Color("DLColor1") : ((self.flightStatusObject.flightStatus?.arrtimestatus == "CD" || self.flightStatusObject.flightStatus?.arrtimestatus == "RT") ? Color("CDColor1") : Color("NOColor1")))))
//                    Spacer()
//                    if flightStatusObject.flightStatus?.arrtimestatusString != "" {
//                        Text(flightStatusObject.flightStatus?.arrtimestatusString?.replacingOccurrences(of: "Flight ", with: "") ?? "no time status")
//                            .font(.callout)
//                            .foregroundColor((self.flightStatusObject.flightStatus?.arrtimestatus == "DL") ? Color("DLColor1") : Color("TextColor"))
//                    }
//                }
//
//                HStack(){
//                    VStack(alignment: .leading) {
//                        Text(flightStatusObject.flightStatus?.depairport ?? "/")
//                            .font(.title)
//                            .foregroundColor(/*@START_MENU_TOKEN@*/.blue/*@END_MENU_TOKEN@*/)
//                        Text(flightStatusObject.airportInfo?.depAirport?.airportName ?? "/")
//                            .font(.body)
//                    }
//                    Spacer()
//                    Image(systemName: "arrow.right").font(.largeTitle)
//                    Spacer()
//                    VStack(alignment: .trailing) {
//                        Text(flightStatusObject.flightStatus?.arrairport ?? "/")
//                            .font(.title)
//                            .foregroundColor(/*@START_MENU_TOKEN@*/.blue/*@END_MENU_TOKEN@*/)
//                        Text(flightStatusObject.airportInfo?.arrAirport?.airportName ?? "/")
//                            .font(.body)
//                    }
//                }
//                }
//        }
//
//        .foregroundColor(.black)
//
//        }
//
//    }


func flightCardGradient(flightStatusObject: FlightStatusObject) -> Gradient {
    
    if (flightStatusObject.flightStatus?.flightstatusString != "" && flightStatusObject.flightStatus?.flightstatus != nil) {
        switch flightStatusObject.flightStatus?.flightstatus {
        case "DP":
            switch flightStatusObject.flightStatus?.deptimestatus {
            case "FE":
                let gradient = Gradient(colors: [Color("OTColorCard1"),Color("OTColorCard2")])
                return gradient
                
            case "OT":
                let gradient = Gradient(colors: [Color("OTColorCard1"),Color("OTColorCard2")])
                return gradient
                
            case "DL":
                let gradient = Gradient(colors: [Color("DLColorCard1"),Color("DLColorCard2")])
                return gradient
                
            default:
                let gradient = Gradient(colors: [Color("NOColorCard1"),Color("NOColorCard2")])
                return gradient
            }
        case "LD":
            switch flightStatusObject.flightStatus?.arrtimestatus {
            case "FE":
                let gradient = Gradient(colors: [Color("OTColorCard1"),Color("OTColorCard2")])
                return gradient
                
            case "OT":
                let gradient = Gradient(colors: [Color("OTColorCard1"),Color("OTColorCard2")])
                return gradient
                
            case "DL":
                let gradient = Gradient(colors: [Color("DLColorCard1"),Color("DLColorCard2")])
                return gradient
                
            default:
                let gradient = Gradient(colors: [Color("NOColorCard1"),Color("NOColorCard2")])
                return gradient
            }
            
        case "CD":
            let gradient = Gradient(colors: [Color("CDColorCard1"),Color("CDColorCard2")])
            return gradient
        default:
            let gradient = Gradient(colors: [Color("NOColorCard1"),Color("NOColorCard2")])
            return gradient
        }
    }
    else {
        let gradient = Gradient(colors: [Color("NOColorCard1"),Color("NOColorCard2")])
        return gradient
    }
    
}



struct FlightCard: View {
    
    @ObservedObject var flightStatusObject:FlightStatusObject
    
    
    @State public var date = Date()
    
    var body: some View {
        //        GeometryReader { geometry in
        //                LinearGradient(gradient: Gradient(colors: [Color(#colorLiteral(red: 1, green: 1, blue: 1, alpha: 1)),Color(#colorLiteral(red: 0.4980392157, green: 0.7215686275, blue: 0, alpha: 1))]), startPoint: .top, endPoint: .bottom)
        //                Image("airplane_stock")
        //                    .resizable()
        //                    .aspectRatio(contentMode: .fit)
        //                    .brightness(0.5)
        //            HStack(alignment: .center){
        
        ZStack(alignment: .center) {
            //            RoundedRectangle(cornerRadius: 10, style: .continuous)
            LinearGradient(gradient: flightCardGradient(flightStatusObject: self.flightStatusObject), startPoint: .top, endPoint: .bottom)
                .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
                .shadow(radius: 3)
            
            
            //            HStack(alignment: .center) {
            VStack(alignment: .leading, spacing: 0) {
                HStack() {
                    Text("\(flightStatusObject.savedFlight?.airlineid ?? "")\(flightStatusObject.savedFlight?.flightnumber ?? "")").font(.title).bold()
                    if ((flightStatusObject.codeshareData?.operating?.airlineid != nil) && (flightStatusObject.savedFlight?.airlineid != flightStatusObject.codeshareData?.operating?.airlineid)) {
                        Text("(\(flightStatusObject.codeshareData?.operating?.airlineid ?? "")\(flightStatusObject.codeshareData?.operating?.flightnumber ?? ""))")
                    }
                    
                    Spacer()
                    if ((Date().addingTimeInterval(-86399) ... Date().addingTimeInterval(518399)).contains((self.flightStatusObject.flightStatus?.depscheduled!)!)) {
                        Button(action: {
//                            print("bell me")
                            self.flightStatusObject.notificationToggle()
                        })
                        {
                            Image(systemName: (self.flightStatusObject.notifications ? "bell.fill" : "bell")).font(.title)
                        }
                    }
                }
                Text(flightStatusObject.flightStatus?.depscheduledDateString ?? "")
                
                HStack() {
                    Spacer()
                    if flightStatusObject.flightStatus?.flightstatusString != "" {
                        Text(flightStatusObject.flightStatus?.flightstatusString ?? "no flight status").bold()
                        
                        if flightStatusObject.flightStatus?.deptimestatusString != "" {
                            Text("(\(flightStatusObject.flightStatus?.deptimestatusString?.replacingOccurrences(of: "Flight ", with: "") ?? "no time status"))")
                                .bold()
                        }
                    }
                    Spacer()
                }
                
                
                HStack() {
                    VStack(spacing: 0) {
                        
                        
                        HStack() {
                            
                            Text(flightStatusObject.flightStatus?.depscheduledString ?? "00:00").strikethrough((flightStatusObject.flightStatus?.depactualString != nil))
                            if flightStatusObject.flightStatus?.depactualString != nil {
                                Text("\(flightStatusObject.flightStatus?.depactualString ?? "00:00")")
                            }
                            else if flightStatusObject.flightStatus?.depestimatedString != nil {
                                Text("(est. \(flightStatusObject.flightStatus?.depestimatedString ?? "00:00"))")
                            }
                            Spacer()
                            if flightStatusObject.flightStatus?.arractualString != nil {
                                Text("\(flightStatusObject.flightStatus?.arractualString ?? "00:00")")
                            }
                            else if flightStatusObject.flightStatus?.arrestimatedString != nil {
                                Text("(est. \(flightStatusObject.flightStatus?.arrestimatedString ?? "00:00"))")
                            }
                            Text(flightStatusObject.flightStatus?.arrscheduledString ?? "00:00").strikethrough((flightStatusObject.flightStatus?.arractualString != nil))
                            
                        }
                        HStack() {
                            Text(flightStatusObject.flightStatus?.depairport ?? "/").font(.title).bold()
                            Spacer()
                            Image(systemName: "arrow.right").font(.title)
                            Spacer()
                            Text(flightStatusObject.flightStatus?.arrairport ?? "/").font(.title).bold()
                        }
                        HStack() {
                            Text(flightStatusObject.airportInfo?.depAirport?.airportName ?? "/")
                            Spacer()
                            Text(flightStatusObject.airportInfo?.arrAirport?.airportName ?? "/")
                        }
                    }
                    
                    
                    
                }
            }.padding(.all, 15)
            
        }
        .foregroundColor(Color("ColorText2"))
    }
    
    
}


//struct FlightCard_Previews: PreviewProvider {
//    static var previews: some View {
//        FlightCard()
//    }
//}
