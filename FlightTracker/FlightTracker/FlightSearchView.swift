//
//  FlightViews.swift
//  FlightTracker
//
//  Created by Miha Strah on 14/07/2020.
//  Copyright © 2020 Miha Strah. All rights reserved.
//

import SwiftUI
import Combine


#if !APPCLIP
struct FlightSearchView: View {
    
    func search() {
        self.flightStatusObject.reset()
        self.flightStatusObject.savedFlight = SavedFlightDataModel(airlineid: self.searchAirline, flightnumber: self.searchFlight, date: self.date)
        self.flightStatusObject.getStatus(update: false)
        self.showFlightStatus = true
    }
    
    static let taskDateFormat: DateFormatter = {
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd' 'HH:mm"
        return dateFormatter
    }()
    
    @EnvironmentObject var userSavedFlights: UserSavedFlights
    @ObservedObject var flightStatusObject = FlightStatusObject()
    
    
    @Binding var currentTab: Tab
    
    
    
    @State public var searchAirline = ""
    @State public var searchFlight = ""
    @State public var date = Date()
    
    
    @State public var showFlightStatus = false
    
    
    @State public var imageHeightAnimation = false
    
    @State private var keyboardHeight: CGFloat = 0
    
    let rangeDate = (Date().addingTimeInterval(-15552000))...(Date().addingTimeInterval(518400))
    
    
    //@ObservedObject var urlImageModel: UrlImageModel
    
