import React, { useState, useCallback } from 'react';
import { OCRTextViewer } from './components/OCRTextViewer';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle,
  Button,
  Alert,
  AlertDescription
} from './components/ui';
import { 
  Upload, 
  FileText, 
  AlertCircle,
  CheckCircle2,
  Loader2
} from 'lucide-react';
import { useDropzone } from 'react-dropzone';

interface OCRResult {
  success: boolean;
  extracted_text: string;
  text_file_path: string;
  metadata: {
    source: string;
    type: string;
    pages?: number;
    extraction_method: string[];
    timestamp: string;
  };
  summary: {
    character_count: number;
    word_count: number;
    line_count: number;
  };
  analysis?: any;
}

export const OCRPage: React.FC = () => {
  const [ocrResult, setOcrResult] = useState<OCRResult | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [processingProgress, setProcessingProgress] = useState(0);

  const processFile = async (file: File) => {
    setIsProcessing(true);
    setError(null);
    setProcessingProgress(0);
    setUploadedFile(file);

    const formData = new FormData();
    formData.append('file', file);

    // Simulate progress updates
    const progressInterval = setInterval(() => {
      setProcessingProgress(prev => {
        if (prev >= 90) return prev;
        return prev + 10;
      });
    }, 500);

    try {
      const response = await fetch('/api/ocr/process', {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);
      setProcessingProgress(100);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'OCR processing failed');
      }

      const result = await response.json();
      setOcrResult(result);
      setError(null);
    } catch (err) {
      clearInterval(progressInterval);
      setError(err instanceof Error ? err.message : 'An error occurred during OCR processing');
      setOcrResult(null);
    } finally {
      setIsProcessing(false);
      setProcessingProgress(0);
    }
  };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      processFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
    },
    maxFiles: 1,
    disabled: isProcessing
  });

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">OCR Text Extraction</h1>
        <p className="text-gray-600">
          Extract text from PDFs and images, then view and analyze the content
        </p>
      </div>

      {/* File Upload Area */}
      {!ocrResult && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5" />
              Upload Document
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div
              {...getRootProps()}
              className={`
                border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
                transition-colors duration-200
                ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
                ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}
              `}
            >
              <input {...getInputProps()} />
              
              {isProcessing ? (
                <div className="space-y-4">
                  <Loader2 className="mx-auto h-12 w-12 text-blue-500 animate-spin" />
                  <p className="text-gray-600">Processing {uploadedFile?.name}...</p>
                  <div className="max-w-xs mx-auto">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${processingProgress}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{processingProgress}%</p>
                  </div>
                </div>
              ) : (
                <>
                  <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  {isDragActive ? (
                    <p className="text-gray-600">Drop the file here...</p>
                  ) : (
                    <div className="space-y-2">
                      <p className="text-gray-600">
                        Drag and drop a PDF or image file here
                      </p>
                      <p className="text-sm text-gray-500">
                        or click to browse files
                      </p>
                      <p className="text-xs text-gray-400 mt-4">
                        Supported formats: PDF, PNG, JPG, JPEG, TIFF, BMP, GIF
                      </p>
                    </div>
                  )}
                </>
              )}
            </div>

            {uploadedFile && !isProcessing && (
              <div className="mt-4 p-3 bg-gray-50 rounded-lg flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-gray-500" />
                  <span className="text-sm text-gray-700">{uploadedFile.name}</span>
                  <span className="text-xs text-gray-500">
                    ({(uploadedFile.size / 1024 / 1024).toFixed(2)} MB)
                  </span>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => processFile(uploadedFile)}
                >
                  Reprocess
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Success Message */}
      {ocrResult && !error && (
        <Alert className="mb-6 border-green-200 bg-green-50">
          <CheckCircle2 className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            Text extraction completed successfully! The extracted text has been saved to: {ocrResult.text_file_path}
          </AlertDescription>
        </Alert>
      )}

      {/* OCR Results Viewer */}
      {ocrResult && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Extraction Results</h2>
            <Button
              variant="outline"
              onClick={() => {
                setOcrResult(null);
                setUploadedFile(null);
                setError(null);
              }}
            >
              <Upload className="mr-2 h-4 w-4" />
              Process New Document
            </Button>
          </div>
          
          <OCRTextViewer 
            result={ocrResult}
            isProcessing={isProcessing}
            processingProgress={processingProgress}
          />
        </div>
      )}

      {/* Instructions */}
      {!ocrResult && !isProcessing && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="text-lg">How it works</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-gray-600">
            <div className="flex gap-3">
              <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-bold">
                1
              </span>
              <p>Upload a PDF or image file containing text</p>
            </div>
            <div className="flex gap-3">
              <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-bold">
                2
              </span>
              <p>OCR extracts all text and saves it to a readable text file</p>
            </div>
            <div className="flex gap-3">
              <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-bold">
                3
              </span>
              <p>View the extracted text with search and highlighting</p>
            </div>
            <div className="flex gap-3">
              <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-bold">
                4
              </span>
              <p>Analyze the text to find emails, dates, keywords, and more</p>
            </div>
            <div className="flex gap-3">
              <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-bold">
                5
              </span>
              <p>Download or copy the extracted text for further use</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};