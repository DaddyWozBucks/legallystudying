import axios from 'axios';
import type { Document, DocumentSummary, QueryResponse, HealthCheck } from '@/app/types';

// Determine the API base URL based on the environment
const getApiBaseUrl = () => {
  // If explicitly set, use it
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  
  // If running in browser
  if (typeof window !== 'undefined') {
    // If on port 3000 or 3001 (dev server), use backend directly
    if (window.location.port === '3000' || window.location.port === '3001') {
      return 'http://localhost:8000';
    }
    // Otherwise use relative path (through nginx proxy)
    return '';
  }
  
  // Server-side rendering
  return '';
};

const API_BASE_URL = getApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const documentApi = {
  async uploadDocument(file: File, parserPluginId?: string, courseId?: string, week?: number): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    
    const params = new URLSearchParams();
    if (parserPluginId) params.append('parser_plugin_id', parserPluginId);
    if (courseId) params.append('course_id', courseId);
    if (week !== undefined) params.append('week', week.toString());
    
    const queryString = params.toString();
    const url = queryString ? `/api/v1/documents/upload?${queryString}` : '/api/v1/documents/upload';
    
    const response = await api.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async getDocuments(): Promise<Document[]> {
    const response = await api.get('/api/v1/documents/');
    // Handle both array and object response formats
    if (Array.isArray(response.data)) {
      return response.data;
    }
    // If response has documents property, return that array
    if (response.data && response.data.documents) {
      return response.data.documents;
    }
    return [];
  },

  async getDocument(id: string): Promise<Document> {
    const response = await api.get(`/api/v1/documents/${id}`);
    return response.data;
  },

  async deleteDocument(id: string): Promise<void> {
    await api.delete(`/api/v1/documents/${id}`);
  },

  async generateSummary(documentId: string): Promise<DocumentSummary> {
    const response = await api.post(`/api/v1/documents/${documentId}/summarize`);
    return response.data;
  },

  async summarizeDocument(documentId: string): Promise<DocumentSummary> {
    const response = await api.post(`/api/v1/documents/${documentId}/summarize`);
    return response.data;
  },

  async query(query: string, documentIds?: string[]): Promise<QueryResponse> {
    const response = await api.post('/api/v1/query', {
      query,
      document_ids: documentIds,
    });
    return response.data;
  },

  async askQuestion(documentId: string, question: string): Promise<{ answer: string }> {
    const response = await api.post(`/api/v1/documents/${documentId}/qa`, {
      question,
    });
    return response.data;
  },

  async healthCheck(): Promise<HealthCheck> {
    const response = await api.get('/api/v1/health/');
    return response.data;
  },

  async getPrompts(category?: string): Promise<any> {
    const params = category ? `?category=${category}` : '';
    const response = await api.get(`/api/v1/prompts/${params}`);
    return response.data;
  },

  async getPrompt(id: string): Promise<any> {
    const response = await api.get(`/api/v1/prompts/${id}`);
    return response.data;
  },

  async getPromptByName(name: string): Promise<any> {
    const response = await api.get(`/api/v1/prompts/by-name/${name}`);
    return response.data;
  },

  async updatePrompt(id: string, data: any): Promise<any> {
    const response = await api.put(`/api/v1/prompts/${id}`, data);
    return response.data;
  },
};

export const degreeApi = {
  async getDegrees(): Promise<any[]> {
    const response = await api.get('/api/v1/degrees/');
    return response.data.degrees || [];
  },

  async getDegree(id: string): Promise<any> {
    const response = await api.get(`/api/v1/degrees/${id}`);
    return response.data;
  },

  async createDegree(data: any): Promise<any> {
    const response = await api.post('/api/v1/degrees/', data);
    return response.data;
  },

  async updateDegree(id: string, data: any): Promise<any> {
    const response = await api.put(`/api/v1/degrees/${id}`, data);
    return response.data;
  },

  async deleteDegree(id: string): Promise<void> {
    await api.delete(`/api/v1/degrees/${id}`);
  },
};

export const courseApi = {
  async getCourses(degreeId?: string): Promise<any[]> {
    const params = degreeId ? `?degree_id=${degreeId}` : '';
    const response = await api.get(`/api/v1/courses/${params}`);
    return response.data.courses || [];
  },

  async getCourse(id: string): Promise<any> {
    const response = await api.get(`/api/v1/courses/${id}`);
    return response.data;
  },

  async getCourseByNumber(courseNumber: string): Promise<any> {
    const response = await api.get(`/api/v1/courses/by-number/${courseNumber}`);
    return response.data;
  },

  async createCourse(data: any): Promise<any> {
    const response = await api.post('/api/v1/courses/', data);
    return response.data;
  },

  async updateCourse(id: string, data: any): Promise<any> {
    const response = await api.put(`/api/v1/courses/${id}`, data);
    return response.data;
  },

  async deleteCourse(id: string): Promise<void> {
    await api.delete(`/api/v1/courses/${id}`);
  },
};