    var body: some View {
        GeometryReader { geometry in
            
            NavigationView {
                ScrollView(){
                    
                    VStack (spacing: 0){
                        ZStack(alignment: .top) {
                            //                                if (self.flightStatusObject.urlImageModel != nil) {
                            Image(uiImage: (self.flightStatusObject.urlImageModel?.image) ?? UIImage(imageLiteralResourceName: "airplane_stock"))
                                .resizable()
                        }
                        .scaledToFill()
                        
                        .aspectRatio(contentMode: .fill)
                        .frame(maxWidth: geometry.size.width, maxHeight: ((self.imageHeightAnimation) || (self.keyboardHeight>0)) ? withAnimation(.linear(duration: 2)) {geometry.size.height * 0.2} : (geometry.size.height * 0.4))
//                        .frame(maxWidth: geometry.size.width, maxHeight: ((self.imageHeightAnimation) || (self.keyboardHeight>0)) ? min((geometry.size.height * 0.2),(geometry.size.height - keyboardHeight)) : (geometry.size.height * 0.4))
                        .onReceive(Publishers.keyboardHeight) {
                            self.keyboardHeight = $0
                        }
                        .clipped()
                        //                        .animation(.spring())
                        //.animation(.easeInOut(duration: 2))
                        //                        .animation(.easeInOut)
                        
                        //                                    .frame(width: geometry.size.width, height: (imageHeightAnimation) ? geometry.size.height * 0.2 : geometry.size.height * 0.4)
                        //                                    .frame(width: geometry.size.width, height: (geometry.size.height * 0.2))
                        //                                        .frame(maxWidth: geometry.size.width, maxHeight: ((imageHeightAnimation) || (keyboardHeight>0))  || (imageHeightAnimation)  ? geometry.size.height * 0.2 : (geometry.size.height * 0.4))
                        //                                    .frame(maxWidth: 500, maxHeight: ((imageHeightAnimation && self.flightStatusObject.searchEnded) || (keyboardHeight>0))  || (imageHeightAnimation)  ? 1000 * 0.2 : (1000 * 0.4))
                        //                                    .transition(.identity)
                        //                                    .animation(.spring())
                        //                                        .clipped()
                        //                                        .onReceive(Publishers.keyboardHeight) { self.keyboardHeight = $0 }
                        .gesture(
                            TapGesture()
                                .onEnded { _ in
                                    withAnimation(.linear) {
                                        self.imageHeightAnimation.toggle()
                                    }
                                    
                                }
                        )
                        
                        
                        VStack(spacing: 0) {
                            
                            ZStack(){
                                VStack(spacing: 15) {
                                    
                                    VStack(spacing: 15) {
                                        
                                        HStack() {
                                            Text("Flight:")
                                                .font(.headline)
                                            TextField("Airline", text: self.$searchAirline)
                                                .font(.body)
                                                .onReceive(Just(self.searchAirline)) { newValue in
                                                    let filtered = newValue.uppercased()
                                                    if filtered != newValue {
                                                        self.searchAirline = filtered
                                                    }
                                                }
                                            TextField("Flight Number", text: self.$searchFlight)
                                                .font(.body)
                                                .keyboardType(.numberPad)
                                                .onReceive(Just(self.searchFlight)) { newValue in
                                                    let filtered = newValue.filter { "0123456789".contains($0) }
                                                    if filtered != newValue {
                                                        self.searchFlight = filtered
                                                    }
                                                }
                                            Spacer()
                                        }
                                        
                                        
                                        if #available(iOS 14.0, *) {
                                            HStack() {
                                            DatePicker(selection: self.$date, in: rangeDate, displayedComponents: .date, label: { Text("Date:").font(.headline)})
                                                .frame(height: 80)
                                                .environment(\.timeZone, TimeZone.current)
                                                
                                                Spacer()
                                            }
                                            
                                            //                                        .clipped()
                                        }
                                        else {
                                            HStack() {
                                                Spacer()
                                                DatePicker("", selection: self.$date, in: self.rangeDate, displayedComponents: .date)
                                                    .frame(height: 80)
                                                    .clipped()
                                                    .environment(\.timeZone, TimeZone.current)
                                                Spacer()
                                            }
                                            .frame(height: 90)
                                            
                                        }
                                        
                                        
                                    }
                                    
                                    HStack(alignment: .center) {
                                        
                                        Spacer()
                                        
                                        Button(action: {
                                            UIApplication.shared.sendAction(#selector(UIResponder.resignFirstResponder), to: nil, from: nil, for: nil)
                                            
                                            self.search()
                                            
                                            
                                        })
                                        {
                                            Text("Search")
                                                .frame(width: 100)
                                                .padding()
                                                .background(Color("ColorButton1"))
                                                .cornerRadius(10)
                                        }.disabled(self.flightStatusObject.searchInProgress)
                                        
                                        Spacer()
                                        
                                        
                                        Button(action: {
                                            
                                            withAnimation(.linear) {
                                            imageHeightAnimation = true
                                            }
                                            self.showFlightStatus = false
                                            self.userSavedFlights.add(flightStatusObject: self.flightStatusObject)
                                            
                                            
                                            self.searchAirline = ""
                                            self.searchFlight = ""
                                            self.currentTab = .savedFlights
                                            
                                            
                                        })
                                        {
                                            Text("Add")
                                                .frame(width: 100)
                                                .foregroundColor((self.flightStatusObject.searchEnded && self.flightStatusObject.searchOK) ? .green : .gray)
                                                .padding()
                                                .background(Color("ColorButton1"))
                                                .cornerRadius(10)
                                            
                                        }
                                        .disabled(!(self.flightStatusObject.searchEnded && self.flightStatusObject.searchOK))
                                        //.padding(.bottom, max(15,keyboardHeight))
                                        
                                        Spacer()
                                        
                                        
                                    }
                                }
                                .padding(.horizontal, 10)
                                .padding(.top, 15)
                                .padding(.bottom, 10)
                            }
                            .background(Color("ColorGray2"))
                            //                                .animation(.spring())
                            
                            
                            if (self.flightStatusObject.searchEnded) {
                                VStack(){
                                    ExistingFlightInfoView(flightStatusObject: self.flightStatusObject)
                                        //.shadow(color: Color(.red), radius: 35, x: 0, y: 0)
                                        .padding(.horizontal, 10)
                                        .padding(.top, 10)
                                        .padding(.bottom, 20)
                                        
                                        .onAppear(){
                                            withAnimation(.linear) {
                                            imageHeightAnimation = true
                                            }
                                        }
                                    //                                        .transition(.asymmetric(insertion: .move(edge: .leading), removal: .scale(scale: 10)))
                                    //                                        .animation(.default)
                                }
                                //                                    .animation(.linear(duration: 5))
                                
                            }
                            
                            if flightStatusObject.searchInProgress {
                                if #available(iOS 14.0, *) {
                                    IndicatorSearch()
                                        .frame(width: 100)
                                        .padding(.top, 25)
                                    //                                                .animation(.linear)
                                    
                                    //                                                                       .animation(.easeInOut)
                                } else {
                                    //                                             Fallback on earlier versions
                                    Text("Searching ...")
                                        .frame(width: 100)
                                        .padding(.top, 25)
                                    //                                                .animation(.linear)
                                    //                                                .animation(.easeInOut)
                                }
                                //                                    }
                                
                                
                            }
                            //                            .animation(.spring())
                            
                        }
                        
                        
                        
                        
                    }
                }
                
                .background(Color("ColorGray1"))
                .navigationBarTitle("Search", displayMode: .automatic)
            }
            .navigationViewStyle(StackNavigationViewStyle())
            
            
        }
    }
}

#else
struct FlightSearchView: View {
    
    func search() {
        self.flightStatusObject.reset()
        self.flightStatusObject.savedFlight = SavedFlightDataModel(airlineid: self.searchAirline, flightnumber: self.searchFlight, date: self.date)
        self.flightStatusObject.getStatus(update: false)
        self.showFlightStatus = true
    }
    
