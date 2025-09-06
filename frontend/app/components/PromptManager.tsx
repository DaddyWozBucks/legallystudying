'use client';

import { useState, useEffect } from 'react';
import { FiEdit2, FiSave, FiX, FiRefreshCw, FiCheck } from 'react-icons/fi';
import { documentApi } from '../lib/api';

interface Prompt {
  id: string;
  name: string;
  description: string;
  template: string;
  category: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface PromptManagerProps {
  category?: string;
  promptName?: string;
  onPromptSelect?: (prompt: Prompt) => void;
  showInModal?: boolean;
}

export default function PromptManager({ 
  category = 'summary',
  promptName = 'document_summary',
  onPromptSelect,
  showInModal = false 
}: PromptManagerProps) {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null);
  const [editingPrompt, setEditingPrompt] = useState<Prompt | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  useEffect(() => {
    loadPrompts();
  }, [category]);

  const loadPrompts = async () => {
    setLoading(true);
    try {
      const response = await documentApi.getPrompts(category);
      setPrompts(response.prompts);
      
      // Select the default prompt or first one
      const defaultPrompt = response.prompts.find((p: Prompt) => p.name === promptName) || response.prompts[0];
      if (defaultPrompt) {
        setSelectedPrompt(defaultPrompt);
        onPromptSelect?.(defaultPrompt);
      }
    } catch (error) {
      console.error('Failed to load prompts:', error);
      setMessage({ type: 'error', text: 'Failed to load prompts' });
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (prompt: Prompt) => {
    setEditingPrompt({ ...prompt });
  };

  const handleSave = async () => {
    if (!editingPrompt) return;
    
    setSaving(true);
    setMessage(null);
    
    try {
      const updated = await documentApi.updatePrompt(editingPrompt.id, {
        template: editingPrompt.template,
        description: editingPrompt.description,
      });
      
      // Update local state
      setPrompts(prompts.map(p => p.id === updated.id ? updated : p));
      setSelectedPrompt(updated);
      setEditingPrompt(null);
      setMessage({ type: 'success', text: 'Prompt updated successfully!' });
      
      // Notify parent if needed
      onPromptSelect?.(updated);
      
      // Clear message after 3 seconds
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      console.error('Failed to save prompt:', error);
      setMessage({ type: 'error', text: 'Failed to save prompt' });
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditingPrompt(null);
  };

  const handleTemplateChange = (value: string) => {
    if (editingPrompt) {
      setEditingPrompt({ ...editingPrompt, template: value });
    }
  };

  const handleReset = async (prompt: Prompt) => {
    // Reset to default by reloading
    await loadPrompts();
    setMessage({ type: 'success', text: 'Prompt reset to default!' });
    setTimeout(() => setMessage(null), 3000);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <FiRefreshCw className="w-6 h-6 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Loading prompts...</span>
      </div>
    );
  }

  const containerClass = showInModal 
    ? "bg-white rounded-lg" 
    : "bg-white rounded-lg shadow-sm border border-gray-200 p-6";

  return (
    <div className={containerClass}>
      {!showInModal && (
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Prompt Templates</h2>
          <p className="text-sm text-gray-600 mt-1">
            Customize the AI prompts used for document processing
          </p>
        </div>
      )}

      {message && (
        <div className={`mb-4 p-3 rounded-lg flex items-center gap-2 ${
          message.type === 'success' 
            ? 'bg-green-50 text-green-800 border border-green-200' 
            : 'bg-red-50 text-red-800 border border-red-200'
        }`}>
          {message.type === 'success' ? <FiCheck className="w-5 h-5" /> : <FiX className="w-5 h-5" />}
          <span className="text-sm">{message.text}</span>
        </div>
      )}

      {/* Prompt selector */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Prompt Template
        </label>
        <select
          value={selectedPrompt?.id || ''}
          onChange={(e) => {
            const prompt = prompts.find(p => p.id === e.target.value);
            if (prompt) {
              setSelectedPrompt(prompt);
              setEditingPrompt(null);
              onPromptSelect?.(prompt);
            }
          }}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {prompts.map(prompt => (
            <option key={prompt.id} value={prompt.id}>
              {prompt.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} - {prompt.description}
            </option>
          ))}
        </select>
      </div>

      {/* Prompt editor */}
      {selectedPrompt && (
        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-700">
                Template Content
              </label>
              {!editingPrompt ? (
                <button
                  onClick={() => handleEdit(selectedPrompt)}
                  className="flex items-center gap-1 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                >
                  <FiEdit2 className="w-4 h-4" />
                  Edit
                </button>
              ) : (
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleSave}
                    disabled={saving}
                    className="flex items-center gap-1 px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400 transition-colors"
                  >
                    <FiSave className="w-4 h-4" />
                    {saving ? 'Saving...' : 'Save'}
                  </button>
                  <button
                    onClick={handleCancel}
                    className="flex items-center gap-1 px-3 py-1 text-sm bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
                  >
                    <FiX className="w-4 h-4" />
                    Cancel
                  </button>
                  <button
                    onClick={() => handleReset(selectedPrompt)}
                    className="flex items-center gap-1 px-3 py-1 text-sm bg-yellow-600 text-white rounded hover:bg-yellow-700 transition-colors"
                  >
                    <FiRefreshCw className="w-4 h-4" />
                    Reset
                  </button>
                </div>
              )}
            </div>
            
            <textarea
              value={editingPrompt?.template || selectedPrompt.template}
              onChange={(e) => handleTemplateChange(e.target.value)}
              disabled={!editingPrompt}
              className={`w-full h-64 px-3 py-2 border rounded-lg font-mono text-sm ${
                editingPrompt 
                  ? 'border-blue-300 bg-white focus:ring-2 focus:ring-blue-500' 
                  : 'border-gray-200 bg-gray-50'
              }`}
              placeholder="Enter your prompt template here..."
            />
            
            <div className="mt-2 text-xs text-gray-500">
              <p>Available placeholders:</p>
              <ul className="mt-1 space-y-1">
                {selectedPrompt.category === 'summary' && (
                  <>
                    <li><code className="bg-gray-100 px-1 py-0.5 rounded">{'{full_text}'}</code> - The complete document text</li>
                  </>
                )}
                {selectedPrompt.category === 'qa' && (
                  <>
                    <li><code className="bg-gray-100 px-1 py-0.5 rounded">{'{context}'}</code> - Relevant document context</li>
                    <li><code className="bg-gray-100 px-1 py-0.5 rounded">{'{question}'}</code> - The user's question</li>
                  </>
                )}
                {selectedPrompt.category === 'flashcards' && (
                  <>
                    <li><code className="bg-gray-100 px-1 py-0.5 rounded">{'{content}'}</code> - Document content</li>
                    <li><code className="bg-gray-100 px-1 py-0.5 rounded">{'{num_cards}'}</code> - Number of flashcards to generate</li>
                  </>
                )}
              </ul>
            </div>
          </div>

          {selectedPrompt.description && (
            <div className="pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-600">
                <strong>Description:</strong> {selectedPrompt.description}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Last updated: {new Date(selectedPrompt.updated_at).toLocaleDateString()}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}