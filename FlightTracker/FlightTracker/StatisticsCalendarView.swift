//
//  StatisticsCalendarView.swift
//  FlightTracker
//
//  Created by Miha Strah on 22/07/2020.
//  Copyright © 2020 Miha Strah. All rights reserved.
//

import SwiftUI

struct StatisticsCalendarView: View {
    @ObservedObject var flightStatusObject: FlightStatusObject
    
    @Binding public var isPresentedDates: Bool
    //@State public var isPresentedDates = true
    
    @State public var singleIsPresented = true
    
    //    var rkManager1 = RKManager(calendar: Calendar.current, minimumDate: Date().addingTimeInterval(-60*60*24*10), maximumDate: Date().addingTimeInterval(60*60*24*18), mode: 4, cancelledDates: [Date().addingTimeInterval(-60*60*24),Date().addingTimeInterval(-60*60*24*3)], onTimeDates: [Date().addingTimeInterval(-60*60*24*3)], delayedDates: [Date().addingTimeInterval(-60*60*24*9)])
    
    
    var body: some View {
        
        //        if self.flightStatusObject.statDays != nil {
        //            RKViewController(isPresented: $singleIsPresented, rkManager: RKManager(calendar: Calendar.current, minimumDate: Date().addingTimeInterval(-60*60*24*90), maximumDate: Date().addingTimeInterval(60*60*24*0), mode: 4, cancelledDates: (self.flightStatusObject.statDays?.statDayDates!.cancelledDates)!, onTimeDates: (self.flightStatusObject.statDays?.statDayDates!.ontimeDates)!, delayedDates: (self.flightStatusObject.statDays?.statDayDates!.delayedDates)!))
        //        }
        
        VStack(alignment: .leading) {
            Text("Statistics for last 90 days")
                .font(.headline)
                .foregroundColor(/*@START_MENU_TOKEN@*/.blue/*@END_MENU_TOKEN@*/)
                .padding(.all, 15)
            
            
            
            
            //RKViewController(isPresented: $singleIsPresented, rkManager: rkManager1)
            if self.flightStatusObject.statDays != nil {
                
                RKViewController(isPresented: $singleIsPresented, rkManager: RKManager(calendar: Calendar.current, minimumDate: self.flightStatusObject.lastUpdated?.addingTimeInterval(-60*60*24*90) ?? Date(), maximumDate: self.flightStatusObject.lastUpdated ?? Date(), mode: 4, cancelledDates: (self.flightStatusObject.statDays?.statDayDates!.cancelledDates)!, onTimeDates: (self.flightStatusObject.statDays?.statDayDates!.ontimeDates)!, delayedDates: (self.flightStatusObject.statDays?.statDayDates!.delayedDates)!))
                //                    .padding(.horizontal, 10)
            }
            
            
            //            if self.flightStatusObject.statDays != nil {
            //                RKViewController(isPresented: $singleIsPresented, rkManager: RKManager(calendar: Calendar.current, minimumDate: Date().addingTimeInterval(-60*60*24*90), maximumDate: Date().addingTimeInterval(60*60*24*0), mode: 4, cancelledDates: (self.flightStatusObject.statDays?.statDayDates!.cancelledDates)!, onTimeDates: (self.flightStatusObject.statDays?.statDayDates!.ontimeDates)!, delayedDates: (self.flightStatusObject.statDays?.statDayDates!.delayedDates)!))
            ////                    .padding(.horizontal, 10)
            //            }
            
            
            HStack() {
                Spacer()
                Circle()
                    .frame(width: 10, height:10, alignment: .center)
                    .foregroundColor(Color("OTColor1"))
                Text("On Time")
                    .font(.caption)
                Circle()
                    .frame(width: 10, height:10, alignment: .center)
                    .foregroundColor(Color("DLColor1"))
                Text("Delayed")
                    .font(.caption)
                Circle()
                    .frame(width: 10, height:10, alignment: .center)
                    .foregroundColor(Color("CDColor1"))
                Text("Canceled")
                    .font(.caption)
                ZStack() {
                    Circle()
                        .frame(width: 10, height:10, alignment: .center)
                        .foregroundColor(Color("ColorCard1"))
                    //                    Circle()
                    //                        .frame(width: 8, height:8, alignment: .center)
                    //                        .foregroundColor(.white)
                }
                Text("No Flight")
                    .font(.caption)
                Spacer()
            }
            .padding(.vertical, 15)
            .padding(.bottom, 20)
        }.background(Color("ColorGray1"))
        .edgesIgnoringSafeArea(.bottom)
        
        
        
    }
}

//struct StatisticsCalendarView_Previews: PreviewProvider {
//    static var previews: some View {
//        StatisticsCalendarView(flightStatusObject: FlightStatusObject())
//    }
//}
