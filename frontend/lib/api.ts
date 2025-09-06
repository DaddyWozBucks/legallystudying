const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Document {
  id: string;
  name: string;
  file_type: string;
  size_bytes: number;
  processing_status: string;
  created_at: string;
  updated_at: string;
  content_hash?: string;
  parser_plugin_id?: string;
  error_message?: string;
}

export interface DocumentSummary {
  document_id: string;
  summary: string;
  key_points: string[];
  generated_at: string;
}

export interface QuestionAnswer {
  question: string;
  answer: string;
  sources: string[];
  confidence: number;
}

export interface Prompt {
  id: string;
  name: string;
  template: string;
  description?: string;
  category?: string;
  variables?: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  private async fetchApi(endpoint: string, options: RequestInit = {}) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `API Error: ${response.status}`);
    }

    return response.json();
  }

  // Document endpoints
  async uploadDocument(file: File, parserPluginId?: string): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    if (parserPluginId) {
      formData.append('parser_plugin_id', parserPluginId);
    }

    return this.fetchApi('/api/v1/documents/upload', {
      method: 'POST',
      body: formData,
    });
  }

  async getDocuments(): Promise<{ documents: Document[]; total: number }> {
    return this.fetchApi('/api/v1/documents/');
  }

  async getDocument(id: string): Promise<Document> {
    return this.fetchApi(`/api/v1/documents/${id}`);
  }

  async deleteDocument(id: string): Promise<void> {
    return this.fetchApi(`/api/v1/documents/${id}`, {
      method: 'DELETE',
    });
  }

  async summarizeDocument(id: string): Promise<DocumentSummary> {
    return this.fetchApi(`/api/v1/documents/${id}/summarize`, {
      method: 'POST',
    });
  }

  async askQuestion(documentId: string, question: string): Promise<QuestionAnswer> {
    return this.fetchApi(`/api/v1/documents/${documentId}/qa`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question }),
    });
  }

  // Query endpoints
  async searchDocuments(query: string, documentIds?: string[]): Promise<any> {
    return this.fetchApi('/api/v1/queries/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        document_ids: documentIds,
        top_k: 10,
      }),
    });
  }

  // Prompt endpoints
  async getPrompts(): Promise<Prompt[]> {
    return this.fetchApi('/api/v1/prompts/');
  }

  async getPrompt(id: string): Promise<Prompt> {
    return this.fetchApi(`/api/v1/prompts/${id}`);
  }

  async createPrompt(prompt: Omit<Prompt, 'id' | 'created_at' | 'updated_at'>): Promise<Prompt> {
    return this.fetchApi('/api/v1/prompts/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(prompt),
    });
  }

  async updatePrompt(id: string, prompt: Partial<Prompt>): Promise<Prompt> {
    return this.fetchApi(`/api/v1/prompts/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(prompt),
    });
  }

  async deletePrompt(id: string): Promise<void> {
    return this.fetchApi(`/api/v1/prompts/${id}`, {
      method: 'DELETE',
    });
  }

  async testPrompt(promptId: string, variables: Record<string, string>): Promise<{ result: string }> {
    return this.fetchApi(`/api/v1/prompts/${promptId}/test`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ variables }),
    });
  }

  // TTS endpoints
  async generateSpeech(text: string, voiceId?: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/v1/tts/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text, voice_id: voiceId }),
    });

    if (!response.ok) {
      throw new Error(`TTS Error: ${response.status}`);
    }

    return response.blob();
  }

  async speakDocumentSummary(documentId: string, voiceId?: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/v1/tts/summary/${documentId}/speak`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ voice_id: voiceId }),
    });

    if (!response.ok) {
      throw new Error(`TTS Error: ${response.status}`);
    }

    return response.blob();
  }

  async getAvailableVoices(): Promise<any> {
    return this.fetchApi('/api/v1/tts/voices');
  }
}

export const api = new ApiClient();
export const documentApi = api;  // Alias for compatibility