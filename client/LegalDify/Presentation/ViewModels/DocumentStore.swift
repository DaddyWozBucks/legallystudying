import Foundation
import Combine

@MainActor
class DocumentStore: ObservableObject {
    @Published var documents: [Document] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private var backendService: BackendService?
    private var refreshTimer: Timer?
    
    func setBackendService(_ service: BackendService) {
        self.backendService = service
        Task {
            await loadDocuments()
        }
        startAutoRefresh()
    }
    
    private func startAutoRefresh() {
        refreshTimer = Timer.scheduledTimer(withTimeInterval: 10, repeats: true) { _ in
            Task { @MainActor in
                await self.loadDocuments()
            }
        }
    }
    
    func loadDocuments() async {
        guard let service = backendService else { return }
        
        isLoading = true
        errorMessage = nil
        
        do {
            documents = try await service.getAllDocuments()
                .sorted { $0.updatedAt > $1.updatedAt }
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
    
    func importDocument(at url: URL) async throws {
        guard let service = backendService else {
            throw DocumentError.backendNotConnected
        }
        
        let document = try await service.uploadDocument(at: url)
        documents.insert(document, at: 0)
    }
    
    func deleteDocument(_ document: Document) async throws {
        guard let service = backendService else {
            throw DocumentError.backendNotConnected
        }
        
        try await service.deleteDocument(document.id)
        documents.removeAll { $0.id == document.id }
    }
    
    func processAllPending() async {
        let pendingDocuments = documents.filter { $0.processingStatus == .pending }
        
        for document in pendingDocuments {
            // Implementation would trigger reprocessing
            // This is a placeholder for the actual implementation
        }
    }
    
    enum DocumentError: LocalizedError {
        case backendNotConnected
        
        var errorDescription: String? {
            switch self {
            case .backendNotConnected:
                return "Backend service is not connected"
            }
        }
    }
    
    deinit {
        refreshTimer?.invalidate()
    }
}