import Foundation
import SwiftUI

@MainActor
class AppCoordinator: ObservableObject {
    @Published var isShowingSearch = false
    @Published var isShowingImporter = false
    @Published var isShowingSettings = false
    @Published var selectedTab: Tab = .documents
    
    enum Tab {
        case documents
        case search
        case settings
    }
    
    func showDocumentImporter() {
        isShowingImporter = true
    }
    
    func hideDocumentImporter() {
        isShowingImporter = false
    }
    
    func showSearch() {
        isShowingSearch = true
    }
    
    func hideSearch() {
        isShowingSearch = false
    }
    
    func showSettings() {
        isShowingSettings = true
    }
    
    func hideSettings() {
        isShowingSettings = false
    }
    
    func navigateToDocument(_ document: Document) {
        selectedTab = .documents
        // Additional navigation logic here
    }
}