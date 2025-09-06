import SwiftUI

@main
struct LegalDifyApp: App {
    @StateObject private var appCoordinator = AppCoordinator()
    @StateObject private var documentStore = DocumentStore()
    @StateObject private var backendService = BackendService()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appCoordinator)
                .environmentObject(documentStore)
                .environmentObject(backendService)
                .frame(minWidth: 1000, minHeight: 700)
        }
        .commands {
            CommandGroup(replacing: .newItem) {
                Button("Import Document...") {
                    appCoordinator.showDocumentImporter()
                }
                .keyboardShortcut("o", modifiers: [.command])
            }
            
            CommandMenu("Documents") {
                Button("Search Documents...") {
                    appCoordinator.showSearch()
                }
                .keyboardShortcut("f", modifiers: [.command])
                
                Divider()
                
                Button("Process All Pending") {
                    Task {
                        await documentStore.processAllPending()
                    }
                }
            }
        }
        
        Settings {
            SettingsView()
                .environmentObject(backendService)
        }
    }
}