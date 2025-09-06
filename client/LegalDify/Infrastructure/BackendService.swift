import Foundation
import Combine

@MainActor
class BackendService: ObservableObject {
    @Published var isConnected = false
    @Published var isProcessing = false
    @Published var lastError: String?
    
    private let baseURL: URL
    private let session: URLSession
    private var cancellables = Set<AnyCancellable>()
    
    init(baseURL: String = "http://127.0.0.1:8000") {
        self.baseURL = URL(string: baseURL)!
        
        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = 30
        configuration.timeoutIntervalForResource = 300
        self.session = URLSession(configuration: configuration)
        
        checkConnection()
        startConnectionMonitoring()
    }
    
    private func startConnectionMonitoring() {
        Timer.publish(every: 5, on: .main, in: .common)
            .autoconnect()
            .sink { _ in
                Task {
                    await self.checkConnection()
                }
            }
            .store(in: &cancellables)
    }
    
    func checkConnection() {
        Task {
            do {
                let url = baseURL.appendingPathComponent("/api/v1/health")
                let (_, response) = try await session.data(from: url)
                
                if let httpResponse = response as? HTTPURLResponse,
                   httpResponse.statusCode == 200 {
                    self.isConnected = true
                    self.lastError = nil
                } else {
                    self.isConnected = false
                }
            } catch {
                self.isConnected = false
                self.lastError = error.localizedDescription
            }
        }
    }
    
    func uploadDocument(at fileURL: URL) async throws -> Document {
        let url = baseURL.appendingPathComponent("/api/v1/documents/upload")
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        let data = try Data(contentsOf: fileURL)
        let fileName = fileURL.lastPathComponent
        
        var body = Data()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(fileName)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: application/octet-stream\r\n\r\n".data(using: .utf8)!)
        body.append(data)
        body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)
        
        request.httpBody = body
        
        let (responseData, _) = try await session.data(for: request)
        
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode(Document.self, from: responseData)
    }
    
    func ingestDocument(path: String, parserPluginId: String? = nil) async throws -> Document {
        let url = baseURL.appendingPathComponent("/api/v1/documents/ingest")
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = [
            "file_path": path,
            "parser_plugin_id": parserPluginId as Any
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, _) = try await session.data(for: request)
        
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode(Document.self, from: data)
    }
    
    func queryDocuments(query: String, topK: Int = 5, documentIds: [UUID]? = nil) async throws -> QueryResult {
        let url = baseURL.appendingPathComponent("/api/v1/queries")
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        var body: [String: Any] = [
            "query": query,
            "top_k": topK
        ]
        
        if let documentIds = documentIds {
            body["document_ids"] = documentIds.map { $0.uuidString }
        }
        
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, _) = try await session.data(for: request)
        
        let decoder = JSONDecoder()
        return try decoder.decode(QueryResult.self, from: data)
    }
    
    func getAllDocuments() async throws -> [Document] {
        let url = baseURL.appendingPathComponent("/api/v1/documents")
        
        let (data, _) = try await session.data(from: url)
        
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        
        let response = try decoder.decode(DocumentListResponse.self, from: data)
        return response.documents
    }
    
    func deleteDocument(_ documentId: UUID) async throws {
        let url = baseURL.appendingPathComponent("/api/v1/documents/\(documentId)")
        
        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"
        
        let (_, _) = try await session.data(for: request)
    }
    
    func getAvailablePlugins() async throws -> [Plugin] {
        let url = baseURL.appendingPathComponent("/api/v1/plugins")
        
        let (data, _) = try await session.data(from: url)
        
        let response = try JSONDecoder().decode(PluginListResponse.self, from: data)
        return response.plugins
    }
    
    private struct DocumentListResponse: Codable {
        let documents: [Document]
        let total: Int
    }
    
    struct Plugin: Codable, Identifiable {
        let name: String
        let supportedFormats: [String]
        let loaded: Bool
        
        var id: String { name }
        
        enum CodingKeys: String, CodingKey {
            case name
            case supportedFormats = "supported_formats"
            case loaded
        }
    }
    
    private struct PluginListResponse: Codable {
        let plugins: [Plugin]
        let total: Int
        let supportedFormats: [String]
        
        enum CodingKeys: String, CodingKey {
            case plugins
            case total
            case supportedFormats = "supported_formats"
        }
    }
}