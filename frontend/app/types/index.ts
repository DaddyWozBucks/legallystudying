export interface Document {
  id: string;
  name: string;
  path: string;
  content_hash: string;
  file_type: string;
  size_bytes: number;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  parser_plugin_id?: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, any>;
  raw_text?: string;
  summary?: string;
  key_points?: string[];
}

export interface DocumentSummary {
  document_id: string;
  summary: string;
  key_points: string[];
  generated_at: string;
}

export interface SearchResult {
  content: string;
  document_name: string;
  chunk_index: number;
  relevance_score: number;
}

export interface QueryResponse {
  query: string;
  answer: string;
  sources: SearchResult[];
  confidence_score: number;
}

export interface Flashcard {
  id: string;
  document_id: string;
  question: string;
  answer: string;
  difficulty: 'easy' | 'medium' | 'hard';
  created_at: string;
}

export interface HealthCheck {
  status: string;
  timestamp: string;
  services: {
    embedding_service: string;
    llm_service: string;
    parser_service: string;
    vector_database: {
      status: string;
      total_chunks: number;
    };
  };
}