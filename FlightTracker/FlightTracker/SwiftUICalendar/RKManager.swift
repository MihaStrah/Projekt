//
//  RKManager.swift
//  RKCalendar
//
//  Created by Raffi Kian on 7/14/19.
//  Copyright © 2019 Raffi Kian. All rights reserved.
//


//MIT License code : https://github.com/RaffiKian/RKCalendar/

import SwiftUI

class RKManager : ObservableObject {

    @Published var calendar = Calendar.current
    @Published var minimumDate: Date = Date()
    @Published var maximumDate: Date = Date()
    @Published var disabledDates: [Date] = [Date]()
    @Published var selectedDates: [Date] = [Date]()
    @Published var selectedDate: Date! = nil
    @Published var startDate: Date! = nil
    @Published var endDate: Date! = nil
    
    @Published var cancelledDates: [Date] = [Date]()
    @Published var onTimeDates: [Date] = [Date]()
    @Published var delayedDates: [Date] = [Date]()
    
    
    @Published var mode: Int = 0
    
    var colors = RKColorSettings()
  
    init(calendar: Calendar, minimumDate: Date, maximumDate: Date, selectedDates: [Date] = [Date](), mode: Int, cancelledDates: [Date], onTimeDates: [Date], delayedDates: [Date]) {
        self.calendar = calendar
        self.minimumDate = minimumDate
        self.maximumDate = maximumDate
        self.selectedDates = selectedDates
        self.mode = mode
        
        self.cancelledDates = cancelledDates
        self.onTimeDates = onTimeDates
        self.delayedDates = delayedDates
    }
    
    func selectedDatesContains(date: Date) -> Bool {
        if let _ = self.selectedDates.first(where: { calendar.isDate($0, inSameDayAs: date) }) {
            return true
        }
        return false
    }
    
    func selectedDatesFindIndex(date: Date) -> Int? {
        return self.selectedDates.firstIndex(where: { calendar.isDate($0, inSameDayAs: date) })
    }
    
    func disabledDatesContains(date: Date) -> Bool {
        if let _ = self.disabledDates.first(where: { calendar.isDate($0, inSameDayAs: date) }) {
            return true
        }
        return false
    }
    
    func disabledDatesFindIndex(date: Date) -> Int? {
        return self.disabledDates.firstIndex(where: { calendar.isDate($0, inSameDayAs: date) })
    }
    
    
    
    
    
    
    func CancelledDatesContains(date: Date) -> Bool {
        if let _ = self.cancelledDates.first(where: { calendar.isDate($0, inSameDayAs: date) }) {
            return true
        }
        return false
    }
    func OnTimeDatesContains(date: Date) -> Bool {
        if let _ = self.onTimeDates.first(where: { calendar.isDate($0, inSameDayAs: date) }) {
            return true
        }
        return false
    }
    func DelayedDatesContains(date: Date) -> Bool {
        if let _ = self.delayedDates.first(where: { calendar.isDate($0, inSameDayAs: date) }) {
            return true
        }
        return false
    }

    
}
