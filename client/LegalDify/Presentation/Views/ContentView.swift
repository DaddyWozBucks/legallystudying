import SwiftUI

struct ContentView: View {
    @EnvironmentObject var documentStore: DocumentStore
    @EnvironmentObject var backendService: BackendService
    @EnvironmentObject var appCoordinator: AppCoordinator
    
    @State private var selectedDocument: Document?
    @State private var searchQuery = ""
    @State private var isShowingImporter = false
    
    var body: some View {
        NavigationSplitView {
            DocumentListView(selectedDocument: $selectedDocument)
                .navigationSplitViewColumnWidth(min: 250, ideal: 300, max: 400)
        } detail: {
            if let document = selectedDocument {
                DocumentDetailView(document: document)
            } else if documentStore.documents.isEmpty {
                EmptyStateView()
            } else {
                Text("Select a document")
                    .font(.largeTitle)
                    .foregroundColor(.secondary)
            }
        }
        .toolbar {
            ToolbarItemGroup(placement: .navigation) {
                Button(action: { appCoordinator.showDocumentImporter() }) {
                    Label("Import", systemImage: "plus.circle")
                }
                
                if !documentStore.documents.isEmpty {
                    Button(action: { appCoordinator.showSearch() }) {
                        Label("Search", systemImage: "magnifyingglass")
                    }
                }
            }
            
            ToolbarItem(placement: .status) {
                ConnectionStatusView()
            }
        }
        .searchable(text: $searchQuery, prompt: "Search documents...")
        .sheet(isPresented: $appCoordinator.isShowingSearch) {
            SearchView()
        }
        .sheet(isPresented: $appCoordinator.isShowingImporter) {
            DocumentImporterView()
        }
    }
}

struct EmptyStateView: View {
    @EnvironmentObject var appCoordinator: AppCoordinator
    
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "doc.text.magnifyingglass")
                .font(.system(size: 72))
                .foregroundColor(.secondary)
            
            Text("No Documents Yet")
                .font(.largeTitle)
                .fontWeight(.semibold)
            
            Text("Import documents to get started with AI-powered search")
                .font(.body)
                .foregroundColor(.secondary)
            
            Button(action: { appCoordinator.showDocumentImporter() }) {
                Label("Import Document", systemImage: "plus.circle.fill")
                    .font(.headline)
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}