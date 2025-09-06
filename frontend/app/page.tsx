'use client';

import { useState, useEffect } from 'react';
import DocumentUpload from './components/DocumentUpload';
import DocumentList from './components/DocumentList';
import DocumentDetail from './components/DocumentDetail';
import Navigation from './components/Navigation';
import DegreesManager from './components/DegreesManager';
import CoursesManager from './components/CoursesManager';
import { Document } from './types';
import { documentApi } from './lib/api';
import { FiAlertTriangle, FiFile, FiUpload, FiFolder } from 'react-icons/fi';

export default function Home() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [healthStatus, setHealthStatus] = useState<'healthy' | 'unhealthy' | 'checking'>('checking');
  const [showUpload, setShowUpload] = useState(false);
  const [activeTab, setActiveTab] = useState<'documents' | 'degrees' | 'courses'>('documents');

  useEffect(() => {
    checkHealth();
    loadDocuments();
  }, []);

  const checkHealth = async () => {
    try {
      const health = await documentApi.healthCheck();
      setHealthStatus(health.status === 'healthy' ? 'healthy' : 'unhealthy');
    } catch (error) {
      setHealthStatus('unhealthy');
    }
  };

  const loadDocuments = async () => {
    setLoading(true);
    setError(null);
    try {
      const docs = await documentApi.getDocuments();
      setDocuments(Array.isArray(docs) ? docs : []);
    } catch (err: any) {
      setError('Failed to load documents. Please ensure the backend is running.');
      console.error('Failed to load documents:', err);
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateFlashcards = (documentId: string) => {
    console.log('Generate flashcards for document:', documentId);
    alert('Flashcard generation will be available soon!');
  };

  if (healthStatus === 'unhealthy') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <FiAlertTriangle className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">Backend Service Unavailable</h2>
          <p className="text-gray-600 mb-4">
            Please ensure the backend service is running at http://localhost:8000
          </p>
          <button 
            onClick={() => {
              setHealthStatus('checking');
              checkHealth();
              loadDocuments();
            }}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar with Navigation */}
      <Navigation
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onUploadClick={() => setShowUpload(!showUpload)}
      />

      {/* Documents List (shown when documents tab is active) */}
      {activeTab === 'documents' && (
        <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider">
              Documents ({documents.length})
            </h3>
          </div>
          
          <div className="flex-1 overflow-y-auto">
            {loading ? (
              <div className="px-4 py-8">
                <div className="animate-pulse space-y-2">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="h-12 bg-gray-100 rounded"></div>
                  ))}
                </div>
              </div>
            ) : documents.length === 0 ? (
              <div className="px-4 py-8 text-center">
                <FiFolder className="w-12 h-12 text-gray-300 mx-auto mb-2" />
                <p className="text-sm text-gray-500">No documents yet</p>
                <button
                  onClick={() => setShowUpload(true)}
                  className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                >
                  Upload First Document
                </button>
              </div>
            ) : (
              <div className="px-2 py-2">
                {documents.map((doc) => (
                  <button
                    key={doc.id}
                    onClick={() => setSelectedDocument(doc)}
                    className={`w-full text-left px-3 py-3 rounded-lg mb-1 transition-colors ${
                      selectedDocument?.id === doc.id
                        ? 'bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200'
                        : 'hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <FiFile className="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {doc.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {(doc.size_bytes / 1024).toFixed(1)} KB • {doc.file_type}
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        {/* Upload Form */}
        {showUpload && activeTab === 'documents' && (
          <div className="p-6 border-b border-gray-200 bg-white">
            <DocumentUpload 
              onUploadSuccess={() => {
                loadDocuments();
                setShowUpload(false);
              }} 
            />
          </div>
        )}

        {/* Documents Tab Content */}
        {activeTab === 'documents' && (
          selectedDocument ? (
            <div className="p-6">
              <DocumentDetail
                document={selectedDocument}
                onClose={() => setSelectedDocument(null)}
                onGenerateFlashcards={handleGenerateFlashcards}
                onDocumentDeleted={() => {
                  loadDocuments();
                  setSelectedDocument(null);
                }}
              />
            </div>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <FiFile className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-gray-900 mb-2">Select a Document</h2>
                <p className="text-gray-600">
                  Choose a document from the sidebar to view details
                </p>
                {documents.length === 0 && (
                  <button
                    onClick={() => setShowUpload(true)}
                    className="mt-4 px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all"
                  >
                    Upload Your First Document
                  </button>
                )}
              </div>
            </div>
          )
        )}

        {/* Degrees Tab Content */}
        {activeTab === 'degrees' && (
          <div className="p-6">
            <DegreesManager />
          </div>
        )}

        {/* Courses Tab Content */}
        {activeTab === 'courses' && (
          <div className="p-6">
            <CoursesManager />
          </div>
        )}
      </div>
    </div>
  );
}