'use client';

import { useState, useEffect } from 'react';
import { Document } from '../types';
import { documentApi } from '../lib/api';
import { summaryStore } from '../lib/summaryStore';
import PromptManager from './PromptManager';
import { 
  FiX, 
  FiFile, 
  FiCalendar, 
  FiHardDrive, 
  FiFileText, 
  FiMessageSquare,
  FiLayers,
  FiTrash2,
  FiRefreshCw,
  FiCheckCircle,
  FiAlertCircle,
  FiClock,
  FiSettings
} from 'react-icons/fi';

interface DocumentDetailProps {
  document: Document;
  onClose: () => void;
  onGenerateFlashcards: (documentId: string) => void;
  onDocumentDeleted?: () => void;
}

export default function DocumentDetail({ 
  document, 
  onClose, 
  onGenerateFlashcards,
  onDocumentDeleted 
}: DocumentDetailProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'summary' | 'qa' | 'flashcards'>('overview');
  const [summary, setSummary] = useState<any>(null);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [summaryError, setSummaryError] = useState<string | null>(null);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState<string | null>(null);
  const [loadingAnswer, setLoadingAnswer] = useState(false);
  const [showPromptEditor, setShowPromptEditor] = useState(false);

  // Load saved summary when component mounts or document changes
  useEffect(() => {
    const savedSummary = summaryStore.getSummary(document.id);
    if (savedSummary) {
      setSummary(savedSummary);
    } else {
      setSummary(null);
    }
  }, [document.id]);

  const handleGenerateSummary = async (regenerate: boolean = false) => {
    setLoadingSummary(true);
    setSummaryError(null);
    
    // Clear existing summary if regenerating
    if (regenerate) {
      setSummary(null);
      summaryStore.clearSummary(document.id);
    }
    
    try {
      const result = await documentApi.summarizeDocument(document.id);
      setSummary(result);
      // Save summary to store
      summaryStore.setSummary(document.id, result);
    } catch (error: any) {
      console.error('Failed to generate summary:', error);
      setSummaryError(error.response?.data?.detail || 'Failed to generate summary. Please try again.');
    } finally {
      setLoadingSummary(false);
    }
  };

  const handleAskQuestion = async () => {
    if (!question.trim()) return;
    
    setLoadingAnswer(true);
    try {
      const result = await documentApi.askQuestion(document.id, question);
      setAnswer(result.answer);
    } catch (error) {
      console.error('Failed to get answer:', error);
      setAnswer('Failed to get answer. Please try again.');
    } finally {
      setLoadingAnswer(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        await documentApi.deleteDocument(document.id);
        onDocumentDeleted?.();
        onClose();
      } catch (error) {
        console.error('Failed to delete document:', error);
        alert('Failed to delete document. Please try again.');
      }
    }
  };

  const getStatusIcon = () => {
    switch (document.processing_status) {
      case 'completed':
        return <FiCheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <FiAlertCircle className="w-5 h-5 text-red-500" />;
      case 'processing':
        return <FiRefreshCw className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return <FiClock className="w-5 h-5 text-gray-400" />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="bg-white rounded-lg shadow-sm">
      {/* Header */}
      <div className="border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FiFile className="w-8 h-8 text-gray-400" />
            <div>
              <h2 className="text-xl font-semibold text-gray-900">{document.name}</h2>
              <div className="flex items-center gap-4 mt-1">
                <span className="text-sm text-gray-500">{formatFileSize(document.size_bytes)}</span>
                <span className="text-sm text-gray-500">{document.file_type}</span>
                <div className="flex items-center gap-1">
                  {getStatusIcon()}
                  <span className="text-sm text-gray-500 capitalize">{document.processing_status}</span>
                </div>
              </div>
            </div>
          </div>
          <button
            onClick={handleDelete}
            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            title="Delete document"
          >
            <FiTrash2 className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex gap-1 px-6">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-3 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'overview'
                ? 'text-blue-600 border-blue-600'
                : 'text-gray-500 border-transparent hover:text-gray-700'
            }`}
          >
            <div className="flex items-center gap-2">
              <FiFileText className="w-4 h-4" />
              Overview
            </div>
          </button>
          <button
            onClick={() => setActiveTab('summary')}
            className={`px-4 py-3 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'summary'
                ? 'text-blue-600 border-blue-600'
                : 'text-gray-500 border-transparent hover:text-gray-700'
            }`}
          >
            <div className="flex items-center gap-2">
              <FiFileText className="w-4 h-4" />
              Summary
            </div>
          </button>
          <button
            onClick={() => setActiveTab('qa')}
            className={`px-4 py-3 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'qa'
                ? 'text-blue-600 border-blue-600'
                : 'text-gray-500 border-transparent hover:text-gray-700'
            }`}
          >
            <div className="flex items-center gap-2">
              <FiMessageSquare className="w-4 h-4" />
              Q&A
            </div>
          </button>
          <button
            onClick={() => setActiveTab('flashcards')}
            className={`px-4 py-3 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'flashcards'
                ? 'text-blue-600 border-blue-600'
                : 'text-gray-500 border-transparent hover:text-gray-700'
            }`}
          >
            <div className="flex items-center gap-2">
              <FiLayers className="w-4 h-4" />
              Flashcards
            </div>
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Document ID</label>
                  <p className="mt-1 text-sm text-gray-900 font-mono">{document.id}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Created</label>
                  <p className="mt-1 text-sm text-gray-900">{formatDate(document.created_at)}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Last Updated</label>
                  <p className="mt-1 text-sm text-gray-900">{formatDate(document.updated_at)}</p>
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Content Hash</label>
                  <p className="mt-1 text-sm text-gray-900 font-mono truncate">{document.content_hash}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">File Path</label>
                  <p className="mt-1 text-sm text-gray-900 truncate">{document.path}</p>
                </div>
                {document.parser_plugin_id && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Parser Plugin</label>
                    <p className="mt-1 text-sm text-gray-900">{document.parser_plugin_id}</p>
                  </div>
                )}
              </div>
            </div>
            {document.error_message && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-800">
                  <strong>Error:</strong> {document.error_message}
                </p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'summary' && (
          <div className="space-y-4">
            {!summary ? (
              <div className="text-center py-12">
                <FiFileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-600 mb-4">No summary generated yet</p>
                <div className="flex items-center justify-center gap-3">
                  <button
                    onClick={() => setShowPromptEditor(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    <FiSettings className="w-4 h-4" />
                    Edit Prompt
                  </button>
                  <button
                    onClick={() => handleGenerateSummary(false)}
                    disabled={loadingSummary || document.processing_status !== 'completed'}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                  >
                    {loadingSummary ? (
                      <span className="flex items-center gap-2">
                        <FiRefreshCw className="w-4 h-4 animate-spin" />
                        Generating...
                      </span>
                    ) : (
                      'Generate Summary'
                    )}
                  </button>
                </div>
                {summaryError && (
                  <p className="mt-4 text-sm text-red-600">{summaryError}</p>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                {/* Header with regenerate button */}
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">Summary</h3>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setShowPromptEditor(true)}
                      className="flex items-center gap-2 px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                    >
                      <FiSettings className="w-4 h-4" />
                      Edit Prompt
                    </button>
                    <button
                      onClick={() => handleGenerateSummary(true)}
                      disabled={loadingSummary || document.processing_status !== 'completed'}
                      className="flex items-center gap-2 px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
                    >
                      <FiRefreshCw className={`w-4 h-4 ${loadingSummary ? 'animate-spin' : ''}`} />
                      {loadingSummary ? 'Regenerating...' : 'Regenerate'}
                    </button>
                  </div>
                </div>
                
                {/* Summary content */}
                {loadingSummary ? (
                  <div className="text-center py-8">
                    <FiRefreshCw className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-2" />
                    <p className="text-gray-600">Regenerating summary...</p>
                  </div>
                ) : (
                  <>
                    <div>
                      <p className="text-gray-700 whitespace-pre-wrap">{summary.summary}</p>
                    </div>
                    {summary.key_points && summary.key_points.length > 0 && (
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">Key Points</h3>
                        <ul className="space-y-2">
                          {summary.key_points.map((point: string, index: number) => (
                            <li key={index} className="flex items-start gap-2">
                              <span className="text-blue-600 mt-1">•</span>
                              <span className="text-gray-700">{point}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    <div className="pt-4 border-t border-gray-200 flex items-center justify-between">
                      <p className="text-xs text-gray-500">
                        Generated on {formatDate(summary.generated_at)}
                      </p>
                    </div>
                  </>
                )}
                
                {summaryError && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-800">{summaryError}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'qa' && (
          <div className="space-y-4">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Ask a question about this document
                </label>
                <textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Enter your question here..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={3}
                />
              </div>
              <button
                onClick={handleAskQuestion}
                disabled={loadingAnswer || !question.trim() || document.processing_status !== 'completed'}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                {loadingAnswer ? (
                  <span className="flex items-center gap-2">
                    <FiRefreshCw className="w-4 h-4 animate-spin" />
                    Getting answer...
                  </span>
                ) : (
                  'Get Answer'
                )}
              </button>
            </div>
            
            {answer && (
              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Answer:</h4>
                <p className="text-gray-700 whitespace-pre-wrap">{answer}</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'flashcards' && (
          <div className="text-center py-12">
            <FiLayers className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600 mb-4">Flashcard generation coming soon!</p>
            <button
              onClick={() => onGenerateFlashcards(document.id)}
              disabled={document.processing_status !== 'completed'}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              Generate Flashcards
            </button>
          </div>
        )}
      </div>
      
      {/* Prompt Editor Modal */}
      {showPromptEditor && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg w-full max-w-3xl max-h-[80vh] overflow-hidden flex flex-col">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold text-gray-900">Edit Summary Prompt</h3>
              <button
                onClick={() => setShowPromptEditor(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <FiX className="w-5 h-5" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4">
              <PromptManager
                category="summary"
                promptName={document.file_type === '.pdf' && document.name.toLowerCase().includes('legal') 
                  ? 'legal_document_summary' 
                  : 'document_summary'}
                showInModal={true}
                onPromptSelect={(prompt) => {
                  console.log('Selected prompt:', prompt);
                }}
              />
            </div>
            <div className="p-4 border-t flex justify-end gap-3">
              <button
                onClick={() => setShowPromptEditor(false)}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Close
              </button>
              <button
                onClick={() => {
                  setShowPromptEditor(false);
                  handleGenerateSummary(true);
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Generate with Updated Prompt
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}