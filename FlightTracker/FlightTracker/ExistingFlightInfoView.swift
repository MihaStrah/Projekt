//
//  test.swift
//  FlightTracker
//
//  Created by Miha Strah on 16/07/2020.
//  Copyright © 2020 Miha Strah. All rights reserved.
//

import SwiftUI

func flightStatusColor(flightStatusObject: FlightStatusObject) -> Color {
    if (flightStatusObject.flightStatus?.flightstatusString != "" && flightStatusObject.flightStatus?.flightstatus != nil) {
        switch flightStatusObject.flightStatus?.flightstatus {
        case "DP":
            switch flightStatusObject.flightStatus?.deptimestatus {
            case "FE":
                return Color("OTColorCard1")
                
            case "OT":
                return Color("OTColorCard1")
                
            case "DL":
                return Color("DLColorCard1")
                
            default:
                return Color("NOColorCard1")
            }
        case "LD":
            switch flightStatusObject.flightStatus?.arrtimestatus {
            case "FE":
                return Color("OTColorCard1")
                
            case "OT":
                return Color("OTColorCard1")
                
            case "DL":
                return Color("DLColorCard1")
                
            default:
                return Color("NOColorCard1")
            }
            
        case "CD":
            return Color("CDColorCardText")
        default:
            return Color("NOColorCard1")
        }
    }
    else {
        return Color("NOColorCard1")
    }
}



func flightStatusAirportColor(flightStatusObject: FlightStatusObject, arrival: Bool) -> Color {
    
    if (flightStatusObject.flightStatus?.flightstatusString != "" && flightStatusObject.flightStatus?.flightstatus != nil) {
        switch flightStatusObject.flightStatus?.flightstatus {
        case "DP":
            if !arrival {
                switch flightStatusObject.flightStatus?.deptimestatus {
                case "FE":
                    return Color("OTColorCard1")
                    
                case "OT":
                    return Color("OTColorCard1")
                    
                case "DL":
                    return Color("DLColorCard1")
                    
                default:
                    return Color("NOColorCard1")
                }
            }
            else {
                return Color("ColorText1")
            }
        case "LD":
            if arrival {
                switch flightStatusObject.flightStatus?.arrtimestatus {
                case "FE":
                    return Color("OTColorCard1")
                    
                case "OT":
                    return Color("OTColorCard1")
                    
                case "DL":
                    return Color("DLColorCard1")
                    
                default:
                    return Color("ColorText1")
                }
            }
            else {
                switch flightStatusObject.flightStatus?.deptimestatus {
                case "FE":
                    return Color("OTColorCard1")
                    
                case "OT":
                    return Color("OTColorCard1")
                    
                case "DL":
                    return Color("DLColorCard1")
                    
                default:
                    return Color("NOColorCard1")
                }
            }
            
        default:
            return Color("ColorText1")
        }
    }
    else {
        return Color("ColorText1")
    }
}



struct ExistingFlightInfoView: View {
    
