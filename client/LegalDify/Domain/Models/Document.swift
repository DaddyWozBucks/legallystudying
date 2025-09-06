import Foundation

struct Document: Identifiable, Codable, Hashable {
    let id: UUID
    let name: String
    let path: String
    let fileType: String
    let sizeBytes: Int
    let processingStatus: ProcessingStatus
    let parserPluginId: String?
    let errorMessage: String?
    let createdAt: Date
    let updatedAt: Date
    let metadata: [String: String]
    
    enum ProcessingStatus: String, Codable {
        case pending
        case processing
        case completed
        case failed
        
        var displayName: String {
            switch self {
            case .pending: return "Pending"
            case .processing: return "Processing..."
            case .completed: return "Ready"
            case .failed: return "Failed"
            }
        }
        
        var symbolName: String {
            switch self {
            case .pending: return "clock"
            case .processing: return "arrow.triangle.2.circlepath"
            case .completed: return "checkmark.circle.fill"
            case .failed: return "exclamationmark.triangle.fill"
            }
        }
    }
    
    var formattedSize: String {
        let formatter = ByteCountFormatter()
        formatter.countStyle = .file
        return formatter.string(fromByteCount: Int64(sizeBytes))
    }
    
    var fileExtension: String {
        (path as NSString).pathExtension.lowercased()
    }
}

struct QueryResult: Codable {
    let answer: String
    let sources: [Source]
    let query: String
    let processingTimeMs: Double
    
    struct Source: Codable, Identifiable {
        let documentId: UUID
        let documentName: String
        let pageNumber: Int?
        let relevanceScore: Double
        let excerpt: String?
        
        var id: UUID { documentId }
        
        enum CodingKeys: String, CodingKey {
            case documentId = "document_id"
            case documentName = "document_name"
            case pageNumber = "page_number"
            case relevanceScore = "relevance_score"
            case excerpt
        }
    }
    
    enum CodingKeys: String, CodingKey {
        case answer
        case sources
        case query
        case processingTimeMs = "processing_time_ms"
    }
}