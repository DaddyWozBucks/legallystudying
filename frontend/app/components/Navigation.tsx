'use client';

import { FiFile, FiBook, FiAward, FiUpload } from 'react-icons/fi';

interface NavigationProps {
  activeTab: 'documents' | 'degrees' | 'courses';
  onTabChange: (tab: 'documents' | 'degrees' | 'courses') => void;
  onUploadClick: () => void;
}

export default function Navigation({ activeTab, onTabChange, onUploadClick }: NavigationProps) {
  return (
    <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          <span className="bg-gradient-to-r from-blue-600 to-purple-600 text-transparent bg-clip-text">
            LegalDify
          </span>
        </h1>
        <p className="text-sm text-gray-600">Document Intelligence Platform</p>
      </div>

      {/* Navigation Tabs */}
      <div className="p-4 space-y-1">
        <button
          onClick={() => onTabChange('documents')}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
            activeTab === 'documents'
              ? 'bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 text-blue-700'
              : 'hover:bg-gray-50 text-gray-700'
          }`}
        >
          <FiFile className="w-5 h-5" />
          <span className="font-medium">Documents</span>
        </button>

        <button
          onClick={() => onTabChange('degrees')}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
            activeTab === 'degrees'
              ? 'bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 text-blue-700'
              : 'hover:bg-gray-50 text-gray-700'
          }`}
        >
          <FiAward className="w-5 h-5" />
          <span className="font-medium">Degree Programs</span>
        </button>

        <button
          onClick={() => onTabChange('courses')}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
            activeTab === 'courses'
              ? 'bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 text-blue-700'
              : 'hover:bg-gray-50 text-gray-700'
          }`}
        >
          <FiBook className="w-5 h-5" />
          <span className="font-medium">Courses</span>
        </button>
      </div>

      <div className="px-4 pb-4">
        <button
          onClick={onUploadClick}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all shadow-md hover:shadow-lg"
        >
          <FiUpload className="w-5 h-5" />
          Upload Document
        </button>
      </div>

      <div className="flex-1 overflow-y-auto" />
    </div>
  );
}