//
//  StatisticsPillView.swift
//  FlightTracker
//
//  Created by Miha Strah on 23/07/2020.
//  Copyright © 2020 Miha Strah. All rights reserved.
//

import SwiftUI

struct StatisticsPillView: View {
    var all: CGFloat = 0
    var cancelled: CGFloat = 0
    var delayed: CGFloat = 0
    var ontime: CGFloat = 0
    
    let capsuleWidth: CGFloat = 300
    
    var body: some View {
        VStack() {
            
            if #available(iOS 14.0, *) {
                ZStack (alignment: .leading) {
                    Capsule()
                        .frame(width: capsuleWidth, height: 20)
                        .foregroundColor(Color(.gray))
                        .animation(.spring())
                    if cancelled != 0 {
                        Rectangle()
                            .foregroundColor(.clear)
                            .frame(width: (self.percent(value: cancelled) * capsuleWidth), height: 20)
                            .background(LinearGradient(gradient: Gradient(colors: [Color("CDColor1"),Color("CDColor2")]), startPoint: .leading, endPoint: .trailing))
                            .offset(x: 0)
                            .animation(.spring())
                    }
                    if delayed != 0 {
                        Rectangle()
                            .foregroundColor(.clear)
                            .frame(width: (self.percent(value: delayed) * capsuleWidth), height: 20)
                            .background(LinearGradient(gradient: Gradient(colors: [Color("DLColor1"),Color("DLColor2")]), startPoint: .leading, endPoint: .trailing))
                            .offset(x: (self.percent(value: cancelled) * capsuleWidth))
                            .animation(.spring())
                    }
                    if ontime != 0 {
                        Rectangle()
                            .foregroundColor(.clear)
                            .frame(width: (self.percent(value: ontime) * capsuleWidth), height: 20)
                            .background(LinearGradient(gradient: Gradient(colors: [Color("OTColor1"),Color("OTColor2")]), startPoint: .leading, endPoint: .trailing))
                            .offset(x: (self.percent(value: cancelled) * capsuleWidth) + (self.percent(value: delayed) * capsuleWidth))
                            .animation(.spring())
                    }
                }
                .mask(RoundedRectangle(cornerRadius: 15, style: .continuous))
            } else {
                ZStack (alignment: .leading) {
                    Capsule()
                        .frame(width: capsuleWidth, height: 20)
                        .foregroundColor(Color(.gray))
                        .animation(.spring())
                    if cancelled != 0 {
                        Rectangle()
                            .foregroundColor(.clear)
                            .frame(width: (self.percent(value: cancelled) * capsuleWidth), height: 20)
                            .background(LinearGradient(gradient: Gradient(colors: [Color("CDColor1"),Color("CDColor2")]), startPoint: .leading, endPoint: .trailing))
                            .offset(x: 0)
                            .animation(.spring())
                    }
                    if delayed != 0 {
                        Rectangle()
                            .foregroundColor(.clear)
                            .frame(width: (self.percent(value: delayed) * capsuleWidth), height: 20)
                            .background(LinearGradient(gradient: Gradient(colors: [Color("DLColor1"),Color("DLColor2")]), startPoint: .leading, endPoint: .trailing))
                            .offset(x: (self.percent(value: cancelled) * capsuleWidth))
                            .animation(.spring())
                    }
                    if ontime != 0 {
                        Rectangle()
                            .foregroundColor(.clear)
                            .frame(width: (self.percent(value: ontime) * capsuleWidth), height: 20)
                            .background(LinearGradient(gradient: Gradient(colors: [Color("OTColor1"),Color("OTColor2")]), startPoint: .leading, endPoint: .trailing))
                            .offset(x: (self.percent(value: cancelled) * capsuleWidth) + (self.percent(value: delayed) * capsuleWidth))
                            .animation(.spring())
                    }
                }.clipShape(Capsule())
            }
            
            HStack() {
                Spacer()
                Circle()
                    .frame(width: 10, height:10, alignment: /*@START_MENU_TOKEN@*/.center/*@END_MENU_TOKEN@*/)
                    .foregroundColor(Color("CDColor1"))
                Text("Canceled: \(String(format: "%.0f", cancelled))")
                    .font(.footnote)
                //                    .animation(.linear)
                Spacer()
                Circle()
                    .frame(width: 10, height:10, alignment: .center)
                    .foregroundColor(Color("DLColor1"))
                Text("Delayed: \(String(format: "%.0f", delayed))")
                    .font(.footnote)
                //                    .animation(.linear)
                Spacer()
                Circle()
                    .frame(width: 10, height:10, alignment: /*@START_MENU_TOKEN@*/.center/*@END_MENU_TOKEN@*/)
                    .foregroundColor(Color("OTColor1"))
                Text("On Time: \(String(format: "%.0f", ontime))")
                    .font(.footnote)
                //                    .animation(.linear)
                
                Spacer()
            }
        }
        
        
    }
    
    func percent(value: CGFloat) -> CGFloat {
        return (value / self.all)
    }
}

//
//extension View {
//    func cornerRadius(_ radius: CGFloat, corners: UIRectCorner) -> some View {
//        clipShape( RoundedCorner(radius: radius, corners: corners) )
//    }
//}
//struct RoundedCorner: Shape {
//
//    var radius: CGFloat = .infinity
//    var corners: UIRectCorner = .allCorners
//
//    func path(in rect: CGRect) -> Path {
//        let path = UIBezierPath(roundedRect: rect, byRoundingCorners: corners, cornerRadii: CGSize(width: radius, height: radius))
//        return Path(path.cgPath)
//    }
//}







struct StatisticsPillView_Previews: PreviewProvider {
    static var previews: some View {
        StatisticsPillView()
    }
}
