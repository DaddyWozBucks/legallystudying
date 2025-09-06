'use client';

import { useState, useEffect } from 'react';
import { degreeApi } from '../lib/api';
import { FiPlus, FiEdit2, FiTrash2, FiAward, FiX, FiSave } from 'react-icons/fi';

interface Degree {
  id: string;
  name: string;
  abbreviation: string;
  description: string;
  prompt_context: string;
  department: string;
  duration_years: number;
  credit_hours: number;
  is_active: boolean;
}

export default function DegreesManager() {
  const [degrees, setDegrees] = useState<Degree[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingDegree, setEditingDegree] = useState<Degree | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    abbreviation: '',
    description: '',
    prompt_context: '',
    department: '',
    duration_years: 4,
    credit_hours: 120,
  });

  useEffect(() => {
    loadDegrees();
  }, []);

  const loadDegrees = async () => {
    try {
      setLoading(true);
      const data = await degreeApi.getDegrees();
      setDegrees(data);
    } catch (error) {
      console.error('Failed to load degrees:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingDegree) {
        await degreeApi.updateDegree(editingDegree.id, formData);
      } else {
        await degreeApi.createDegree(formData);
      }
      loadDegrees();
      resetForm();
    } catch (error) {
      console.error('Failed to save degree:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this degree program?')) {
      try {
        await degreeApi.deleteDegree(id);
        loadDegrees();
      } catch (error) {
        console.error('Failed to delete degree:', error);
      }
    }
  };

  const resetForm = () => {
    setShowForm(false);
    setEditingDegree(null);
    setFormData({
      name: '',
      abbreviation: '',
      description: '',
      prompt_context: '',
      department: '',
      duration_years: 4,
      credit_hours: 120,
    });
  };

  const startEdit = (degree: Degree) => {
    setEditingDegree(degree);
    setFormData({
      name: degree.name,
      abbreviation: degree.abbreviation,
      description: degree.description,
      prompt_context: degree.prompt_context,
      department: degree.department,
      duration_years: degree.duration_years,
      credit_hours: degree.credit_hours,
    });
    setShowForm(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Degree Programs</h2>
        <p className="text-gray-600">Manage academic degree programs and their contexts</p>
      </div>

      {/* Add New Button */}
      {!showForm && (
        <button
          onClick={() => setShowForm(true)}
          className="mb-6 flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all shadow-md hover:shadow-lg"
        >
          <FiPlus className="w-5 h-5" />
          Add New Degree Program
        </button>
      )}

      {/* Form */}
      {showForm && (
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6 border border-gray-200">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-semibold text-gray-900">
              {editingDegree ? 'Edit Degree Program' : 'New Degree Program'}
            </h3>
            <button
              onClick={resetForm}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <FiX className="w-5 h-5" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Degree Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Juris Doctor"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Abbreviation
                </label>
                <input
                  type="text"
                  value={formData.abbreviation}
                  onChange={(e) => setFormData({ ...formData, abbreviation: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., JD"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={3}
                placeholder="Describe the degree program..."
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Prompt Context
                <span className="ml-2 text-xs text-gray-500">
                  (This will be added to AI prompts for better context)
                </span>
              </label>
              <textarea
                value={formData.prompt_context}
                onChange={(e) => setFormData({ ...formData, prompt_context: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={2}
                placeholder="e.g., Legal education focusing on constitutional law, contracts, torts..."
                required
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Department
                </label>
                <input
                  type="text"
                  value={formData.department}
                  onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Law School"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Duration (years)
                </label>
                <input
                  type="number"
                  value={formData.duration_years}
                  onChange={(e) => setFormData({ ...formData, duration_years: parseFloat(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  step="0.5"
                  min="1"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Credit Hours
                </label>
                <input
                  type="number"
                  value={formData.credit_hours}
                  onChange={(e) => setFormData({ ...formData, credit_hours: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="0"
                  required
                />
              </div>
            </div>

            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={resetForm}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all"
              >
                <FiSave className="w-4 h-4" />
                {editingDegree ? 'Update' : 'Create'} Degree
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Degrees List */}
      <div className="grid gap-4">
        {degrees.length === 0 ? (
          <div className="bg-white rounded-xl p-12 text-center border border-gray-200">
            <FiAward className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Degree Programs Yet</h3>
            <p className="text-gray-500">Add your first degree program to get started</p>
          </div>
        ) : (
          degrees.map((degree) => (
            <div
              key={degree.id}
              className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 bg-gradient-to-r from-blue-100 to-purple-100 rounded-lg">
                      <FiAward className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        {degree.name} ({degree.abbreviation})
                      </h3>
                      <p className="text-sm text-gray-500">{degree.department}</p>
                    </div>
                  </div>
                  <p className="text-gray-600 mb-3">{degree.description}</p>
                  <div className="bg-gray-50 rounded-lg p-3 mb-3">
                    <p className="text-sm text-gray-700">
                      <span className="font-medium">AI Context:</span> {degree.prompt_context}
                    </p>
                  </div>
                  <div className="flex gap-4 text-sm text-gray-500">
                    <span>{degree.duration_years} years</span>
                    <span>•</span>
                    <span>{degree.credit_hours} credit hours</span>
                  </div>
                </div>
                <div className="flex gap-2 ml-4">
                  <button
                    onClick={() => startEdit(degree)}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <FiEdit2 className="w-4 h-4 text-gray-600" />
                  </button>
                  <button
                    onClick={() => handleDelete(degree.id)}
                    className="p-2 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <FiTrash2 className="w-4 h-4 text-red-600" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}