    static let taskDateFormat: DateFormatter = {
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd' 'HH:mm"
        return dateFormatter
    }()
    
    @ObservedObject var flightStatusObject = FlightStatusObject()
    
    @State public var searchAirline = ""
    @State public var searchFlight = ""
    @State public var date = Date()
    
    
    @State public var showFlightStatus = false
    
    
    @State public var imageHeightAnimation = false
    
    @State private var keyboardHeight: CGFloat = 0
    
    let rangeDate = (Date().addingTimeInterval(-15552000))...(Date().addingTimeInterval(518400))
    
    
    //@ObservedObject var urlImageModel: UrlImageModel
    
    var body: some View {
        GeometryReader { geometry in
            
            NavigationView {
                ScrollView(){
                    
                    VStack (spacing: 0){
                        ZStack(alignment: .top) {
                            //                                if (self.flightStatusObject.urlImageModel != nil) {
                            Image(uiImage: (self.flightStatusObject.urlImageModel?.image) ?? UIImage(imageLiteralResourceName: "airplane_stock"))
                                .resizable()
                        }
                        .scaledToFill()
                        
                        .aspectRatio(contentMode: .fill)
                        .frame(maxWidth: geometry.size.width, maxHeight: ((self.imageHeightAnimation) || (self.keyboardHeight>0)) ? withAnimation(.linear(duration: 2)) {geometry.size.height * 0.2} : (geometry.size.height * 0.4))
                        .onReceive(Publishers.keyboardHeight) { self.keyboardHeight = $0 }
                        .clipped()

                        .gesture(
                            TapGesture()
                                .onEnded { _ in
                                    withAnimation(.linear) {
                                        self.imageHeightAnimation.toggle()
                                    }
                                    
                                }
                        )
                        
                        
                        VStack(spacing: 0) {
                            
                            ZStack(){
                                VStack(spacing: 15) {
                                    
                                    VStack(spacing: 15) {
                                        
                                        HStack() {
                                            Text("Flight:")
                                                .font(.headline)
                                            TextField("Airline", text: self.$searchAirline)
                                                .font(.body)
                                                .onReceive(Just(self.searchAirline)) { newValue in
                                                    let filtered = newValue.uppercased()
                                                    if filtered != newValue {
                                                        self.searchAirline = filtered
                                                    }
                                                }
                                            TextField("Flight Number", text: self.$searchFlight)
                                                .font(.body)
                                                .keyboardType(.numberPad)
                                                .onReceive(Just(self.searchFlight)) { newValue in
                                                    let filtered = newValue.filter { "0123456789".contains($0) }
                                                    if filtered != newValue {
                                                        self.searchFlight = filtered
                                                    }
                                                }
                                            Spacer()
                                        }
                                        
                                        HStack() {
                                        
                                        HStack() {
                                            DatePicker(selection: self.$date, in: rangeDate, displayedComponents: .date, label: { Text("Date:").font(.headline)})
                                                .frame(height: 80)
                                                .environment(\.timeZone, TimeZone.current)
                                                .padding(.trailing, 35)
                                                
                                                
                                            }
                                            
                                            //                                        .clipped()
                                        .frame(height: 90)
                                        
                                            HStack() {
                                            Button(action: {
                                                UIApplication.shared.sendAction(#selector(UIResponder.resignFirstResponder), to: nil, from: nil, for: nil)
                                                
                                                self.search()
                                                
                                                
                                            })
                                            {
                                                Text("Search")
                                                    .frame(width: 100)
                                                    .padding()
                                                    .background(Color("ColorButton1"))
                                                    .cornerRadius(10)
                                            }.disabled(self.flightStatusObject.searchInProgress)
                                            }.frame(width: geometry.size.width - 230, alignment: .center)
                                            
                                        
                                        }
                                        
                                    }
                                    
                                   
                                }
                                .padding(.horizontal, 10)
                                .padding(.top, 15)
                                .padding(.bottom, 0)
                            }
                            .background(Color("ColorGray2"))
                            //                                .animation(.spring())
                            
                            
                            if (self.flightStatusObject.searchEnded) {
                                VStack(){
                                    ExistingFlightInfoView(flightStatusObject: self.flightStatusObject)
                                        //.shadow(color: Color(.red), radius: 35, x: 0, y: 0)
                                        .padding(.horizontal, 10)
                                        .padding(.top, 10)
                                        .padding(.bottom, 20)
                                        
                                        .onAppear(){
                                            imageHeightAnimation = true
                                        }
                                    //                                        .transition(.asymmetric(insertion: .move(edge: .leading), removal: .scale(scale: 10)))
                                    //                                        .animation(.default)
                                }
                                //                                    .animation(.linear(duration: 5))
                                
                            }
                            
                            if flightStatusObject.searchInProgress {
                                if #available(iOS 14.0, *) {
                                    IndicatorSearch()
                                        .frame(width: 100)
                                        .padding(.top, 25)
                                } else {
                                    // Fallback on earlier versions
                                }
                                    //                                                .animation(.linear)
                                    
                                    //                                                                       .animation(.easeInOut)
                                
                                //                                    }
                                
                                
                            }
                            //                            .animation(.spring())
                            
                        }
                        
                        
                        
                        
                    }
                }
                
                .background(Color("ColorGray1"))
                .edgesIgnoringSafeArea(.bottom)
                .navigationBarTitle("Flight Status", displayMode: .automatic)
            }
            
            
            .navigationViewStyle(StackNavigationViewStyle())
            
            
        }
    }
}
#endif




































