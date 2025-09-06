'use client';

import React, { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { FiUploadCloud, FiFile, FiX, FiBook, FiCalendar } from 'react-icons/fi';
import { documentApi, courseApi } from '@/app/lib/api';

interface DocumentUploadProps {
  onUploadSuccess: () => void;
}

interface Course {
  id: string;
  course_number: string;
  name: string;
}

export default function DocumentUpload({ onUploadSuccess }: DocumentUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<string>('');
  const [selectedWeek, setSelectedWeek] = useState<number | undefined>(undefined);
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    try {
      const data = await courseApi.getCourses();
      setCourses(data);
    } catch (error) {
      console.error('Failed to load courses:', error);
    }
  };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setSelectedFiles(acceptedFiles);
    setError(null);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/tiff': ['.tiff', '.tif'],
      'image/bmp': ['.bmp'],
      'image/gif': ['.gif'],
    },
    multiple: false,
  });

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    setUploading(true);
    setError(null);

    try {
      for (const file of selectedFiles) {
        await documentApi.uploadDocument(
          file, 
          undefined, // parser plugin id
          selectedCourse || undefined,
          selectedWeek
        );
      }
      setSelectedFiles([]);
      setSelectedCourse('');
      setSelectedWeek(undefined);
      setShowAdvanced(false);
      onUploadSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(files => files.filter((_, i) => i !== index));
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <h2 className="text-xl font-semibold mb-4 text-gray-900">Upload Document</h2>
      
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all
          ${isDragActive 
            ? 'border-blue-500 bg-gradient-to-r from-blue-50 to-purple-50' 
            : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'}`}
      >
        <input {...getInputProps()} />
        <div className="p-3 bg-gradient-to-r from-blue-100 to-purple-100 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
          <FiUploadCloud className="w-8 h-8 text-blue-600" />
        </div>
        {isDragActive ? (
          <p className="text-blue-600 font-medium">Drop the file here...</p>
        ) : (
          <div>
            <p className="text-gray-700 font-medium mb-2">Drag & drop a document here, or click to select</p>
            <p className="text-sm text-gray-500">Supports PDF, DOCX, DOC, TXT, and image files</p>
            <p className="text-xs text-gray-400 mt-1">Images will be processed with OCR to extract text</p>
          </div>
        )}
      </div>

      {selectedFiles.length > 0 && (
        <div className="mt-4">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Selected Files:</h3>
          <div className="space-y-2">
            {selectedFiles.map((file, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg">
                <div className="flex items-center">
                  <FiFile className="w-4 h-4 mr-2 text-gray-500" />
                  <span className="text-sm text-gray-700 font-medium">{file.name}</span>
                  <span className="ml-2 text-xs text-gray-500">
                    ({(file.size / 1024 / 1024).toFixed(2)} MB)
                  </span>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="p-1 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  <FiX className="w-4 h-4 text-gray-500" />
                </button>
              </div>
            ))}
          </div>

          {/* Course Assignment Section */}
          <div className="mt-4 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="w-full flex items-center justify-between text-left"
            >
              <span className="text-sm font-medium text-gray-700">
                📚 Assign to Course (Optional)
              </span>
              <span className="text-xs text-gray-500">
                {showAdvanced ? '▼' : '▶'}
              </span>
            </button>

            {showAdvanced && (
              <div className="mt-4 space-y-3">
                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-1">
                    <FiBook className="w-4 h-4" />
                    Course
                  </label>
                  <select
                    value={selectedCourse}
                    onChange={(e) => setSelectedCourse(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">No Course Assignment</option>
                    {courses.map((course) => (
                      <option key={course.id} value={course.id}>
                        {course.course_number}: {course.name}
                      </option>
                    ))}
                  </select>
                </div>

                {selectedCourse && (
                  <div>
                    <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-1">
                      <FiCalendar className="w-4 h-4" />
                      Week Number
                    </label>
                    <input
                      type="number"
                      value={selectedWeek || ''}
                      onChange={(e) => setSelectedWeek(e.target.value ? parseInt(e.target.value) : undefined)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="e.g., 1, 2, 3..."
                      min="1"
                      max="52"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Organize readings by week for better course management
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {selectedFiles.length > 0 && (
        <button
          onClick={handleUpload}
          disabled={uploading}
          className="mt-4 w-full flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg"
        >
          {uploading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              Uploading...
            </>
          ) : (
            <>
              <FiUploadCloud className="w-5 h-5" />
              Upload Document
            </>
          )}
        </button>
      )}
    </div>
  );
}