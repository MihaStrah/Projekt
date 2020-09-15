//
//  RKViewController.swift
//  RKCalendar
//
//  Created by Raffi Kian on 7/14/19.
//  Copyright © 2019 Raffi Kian. All rights reserved.
//

import SwiftUI

struct RKViewController: View {
    
    @Binding var isPresented: Bool
    
    @ObservedObject var rkManager: RKManager
    
    var body: some View {
        //        Group {
        //            RKWeekdayHeader(rkManager: self.rkManager)
        //            Divider()
        //            List {
        //                ForEach(0..<numberOfMonths()) { index in
        //                    RKMonth(isPresented: self.$isPresented, rkManager: self.rkManager, monthOffset: index)
        //                    //Divider()
        //                }
        //
        //            }
        //
        Group {
            RKWeekdayHeader(rkManager: self.rkManager)
            //USE THIS  when bug in xcode resolved->
//            ScrollView {
//                VStack(spacing: 10) {
//                    if #available(iOS 14.0, *) {
//                        ScrollViewReader { value in
//                            ForEach(0..<numberOfMonths()) { index in
//                                RKMonth(isPresented: self.$isPresented, rkManager: self.rkManager, monthOffset: index)
//                            }
//                            .onAppear {
//                                value.scrollTo(numberOfMonths() - 1, anchor: .bottom)
//                            }
//                        }
//                    } else {
//                        ForEach(0..<numberOfMonths()) { index in
//                            RKMonth(isPresented: self.$isPresented, rkManager: self.rkManager, monthOffset: index)
//                            //Divider()
//                        }
//                    }
//                }
//            }.padding(.horizontal, 10)
            
            
                        ScrollView() {
                            VStack(spacing: 10) {
                            ForEach(0..<numberOfMonths()) { index in
                                RKMonth(isPresented: self.$isPresented, rkManager: self.rkManager, monthOffset: (index))
                                    
                        }
            
                            }
//                            render with metal
                            .drawingGroup()
                            
                        }.padding(.horizontal, 10)
            
            
        }
    }
    
    func numberOfMonths() -> Int {
        return rkManager.calendar.dateComponents([.month], from: rkManager.minimumDate, to: RKMaximumDateMonthLastDay()).month! + 2
    }
    
    func RKMaximumDateMonthLastDay() -> Date {
        var components = rkManager.calendar.dateComponents([.year, .month, .day], from: rkManager.maximumDate)
        components.month! += 1
        components.day = 0
        
        return rkManager.calendar.date(from: components)!
    }
}

//
//struct RKViewController_Previews : PreviewProvider {
//    static var previews: some View {
//        Group {
////            RKViewController(isPresented: .constant(false), rkManager: RKManager(calendar: Calendar.current, minimumDate: Date(), maximumDate: Date().addingTimeInterval(60*60*24*365), mode: 0))
////            RKViewController(isPresented: .constant(false), rkManager: RKManager(calendar: Calendar.current, minimumDate: Date(), maximumDate: Date().addingTimeInterval(60*60*24*32), mode: 0))
////                .environment(\.colorScheme, .dark)
////                .environment(\.layoutDirection, .rightToLeft)
//        }
//    }
//}
//
//
