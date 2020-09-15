//
//  StatisticsView.swift
//  FlightTracker
//
//  Created by Miha Strah on 21/07/2020.
//  Copyright © 2020 Miha Strah. All rights reserved.
//



import SwiftUI
import Foundation

struct StatisticsView: View {
    @ObservedObject var flightStatusObject: FlightStatusObject
    @State var pickerSelection = 1
    var days: Int
    
    
    var body: some View {
        VStack(alignment: .leading) {
            
            Picker(selection: $pickerSelection, label: Text("Stats")){
                Text("Departure").tag(0)
                Text("Arrival").tag(1)
            }
            .pickerStyle(SegmentedPickerStyle())
            .padding(.horizontal, 5)
            
            
            
            VStack(alignment: .center, spacing: 0){
                
                if days == 7 {
                    if flightStatusObject.stat7Day != nil {
                        
                        StatisticsPillView(
                            all: CGFloat(flightStatusObject.stat7Day?.allflights ?? 0),
                            cancelled: CGFloat(flightStatusObject.stat7Day?.cancelled ?? 0),
                            delayed: CGFloat(pickerSelection == 0 ? flightStatusObject.stat7Day?.dep_DL ?? 0 : flightStatusObject.stat7Day?.arr_DL ?? 0),
                            ontime: (pickerSelection == 0 ? (CGFloat(flightStatusObject.stat7Day?.dep_OT ?? 0) + CGFloat(flightStatusObject.stat7Day?.dep_FE ?? 0)) : (CGFloat(flightStatusObject.stat7Day?.arr_OT ?? 0) + CGFloat(flightStatusObject.stat7Day?.arr_FE ?? 0)))
                        )
                        .padding(.vertical, 15)
                        
                        
                        if flightStatusObject.stat7Day?.averageTimeArr != nil && flightStatusObject.stat7Day?.averageTimeDep != nil {
                            BarView(value: (pickerSelection == 0 ? CGFloat((flightStatusObject.stat7Day?.averageTimeDep)!) : CGFloat((flightStatusObject.stat7Day?.averageTimeArr)!)), text: (pickerSelection == 0 ? "Departure" : "Arrival"))
                            
                        }
                        if flightStatusObject.stat7Day?.averageTimeArr_DL != nil && flightStatusObject.stat7Day?.averageTimeDep_DL != nil {
                            BarView(value: (pickerSelection == 0 ? CGFloat((flightStatusObject.stat7Day?.averageTimeDep_DL)!) : CGFloat((flightStatusObject.stat7Day?.averageTimeArr_DL)!)), text: (pickerSelection == 0 ? "Average Delay" : "Average Delay"))
                        }
                    }
                }
                else if days == 30 {
                    
                    StatisticsPillView(
                        all: CGFloat(flightStatusObject.stat30Day?.allflights ?? 0),
                        cancelled: CGFloat(flightStatusObject.stat30Day?.cancelled ?? 0),
                        delayed: CGFloat(pickerSelection == 0 ? flightStatusObject.stat30Day?.dep_DL ?? 0 : flightStatusObject.stat30Day?.arr_DL ?? 0),
                        ontime: (pickerSelection == 0 ? (CGFloat(flightStatusObject.stat30Day?.dep_OT ?? 0) + CGFloat(flightStatusObject.stat30Day?.dep_FE ?? 0)) : (CGFloat(flightStatusObject.stat30Day?.arr_OT ?? 0) + CGFloat(flightStatusObject.stat30Day?.arr_FE ?? 0)))
                    )
                    .padding(.vertical, 15)
                    
                    if flightStatusObject.stat30Day != nil {
                        if flightStatusObject.stat30Day?.averageTimeArr != nil && flightStatusObject.stat30Day?.averageTimeDep != nil {
                            BarView(value: (pickerSelection == 0 ? CGFloat((flightStatusObject.stat30Day?.averageTimeDep)!) : CGFloat((flightStatusObject.stat30Day?.averageTimeArr)!)), text: (pickerSelection == 0 ? "Departure" : "Arrival"))
                        }
                        if flightStatusObject.stat30Day?.averageTimeArr_DL != nil && flightStatusObject.stat30Day?.averageTimeDep_DL != nil {
                            BarView(value: (pickerSelection == 0 ? CGFloat((flightStatusObject.stat30Day?.averageTimeDep_DL)!) : CGFloat((flightStatusObject.stat30Day?.averageTimeArr_DL)!)), text: (pickerSelection == 0 ? "Average Delay" : "Average Delay"))
                        }
                    }
                }
                
            }
        }.padding(.top, 5)
        
        
        
        
    }
    
}


struct BarView: View{
    
    var value: CGFloat = 0
    var text: String
    
    var body: some View {
        HStack {
            Spacer()
            VStack(alignment: .center) {
                Text("\(text):")
                    .font(.footnote)
                Text(" \(String(format: "%.0f", abs(Double(value)))) min \(value > 0 ? "late" : "early")").padding(.leading, 5)
                    .font(.callout)
                    .lineLimit(nil)
                    .fixedSize(horizontal: false, vertical: true)
            }
            
            Spacer()
            ZStack (alignment: .leading) {
                Color("ColorGray3").frame(width: 4, height: 50)
                    .offset(x: -2)
                    .animation(.spring())
                Capsule()
                    .frame(width: 170, height: 20)
                    .foregroundColor(Color("ColorGray3"))
                    .offset(x: -40)
                    .animation(.spring())
                RoundedRectangle(cornerRadius: 25)
                    .fill(LinearGradient(gradient: ((value > 5) ? Gradient(colors: [Color("DLColor1"),Color("DLColor2")]) : Gradient(colors: [Color("OTColor1"),Color("OTColor2")])), startPoint: (.leading), endPoint: .trailing))
                    //min time -30, max time +120 (0min is 20 wide)
                    //                    .frame(width: (value >= 0 ? min(value+20, 140) : max(value-20, -50)), height: 20)
                    .frame(width: (value >= 0 ? min(value+20, 140) : min( abs(value) + 20, 50)), height: 20)
                    //                    .offset(x: (value >= 0 ? -10 : 10))
                    .offset(x: (value >= 0 ? -10 : (10 - min(abs(value) + 20, 50))))
                    .animation(.spring())
                if value > 120 {
                    Image(systemName: "plus").offset(x: 110)
                        .foregroundColor(Color("ColorGray3"))
                        .animation(.spring())
                }
                if value < -30 {
                    Image(systemName: "minus").offset(x: -30)
                        .foregroundColor(Color("ColorGray3"))
                        .animation(.spring())
                }
            }
            .offset(x: 40)
            .padding(.horizontal, 15)
            
        }
    }
}




struct StatisticsView_Previews: PreviewProvider {
    static var previews: some View {
        StatisticsView(flightStatusObject: FlightStatusObject(), days: 7)
    }
}
