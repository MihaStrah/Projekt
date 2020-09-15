//
//  MainView.swift
//  FlightTracker
//
//  Created by Miha Strah on 24/07/2020.
//  Copyright © 2020 Miha Strah. All rights reserved.
//

import SwiftUI
import MapKit


enum Tab {
    case savedFlights, searchFlight
}





struct MainView: View {
    
    
    
    
    
    //    init() {
    //
    //
    // To remove only extra separators below the list:
    //                    UITableView.appearance().tableFooterView = UIView()
    //
    // To remove all separators including the actual ones:
    //                UITableView.appearance().separatorStyle = .none
    
    //            UITableView.appearance().backgroundColor = UIColor.init(named: "ColorGray1")
    //
    //            UITableViewCell.appearance().backgroundColor = .clear
    //            UITableViewCell.appearance().selectionStyle = .none
    
    //            UIScrollView.appearance().backgroundColor = UIColor.init(named: "ColorGray1")
    
    //            UINavigationBar.appearance().shadowImage = UIImage()
    
    //            let appearance = UINavigationBarAppearance()
    //            appearance.shadowImage = nil
    //            appearance.shadowColor = nil
    //            UINavigationBar.appearance().standardAppearance = appearance
    //            UINavigationBar.appearance().compactAppearance = appearance
    
    //            let navigationBarAppearence = UINavigationBarAppearance()
    //            navigationBarAppearence.shadowColor = .clear
    //            UINavigationBar.appearance().scrollEdgeAppearance = navigationBarAppearence
    
    //            appearance.configureWithOpaqueBackground()
    //            appearance.configureWithDefaultBackground()
    //            appearance.backgroundColor = .yellow
    //            appearance.configureWithOpaqueBackground()
    //                appearance.shadowColor = .clear
    //                UINavigationBar.appearance().standardAppearance = appearance
    //                UINavigationBar.appearance().scrollEdgeAppearance = appearance
    //            UINavigationBar.appearance().compactAppearance = appearance
    //
    //    }
    
    
    
    
    
    
    init(currentTab: Binding<Tab>) {

        
        if #available(iOS 14.0, *) {
            
            // iOS 14 doesn't have extra separators below the list by default.
        } else {
            // To remove only extra separators below the list:
            UITableView.appearance().tableFooterView = UIView()
        }
        //            UITableView.appearance().separatorStyle = .none
        
        
        //                      UITableViewCell.appearance().backgroundColor = UIColor(named: "ColorGray1")
        //        UITableView.appearance().backgroundColor = .red
        
        
        
        //        UITableView.appearance().backgroundColor = .clear // For tableView
        //                UITableViewCell.appearance().backgroundColor = .clear
        
        
        
        
        //        UITableView.appearance().backgroundColor = .green
        //         UITableViewCell.appearance().backgroundColor = UIColor.init(named: "ColorGray1")
        
        
        UITableView.appearance().backgroundColor = UIColor(named: "ColorGray1")
        UITableViewCell.appearance().backgroundColor = .clear
        
        
        
        //        UIScrollView.appearance().backgroundColor = UIColor(named: "ColorGray1")
        
        self._currentTab = currentTab
        
        
    }
    
    @EnvironmentObject var userSavedFlights: UserSavedFlights
    
    @Binding var currentTab: Tab
    
//    @State private var editMode = EditMode.inactive
    
//    @State private var showingAlert = false
    
//    @State public var showingNewFlightView = false
    
    
    
    var body: some View {
        
        GeometryReader { geometry in
            
            TabView(selection: self.$currentTab){
                
                
                SavedFlightsView()
                    .tabItem{
                        VStack() {
                            Image(systemName: "airplane")
                            Text("Saved Flights")
                        }
                        
                    }
                    .tag(Tab.savedFlights)
                //
                
                FlightSearchView(currentTab: self.$currentTab)
                    .tabItem{
                        VStack() {
                            Image(systemName: "magnifyingglass")
                            Text("Search Flights")
                        }
                    }
                    .tag(Tab.searchFlight)
                
                
                
                
                
            }
            
            
            
            
        }
        
        
        
    }
}







extension View {
    func endEditing(_ force: Bool) {
        UIApplication.shared.windows.forEach { $0.endEditing(force)}
    }
}

struct SavedFlightsView: View {
    
    
    
    
//    @State var showingFlightView = false
    
    @State private var editMode = EditMode.inactive
    @State private var showingAlert = false
//    @State public var showingNewFlightView = false
    
    
    @EnvironmentObject var userSavedFlights: UserSavedFlights
    
    
    
    var body: some View {
        NavigationView {
            VStack() {
                List { // List works because it conforms to View
                    
                    ForEach((self.userSavedFlights.userSavedFlightStatusObjects)){flightStatusObject in
                        
                        ZStack() {
                            NavigationLink(destination: ExistingFlightView(flightStatusObject: flightStatusObject), tag: flightStatusObject.id, selection: self.$userSavedFlights.selectedItem) {
                                EmptyView()
                                
                                
                            }
                            
                            FlightCard(flightStatusObject: flightStatusObject)
                                .buttonStyle(PlainButtonStyle())
                                .listRowInsets(EdgeInsets.init(top: 0, leading: 0, bottom: 0, trailing: 0))
                            
                            
                        }
                        //                        .listRowInsets(EdgeInsets())
                        
                        .listRowBackground(Color("ColorGray1"))
                        
                        
                    }
                    .onDelete(perform: onDelete)
                    .onMove(perform: onMove)
                    
                    
                }
                //                .listStyle(GroupedListStyle())
                //                .listStyle(InsetGroupedListStyle())
                
                //                .environment(\.horizontalSizeClass, .regular)
                
                
            }
            
            .navigationBarTitle("Saved Flights", displayMode: .automatic)
            .navigationBarItems(
                leading:
                    EditButton()
                ,
                trailing:
                    HStack() {
                        if editMode.isEditing {
                            Button(action: {
                                self.showingAlert = true
                            }) {
                                Image(systemName: "trash").imageScale(.large).foregroundColor(.red)
                                    .padding()
                            }
                            .alert(isPresented: $showingAlert) {
                                Alert(title: Text("Remove all flights?"), primaryButton: .destructive(Text("Remove")) {
                                    self.userSavedFlights.reset()
                                    self.userSavedFlights.save()
                                    self.editMode = .inactive
                                }, secondaryButton: .cancel())}
                        }
                        
                    }
            )
            .environment(\.editMode, $editMode)
        }
        .navigationViewStyle(StackNavigationViewStyle())
        
        
    }
    
    
    
    
    private func onDelete(offsets: IndexSet) {
        self.userSavedFlights.removeOnIndexSet(atOffsets: offsets)
    }
    
    private func onMove(source: IndexSet, destination: Int) {
        self.userSavedFlights.userSavedFlightStatusObjects.move(fromOffsets: source, toOffset: destination)
        self.userSavedFlights.save()
        
    }
}



