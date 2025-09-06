'use client';

import { useState, useEffect } from 'react';
import { courseApi, degreeApi } from '../lib/api';
import { FiPlus, FiEdit2, FiTrash2, FiBook, FiX, FiSave, FiTag } from 'react-icons/fi';

interface Course {
  id: string;
  course_number: string;
  name: string;
  description: string;
  prompt_context: string;
  degree_id?: string;
  credits: number;
  semester: string;
  professor: string;
  attributes: string[];
  prerequisites: string[];
  learning_objectives: string[];
  is_active: boolean;
}

interface Degree {
  id: string;
  name: string;
  abbreviation: string;
}

export default function CoursesManager() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [degrees, setDegrees] = useState<Degree[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingCourse, setEditingCourse] = useState<Course | null>(null);
  const [formData, setFormData] = useState({
    course_number: '',
    name: '',
    description: '',
    prompt_context: '',
    degree_id: '',
    credits: 3,
    semester: '',
    professor: '',
    attributes: [] as string[],
    prerequisites: [] as string[],
    learning_objectives: [] as string[],
  });
  const [newAttribute, setNewAttribute] = useState('');
  const [newPrerequisite, setNewPrerequisite] = useState('');
  const [newObjective, setNewObjective] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [coursesData, degreesData] = await Promise.all([
        courseApi.getCourses(),
        degreeApi.getDegrees(),
      ]);
      setCourses(coursesData);
      setDegrees(degreesData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingCourse) {
        await courseApi.updateCourse(editingCourse.id, formData);
      } else {
        await courseApi.createCourse(formData);
      }
      loadData();
      resetForm();
    } catch (error) {
      console.error('Failed to save course:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this course?')) {
      try {
        await courseApi.deleteCourse(id);
        loadData();
      } catch (error) {
        console.error('Failed to delete course:', error);
      }
    }
  };

  const resetForm = () => {
    setShowForm(false);
    setEditingCourse(null);
    setFormData({
      course_number: '',
      name: '',
      description: '',
      prompt_context: '',
      degree_id: '',
      credits: 3,
      semester: '',
      professor: '',
      attributes: [],
      prerequisites: [],
      learning_objectives: [],
    });
    setNewAttribute('');
    setNewPrerequisite('');
    setNewObjective('');
  };

  const startEdit = (course: Course) => {
    setEditingCourse(course);
    setFormData({
      course_number: course.course_number,
      name: course.name,
      description: course.description,
      prompt_context: course.prompt_context,
      degree_id: course.degree_id || '',
      credits: course.credits,
      semester: course.semester,
      professor: course.professor,
      attributes: course.attributes || [],
      prerequisites: course.prerequisites || [],
      learning_objectives: course.learning_objectives || [],
    });
    setShowForm(true);
  };

  const addToList = (type: 'attributes' | 'prerequisites' | 'learning_objectives', value: string) => {
    if (value.trim()) {
      setFormData({
        ...formData,
        [type]: [...formData[type], value.trim()],
      });
    }
  };

  const removeFromList = (type: 'attributes' | 'prerequisites' | 'learning_objectives', index: number) => {
    setFormData({
      ...formData,
      [type]: formData[type].filter((_, i) => i !== index),
    });
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
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Courses</h2>
        <p className="text-gray-600">Manage courses and their educational contexts</p>
      </div>

      {/* Add New Button */}
      {!showForm && (
        <button
          onClick={() => setShowForm(true)}
          className="mb-6 flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all shadow-md hover:shadow-lg"
        >
          <FiPlus className="w-5 h-5" />
          Add New Course
        </button>
      )}

      {/* Form */}
      {showForm && (
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6 border border-gray-200">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-semibold text-gray-900">
              {editingCourse ? 'Edit Course' : 'New Course'}
            </h3>
            <button
              onClick={resetForm}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <FiX className="w-5 h-5" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Course Number
                </label>
                <input
                  type="text"
                  value={formData.course_number}
                  onChange={(e) => setFormData({ ...formData, course_number: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., LAW 101"
                  required
                />
              </div>
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Course Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Constitutional Law"
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
                placeholder="Describe the course content..."
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
                placeholder="e.g., Focus on constitutional principles, judicial review, federalism..."
                required
              />
            </div>

            <div className="grid grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Degree Program
                </label>
                <select
                  value={formData.degree_id}
                  onChange={(e) => setFormData({ ...formData, degree_id: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select Degree</option>
                  {degrees.map((degree) => (
                    <option key={degree.id} value={degree.id}>
                      {degree.name} ({degree.abbreviation})
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Credits
                </label>
                <input
                  type="number"
                  value={formData.credits}
                  onChange={(e) => setFormData({ ...formData, credits: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="0"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Semester
                </label>
                <input
                  type="text"
                  value={formData.semester}
                  onChange={(e) => setFormData({ ...formData, semester: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Fall 2024"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Professor
                </label>
                <input
                  type="text"
                  value={formData.professor}
                  onChange={(e) => setFormData({ ...formData, professor: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Dr. Smith"
                  required
                />
              </div>
            </div>

            {/* Attributes */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Attributes
              </label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={newAttribute}
                  onChange={(e) => setNewAttribute(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      addToList('attributes', newAttribute);
                      setNewAttribute('');
                    }
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Required, Bar Exam Subject"
                />
                <button
                  type="button"
                  onClick={() => {
                    addToList('attributes', newAttribute);
                    setNewAttribute('');
                  }}
                  className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
                >
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.attributes.map((attr, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                  >
                    <FiTag className="w-3 h-3" />
                    {attr}
                    <button
                      type="button"
                      onClick={() => removeFromList('attributes', index)}
                      className="ml-1 hover:text-blue-900"
                    >
                      <FiX className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            </div>

            {/* Prerequisites */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Prerequisites
              </label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={newPrerequisite}
                  onChange={(e) => setNewPrerequisite(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      addToList('prerequisites', newPrerequisite);
                      setNewPrerequisite('');
                    }
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., LAW 100"
                />
                <button
                  type="button"
                  onClick={() => {
                    addToList('prerequisites', newPrerequisite);
                    setNewPrerequisite('');
                  }}
                  className="px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors"
                >
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.prerequisites.map((prereq, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center gap-1 px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm"
                  >
                    {prereq}
                    <button
                      type="button"
                      onClick={() => removeFromList('prerequisites', index)}
                      className="ml-1 hover:text-purple-900"
                    >
                      <FiX className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            </div>

            {/* Learning Objectives */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Learning Objectives
              </label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={newObjective}
                  onChange={(e) => setNewObjective(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      addToList('learning_objectives', newObjective);
                      setNewObjective('');
                    }
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Understand constitutional principles"
                />
                <button
                  type="button"
                  onClick={() => {
                    addToList('learning_objectives', newObjective);
                    setNewObjective('');
                  }}
                  className="px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors"
                >
                  Add
                </button>
              </div>
              <div className="space-y-1">
                {formData.learning_objectives.map((obj, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-2 p-2 bg-green-50 rounded-lg"
                  >
                    <span className="flex-1 text-sm text-gray-700">• {obj}</span>
                    <button
                      type="button"
                      onClick={() => removeFromList('learning_objectives', index)}
                      className="text-green-600 hover:text-green-800"
                    >
                      <FiX className="w-4 h-4" />
                    </button>
                  </div>
                ))}
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
                {editingCourse ? 'Update' : 'Create'} Course
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Courses List */}
      <div className="grid gap-4">
        {courses.length === 0 ? (
          <div className="bg-white rounded-xl p-12 text-center border border-gray-200">
            <FiBook className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Courses Yet</h3>
            <p className="text-gray-500">Add your first course to get started</p>
          </div>
        ) : (
          courses.map((course) => {
            const degree = degrees.find(d => d.id === course.degree_id);
            return (
              <div
                key={course.id}
                className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="p-2 bg-gradient-to-r from-blue-100 to-purple-100 rounded-lg">
                        <FiBook className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {course.course_number}: {course.name}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {course.professor} • {course.semester} • {course.credits} credits
                        </p>
                      </div>
                    </div>
                    
                    <p className="text-gray-600 mb-3">{course.description}</p>
                    
                    <div className="bg-gray-50 rounded-lg p-3 mb-3">
                      <p className="text-sm text-gray-700">
                        <span className="font-medium">AI Context:</span> {course.prompt_context}
                      </p>
                    </div>

                    {degree && (
                      <p className="text-sm text-gray-500 mb-2">
                        <span className="font-medium">Degree:</span> {degree.name} ({degree.abbreviation})
                      </p>
                    )}

                    {course.attributes && course.attributes.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-2">
                        {course.attributes.map((attr, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs"
                          >
                            <FiTag className="w-3 h-3" />
                            {attr}
                          </span>
                        ))}
                      </div>
                    )}

                    {course.prerequisites && course.prerequisites.length > 0 && (
                      <p className="text-sm text-gray-500">
                        <span className="font-medium">Prerequisites:</span> {course.prerequisites.join(', ')}
                      </p>
                    )}
                  </div>
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => startEdit(course)}
                      className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      <FiEdit2 className="w-4 h-4 text-gray-600" />
                    </button>
                    <button
                      onClick={() => handleDelete(course.id)}
                      className="p-2 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <FiTrash2 className="w-4 h-4 text-red-600" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}