extension Publishers {
    static var keyboardHeight: AnyPublisher<CGFloat, Never> {
        let willShow = NotificationCenter.default.publisher(for: UIApplication.keyboardWillShowNotification)
            .map { $0.keyboardHeight }
        
        let willHide = NotificationCenter.default.publisher(for: UIApplication.keyboardWillHideNotification)
            .map { _ in CGFloat(0) }
        
        return MergeMany(willShow, willHide)
            .eraseToAnyPublisher()
    }
}
extension Notification {
    var keyboardHeight: CGFloat {
        return (userInfo?[UIResponder.keyboardFrameEndUserInfoKey] as? CGRect)?.height ?? 0
    }
}


//Searching indicator
@available(iOS 14.0, *)
struct IndicatorSearch: View {
    var body: some View {
        ProgressView()
    }
}




// NAVIGATION BAR COLOR ->

//WORKING IN iOS 13
extension UINavigationController {
    override open func viewDidLoad() {
        super.viewDidLoad()
        
        let standard = UINavigationBarAppearance()
        standard.configureWithDefaultBackground()
        //        standard.backgroundColor = UIColor(named: "ColorGray1")
        standard.shadowColor = .clear
        
        
        
        let compact = UINavigationBarAppearance()
        //        compact.configureWithTransparentBackground()
        compact.backgroundColor = UIColor(named: "ColorGray1")
        compact.shadowColor = .clear
        
        
        let scrollEdge = UINavigationBarAppearance()
        //        scrollEdge.configureWithTransparentBackground()
        scrollEdge.backgroundColor = UIColor(named: "ColorGray1")
        scrollEdge.shadowColor = .clear
        
        
        navigationBar.standardAppearance = standard
        //    navigationBar.compactAppearance = compact
        navigationBar.scrollEdgeAppearance = scrollEdge
    }
}



struct NavigationConfigurator: UIViewControllerRepresentable {
    var configure: (UINavigationController) -> Void = { _ in }
    
    func makeUIViewController(context: UIViewControllerRepresentableContext<NavigationConfigurator>) -> UIViewController {
        UIViewController()
    }
    func updateUIViewController(_ uiViewController: UIViewController, context: UIViewControllerRepresentableContext<NavigationConfigurator>) {
        if let nc = uiViewController.navigationController {
            self.configure(nc)
        }
    }
    
}




//FOR iOS 14 (bug in ios 13.5) (for dynamic color)
//struct NavigationBarModifier: ViewModifier {
//
//    var backgroundColor: UIColor?
//
//    init( backgroundColor: UIColor?) {
//        self.backgroundColor = backgroundColor
//        let coloredAppearance = UINavigationBarAppearance()
//        coloredAppearance.configureWithTransparentBackground()
//        coloredAppearance.backgroundColor = .clear
//        coloredAppearance.titleTextAttributes = [.foregroundColor: UIColor.white]
//        coloredAppearance.largeTitleTextAttributes = [.foregroundColor: UIColor.white]
//
//        UINavigationBar.appearance().standardAppearance = coloredAppearance
//        UINavigationBar.appearance().compactAppearance = coloredAppearance
//        UINavigationBar.appearance().scrollEdgeAppearance = coloredAppearance
//        UINavigationBar.appearance().tintColor = .white
//
//    }
//    func body(content: Content) -> some View {
//            ZStack{
//                content
//                VStack {
//                    GeometryReader { geometry in
//                        Color(self.backgroundColor ?? .clear)
//                            .frame(height: geometry.safeAreaInsets.top)
//                            .edgesIgnoringSafeArea(.top)
//                        Spacer()
//                    }
//                }
//            }
//        }
//}
//
//extension View {
//
//    func navigationBarColor(_ backgroundColor: UIColor?) -> some View {
//        self.modifier(NavigationBarModifier(backgroundColor: backgroundColor))
//    }
//
//}

// <- NAVIGATION BAR COLOR
