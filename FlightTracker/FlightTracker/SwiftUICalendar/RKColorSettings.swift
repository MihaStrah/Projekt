//
//  RKColorSettings.swift
//  RKCalendar
//
//  Copyright © 2019 Raffi Kian. All rights reserved.
//

import Foundation
import Combine
import SwiftUI

class RKColorSettings : ObservableObject {

    // foreground colors
    @Published var textColor: Color = Color.primary
    @Published var todayColor: Color = Color.white
    @Published var selectedColor: Color = Color.white
    @Published var disabledColor: Color = Color.gray
    @Published var betweenStartAndEndColor: Color = Color.white
    // background colors
    @Published var textBackColor: Color = Color.clear
    @Published var todayBackColor: Color = Color.blue
    @Published var selectedBackColor: Color = Color.red
    @Published var disabledBackColor: Color = Color.clear
    @Published var betweenStartAndEndBackColor: Color = Color.blue
    // headers foreground colors
    @Published var weekdayHeaderColor: Color = Color.primary
    @Published var monthHeaderColor: Color = Color.primary
    // headers background colors
    @Published var weekdayHeaderBackColor: Color = Color.clear
    @Published var monthBackColor: Color = Color("ColorCard1")
    
//    @Published var cancelledColor: Color = Color.black
//    @Published var onTimeColor: Color = Color.green
//    @Published var delayedColor: Color = Color.red
    @Published var cancelledColor: Color = Color("CDColor1")
    @Published var onTimeColor: Color = Color("OTColor1")
    @Published var delayedColor: Color = Color("DLColor1")

    let testColor = Color(#colorLiteral(red: 0, green: 0.1914038658, blue: 0.7577866912, alpha: 1))
}