    static let taskDateFormat: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateStyle = .long
        formatter.timeStyle = .long
        return formatter
    }()
    
    @ObservedObject var flightStatusObject: FlightStatusObject
    
    @State public var showingImageView = false
    
    @State public var isPresentedDates = false
    @State public var isPresentedAircraft = false
    
    var body: some View {
        
        VStack() {
            if (self.flightStatusObject.searchOK){
                
                ZStack() {
                    
                    RoundedRectangle(cornerRadius: 10, style: .continuous)
                    //                        .animation(.linear(duration:3))
                    //                        .transition(AnyTransition.scale.animation(.easeInOut(duration: 3.0)))
                    //                Color("ColorCard1")
                    
                    VStack(alignment: .leading, spacing: 4) {
                        HStack() {
                            Text("\(flightStatusObject.savedFlight?.airlineid ?? "")\(flightStatusObject.savedFlight?.flightnumber ?? "")")
                                .font(.headline)
                            if (flightStatusObject.airlineInfo?.airlineName != nil) {
                                Text("operated by \(flightStatusObject.airlineInfo?.airlineName ?? "")")
                                    .font(.subheadline)
                                
                            }
                        }
                        .foregroundColor(/*@START_MENU_TOKEN@*/.blue/*@END_MENU_TOKEN@*/)
                        Text(flightStatusObject.flightStatus?.depscheduledDateString ?? "")
                            .font(.subheadline)
                        if flightStatusObject.flightStatus?.flightstatusString != nil {
                            HStack() {
                                Spacer()
                                Text(flightStatusObject.flightStatus?.flightstatusString ?? "")
                                    .font(.title)
                                    .bold()
                                    .foregroundColor(flightStatusColor(flightStatusObject: self.flightStatusObject))
                                
                                Spacer()
                            }
                        }
                        
                        HStack(){
                            Text(flightStatusObject.flightStatus?.depscheduledString ?? "")
                                .font(.title)
                            if flightStatusObject.flightStatus?.depactualString != nil {
                                VStack() {
                                    Text("Actual")
                                        .font(.caption)
                                    Text("(\(flightStatusObject.flightStatus?.depactualString ?? ""))")
                                        .font(.body)
                                }.foregroundColor(flightStatusAirportColor(flightStatusObject: self.flightStatusObject, arrival: false))
                            }
                            else if flightStatusObject.flightStatus?.depestimatedString != nil {
                                VStack() {
                                    Text("Estimated")
                                        .font(.caption)
                                    Text("(\(flightStatusObject.flightStatus?.depestimatedString ?? ""))")
                                        .font(.body)
                                }
                            }
                            Spacer()
                            if flightStatusObject.flightStatus?.arractualString != nil {
                                VStack() {
                                    Text("Actual")
                                        .font(.caption)
                                    Text("(\(flightStatusObject.flightStatus?.arractualString ?? ""))")
                                        .font(.body)
                                    
                                }.foregroundColor(flightStatusAirportColor(flightStatusObject: self.flightStatusObject, arrival: true))
                            }
                            else if flightStatusObject.flightStatus?.arrestimatedString != nil {
                                VStack() {
                                    Text("Estimated")
                                        .font(.caption)
                                    Text("(\(flightStatusObject.flightStatus?.arrestimatedString ?? ""))")
                                        .font(.body)
                                }
                            }
                            Text(flightStatusObject.flightStatus?.arrscheduledString ?? "")
                                .font(.title)
                            
                        }
                        .padding(.vertical, 5.0)
                        HStack(){
                            if flightStatusObject.flightStatus?.deptimestatusString != "" {
                                Text(flightStatusObject.flightStatus?.deptimestatusString ?? "")
                                    .font(.callout)
                            }
                            Spacer()
                            if flightStatusObject.flightStatus?.arrtimestatusString != "" {
                                Text(flightStatusObject.flightStatus?.arrtimestatusString ?? "")
                                    .font(.callout)
                                
                            }
                        }
                        
                        
                        HStack(){
                            Spacer()
                            VStack() {
                                Text(flightStatusObject.flightStatus?.depairport ?? "")
                                    .font(.title)
                                    .foregroundColor(/*@START_MENU_TOKEN@*/.blue/*@END_MENU_TOKEN@*/)
                                Text(flightStatusObject.airportInfo?.depAirport?.airportName ?? "")
                                    .font(.body)
                            }
                            Spacer()
                            Image(systemName: "arrow.right").font(.title)
                            Spacer()
                            VStack() {
                                Text(flightStatusObject.flightStatus?.arrairport ?? "")
                                    .font(.title)
                                    .foregroundColor(/*@START_MENU_TOKEN@*/.blue/*@END_MENU_TOKEN@*/)
                                Text(flightStatusObject.airportInfo?.arrAirport?.airportName ?? "")
                                    .font(.body)
                            }
                            Spacer()
                        }
                        
                        HStack(){
                            if flightStatusObject.flightStatus?.depterminal != "" {
                                Text("Terminal ")
                                    .font(.subheadline)
                                
                                Text(flightStatusObject.flightStatus?.depterminal ?? "")
                                    .font(.subheadline)
                                    .bold()
                            }
                            if flightStatusObject.flightStatus?.depgate != "" {
                                Text("Gate ")
                                    .font(.subheadline)
                                Text(flightStatusObject.flightStatus?.depgate ?? "")
                                    .font(.subheadline)
                                    .bold()
                            }
                            Spacer()
                            if flightStatusObject.flightStatus?.arrterminal != "" {
                                Text("Terminal ")
                                    .font(.subheadline)
                                Text(flightStatusObject.flightStatus?.arrterminal ?? "")
                                    .font(.subheadline)
                                    .bold()
                            }
                            if flightStatusObject.flightStatus?.arrgate != "" {
                                Text("Gate ")
                                    .font(.subheadline)
                                Text(flightStatusObject.flightStatus?.arrgate ?? "")
                                    .font(.subheadline)
                                    .bold()
                            }
                        }
                    }
                    .foregroundColor(Color("ColorText1"))
                    .padding(/*@START_MENU_TOKEN@*/.all/*@END_MENU_TOKEN@*/, 15)
                }
                .foregroundColor(Color("ColorCard1"))
                //                .transition(.asymmetric(insertion: .move(edge: .leading), removal: .scale(scale: 10)))
                //                .animation(.linear(duration: 2))
                //                .transition(AnyTransition.slide)
                //                .animation(.default)
                //        .padding(/*@START_MENU_TOKEN@*/.all/*@END_MENU_TOKEN@*/, 15)
                //        .background(Color("ColorCard1"))
                //        .cornerRadius(10)
                
            }
            //            .animation(.linear(duration: 4))
            
            

            
            if (self.flightStatusObject.codeshareData?.codeshares != nil && !(self.flightStatusObject.codeshareData?.codeshares?.isEmpty ?? true) ){
                ZStack(alignment: .topLeading) {
                    RoundedRectangle(cornerRadius: 10, style: .continuous)
                    //                        .animation(.linear(duration:3))
                    
                    //                Color("ColorCard1")
                    VStack(alignment: .leading, spacing: 4) {
                        
                        Text("Codeshare Flights")
                            .font(.headline)
                            .foregroundColor(/*@START_MENU_TOKEN@*/.blue/*@END_MENU_TOKEN@*/)
                        HStack() {
                            Text("Operating: ")
                                .font(.callout)
                            Text("\(self.flightStatusObject.codeshareData!.operating!.airlineid!)\(self.flightStatusObject.codeshareData!.operating!.flightnumber!)")
                                .font(.body)
                        }
                        
                        HStack(alignment: .top) {
                            Text("Codeshare: ")
                                .font(.callout)
                            
                            Text(self.flightStatusObject.codeshareData!.getString())
                                .lineLimit(nil)
                                
                            
                            //                                ForEach(self.flightStatusObject.codeshareData!.codeshares!) { codeshare in
                            //                                    Text("\(codeshare.airlineid!)\(codeshare.flightnumber!) ")
                            //                                        .font(.body)
                            //                                }
                        }
                    }
                    .foregroundColor(Color("ColorText1"))
                    .padding(/*@START_MENU_TOKEN@*/.all/*@END_MENU_TOKEN@*/, 15)
                }
                .fixedSize(horizontal: false, vertical: true)
                .foregroundColor(Color("ColorCard1"))
                //                .transition(.asymmetric(insertion: .move(edge: .leading), removal: .scale(scale: 10)))
                //                .animation(.linear(duration: 2))
                //                .transition(AnyTransition.slide)
                //                .animation(.default)
                //            .padding(/*@START_MENU_TOKEN@*/.all/*@END_MENU_TOKEN@*/, 15)
                //            .background(Color("ColorCard1"))
                //            .cornerRadius(10)
                
            }
            
            
            if (self.flightStatusObject.flightStatus?.aircraftcode != nil && self.flightStatusObject.flightStatus?.aircraftcode != ""){
                ZStack(alignment: .topLeading) {
                    RoundedRectangle(cornerRadius: 10, style: .continuous)
                    //                        .animation(.linear(duration:3))
                    //                Color("ColorCard1")
                    HStack() {
                        VStack(alignment: .leading, spacing: 4) {
                            
                            Text("Aircraft")
                                .font(.headline)
                                .foregroundColor(/*@START_MENU_TOKEN@*/.blue/*@END_MENU_TOKEN@*/)
                            HStack(alignment: .top) {
                                Text("Code:")
                                    .font(.callout)
                                Text("\(self.flightStatusObject.aircraftInfo?.aircraftName ?? "")")
                                    .font(.body)
                                    .lineLimit(nil)
                                    
                            }
                            
                            if (self.flightStatusObject.flightStatus?.aircraftreg != nil && self.flightStatusObject.flightStatus?.aircraftreg != "") {
                                HStack(alignment: .top) {
                                    Text("Registration:")
                                        .font(.callout)
                                    Text("\(self.flightStatusObject.flightStatus?.aircraftreg ?? "")")
                                        .font(.body)
                                        .lineLimit(nil)
                                        
                                }
                            }
                            
                            if (((flightStatusObject.aircraftLocation != nil) && ((flightStatusObject.aircraftLocation?.updated)! > Date().addingTimeInterval(-120)) && (flightStatusObject.aircraftLocation?.latitude != nil) && (flightStatusObject.aircraftLocation?.longitude != nil)) || (isPresentedAircraft)) {
                            Button(action: {
    //                            print("check")
                                self.isPresentedAircraft.toggle()
                            }) {
                                Text("Location")
                                    .bold()
                                    .foregroundColor(.white)
                                    .padding(.all,10)
                                    .padding([.leading, .trailing], 30)
                                    .background(Color.blue)
                                    .cornerRadius(20)
                            }.sheet(isPresented: $isPresentedAircraft) {
                                AircraftMapView(flightStatusObject: self.flightStatusObject)
                            }
                            .padding(.top, 15)
                            }
                            
                        }
                        
                        if ((self.flightStatusObject.urlImageModel != nil) && (self.flightStatusObject.urlImageModel?.image != nil)) {
                            Spacer()
                            
                            Image(uiImage: self.flightStatusObject.urlImageModel!.image!)
                                .resizable()
                                //                                .padding(/*@START_MENU_TOKEN@*/.all/*@END_MENU_TOKEN@*/, 15)
                                .aspectRatio(contentMode: /*@START_MENU_TOKEN@*/.fill/*@END_MENU_TOKEN@*/)
                                .frame(width: 150, height: 100, alignment: .trailing)
                                //                                .clipped()
                                
                                .animation(.spring())
                                .gesture(
                                    TapGesture()
                                        .onEnded { _ in
                                            self.showingImageView.toggle()
                                        }
                                )
                                .sheet(isPresented: $showingImageView) {
                                    AircraftImageOnlyView(flightStatusObject: self.flightStatusObject)
                                }
                                }
                    }
                    .foregroundColor(Color("ColorText1"))
                    .padding(/*@START_MENU_TOKEN@*/.all/*@END_MENU_TOKEN@*/, 15)
                }.fixedSize(horizontal: false, vertical: true)
                
                .foregroundColor(Color("ColorCard1"))
                //                .transition(.asymmetric(insertion: .move(edge: .leading), removal: .scale(scale: 10)))
                //                .animation(.linear(duration: 2))
                //                .transition(AnyTransition.slide)
                //                .animation(.default)
                //            .padding(/*@START_MENU_TOKEN@*/.all/*@END_MENU_TOKEN@*/, 15)
                //            .background(Color("ColorCard1"))
                //            .cornerRadius(10)
                
            }
            
            if self.flightStatusObject.stat7Day != nil {
                ZStack(alignment: .topLeading) {
                    RoundedRectangle(cornerRadius: 10, style: .continuous)
                    //                        .animation(.linear(duration:3))
                    //                Color("ColorCard1")
                    VStack(alignment: .leading, spacing: 4) {
                        
                        Text("Statistics for last week")
                            .font(.headline)
                            .foregroundColor(/*@START_MENU_TOKEN@*/.blue/*@END_MENU_TOKEN@*/)
                        
                        StatisticsView(flightStatusObject: self.flightStatusObject, days: 7)
                        
                    }
                    .foregroundColor(Color("ColorText1"))
                    .padding(/*@START_MENU_TOKEN@*/.all/*@END_MENU_TOKEN@*/, 15)
                    
                }
                .foregroundColor(Color("ColorCard1"))
                //                .transition(AnyTransition.slide)
                //                .animation(.default)
                //            .padding(/*@START_MENU_TOKEN@*/.all/*@END_MENU_TOKEN@*/, 15)
                //            .background(Color("ColorCard1"))
                //            .cornerRadius(10)
                
            }
            
            if self.flightStatusObject.stat30Day != nil {
                ZStack(alignment: .topLeading) {
                    RoundedRectangle(cornerRadius: 10, style: .continuous)
                    //                        .animation(.linear(duration:3))
                    //                Color("ColorCard1")
                    VStack(alignment: .leading, spacing: 4) {
                        
                        Text("Statistics for last month")
                            .font(.headline)
                            .foregroundColor(/*@START_MENU_TOKEN@*/.blue/*@END_MENU_TOKEN@*/)
                        
                        StatisticsView(flightStatusObject: self.flightStatusObject, days: 30)
                        
                        
                        
                        //                        if #available(iOS 14.0, *) {
                        Button(action: {
//                            print("check")
                            self.isPresentedDates.toggle()
                        }) {
                            Text("More history")
                                .bold()
                                .foregroundColor(.white)
                                .padding(.all,10)
                                .padding([.leading, .trailing], 30)
                                .background(Color.blue)
                                .cornerRadius(20)
                        }.sheet(isPresented: $isPresentedDates) {
                            StatisticsCalendarView(flightStatusObject: self.flightStatusObject, isPresentedDates: self.$isPresentedDates)
                        }
                        .padding(.top, 15)
                        //                        } else {
                        //                            // Fallback on earlier versions
                        //                        }
                        
                        
                    }
                    .foregroundColor(Color("ColorText1"))
                    .padding(/*@START_MENU_TOKEN@*/.all/*@END_MENU_TOKEN@*/, 15)
                    
                }
                
                .foregroundColor(Color("ColorCard1"))
                //                .transition(AnyTransition.slide)
                //                .animation(.default)
                //            .padding(/*@START_MENU_TOKEN@*/.all/*@END_MENU_TOKEN@*/, 15)
                //            .background(Color("ColorCard1"))
                //            .cornerRadius(10)
            }
            
            if (self.flightStatusObject.airportInfo?.arrAirport?.latitude != nil && self.flightStatusObject.airportInfo?.depAirport?.latitude != nil) {
                ZStack(alignment: .topLeading) {
                    RoundedRectangle(cornerRadius: 10, style: .continuous)
                    //                        .animation(.linear(duration:3))
                    //                Color("ColorCard1")
                    VStack(alignment: .leading, spacing: 4) {
                        
                        Text("Map")
                            .font(.headline)
                            .foregroundColor(/*@START_MENU_TOKEN@*/.blue/*@END_MENU_TOKEN@*/)
                        AirportMapView(flightStatusObject: self.flightStatusObject)
                            
                        
                        
                    }
                    .foregroundColor(Color("ColorText1"))
                    .padding(/*@START_MENU_TOKEN@*/.all/*@END_MENU_TOKEN@*/, 15)
                }
                
                .foregroundColor(Color("ColorCard1"))
                //                .transition(AnyTransition.slide)
                //                .animation(.default)
                //            .padding(/*@START_MENU_TOKEN@*/.all/*@END_MENU_TOKEN@*/, 15)
                //            .background(Color("ColorCard1"))
                //            .cornerRadius(10)
                
                
            }
            
            
            
            
            
            VStack(spacing: 5){


//!self.flightStatusObject.searchInProgress && 
                if (self.flightStatusObject.searchOK && (self.flightStatusObject.lastUpdated != nil)) {
                    HStack() {
                        Text("Last updated \(self.flightStatusObject.lastUpdated!, formatter: Self.taskDateFormat)")
                            .font(.footnote)
                            .foregroundColor(Color("ColorText1"))
                    }

                }

                if (self.flightStatusObject.searchOK) {
                    HStack() {
                        Text("Flight data by Lufthansa")
                            .font(.footnote)
                            .foregroundColor(Color("ColorText1"))
                    }


                }

                if (self.flightStatusObject.searchOK && (self.flightStatusObject.urlImageModel?.image != nil)) {
                    HStack() {
                        Text("Aircraft image by \(self.flightStatusObject.imageData?.photographer ?? "Unknown") (airport-data.com)")
                            .font(.footnote)
                            .foregroundColor(Color("ColorText1"))
                    }


                }


            }
            .padding(.all, 15)
            
            
            
            
            
            //        .padding(.top, 10)
            //        .padding(.bottom, 60)
            //        .padding(.horizontal, /*@START_MENU_TOKEN@*/10/*@END_MENU_TOKEN@*/)
            
            
        }
    }
}













//struct test_Previews: PreviewProvider {
//    static var previews: some View {
//        FlightInfoView(flightStatusObject: FlightStatusObject())
//    }
//}

