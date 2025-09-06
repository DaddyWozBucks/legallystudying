import React, { useState } from 'react';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
  Button,
  ScrollArea,
  Badge,
  Alert,
  AlertDescription,
  Progress
} from '@/components/ui';
import { 
  FileText, 
  Download, 
  Copy, 
  Search,
  CheckCircle,
  AlertCircle,
  Loader2,
  Eye,
  Brain,
  FileSearch
} from 'lucide-react';

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
  analysis?: {
    key_information: {
      emails: string[];
      phone_numbers: string[];
      dates: string[];
      urls: string[];
      monetary_amounts: string[];
      document_numbers: string[];
    };
    keyword_analysis: {
      top_keywords: Record<string, number>;
    };
    sentiment: {
      positive_indicators: number;
      negative_indicators: number;
      sentiment_ratio: number;
    };
    summary: {
      readability_score: string;
      is_structured: boolean;
    };
  };
}

interface OCRTextViewerProps {
  result?: OCRResult;
  isProcessing?: boolean;
  onProcessFile?: (file: File) => void;
  processingProgress?: number;
}

export const OCRTextViewer: React.FC<OCRTextViewerProps> = ({
  result,
  isProcessing = false,
  onProcessFile,
  processingProgress = 0
}) => {
  const [copiedText, setCopiedText] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('text');

  const handleCopyText = () => {
    if (result?.extracted_text) {
      navigator.clipboard.writeText(result.extracted_text);
      setCopiedText(true);
      setTimeout(() => setCopiedText(false), 2000);
    }
  };

  const handleDownloadText = () => {
    if (result?.extracted_text) {
      const blob = new Blob([result.extracted_text], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `extracted_text_${new Date().getTime()}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  const highlightText = (text: string, term: string) => {
    if (!term) return text;
    const regex = new RegExp(`(${term})`, 'gi');
    return text.split(regex).map((part, i) => 
      regex.test(part) ? <mark key={i} className="bg-yellow-200">{part}</mark> : part
    );
  };

  if (isProcessing) {
    return (
      <Card className="w-full">
        <CardContent className="pt-6">
          <div className="flex flex-col items-center justify-center space-y-4 py-8">
            <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
            <p className="text-sm text-gray-600">Processing document with OCR...</p>
            {processingProgress > 0 && (
              <div className="w-full max-w-xs">
                <Progress value={processingProgress} className="w-full" />
                <p className="text-xs text-gray-500 mt-1 text-center">
                  {processingProgress}% complete
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!result) {
    return (
      <Card className="w-full">
        <CardContent className="pt-6">
          <div className="flex flex-col items-center justify-center space-y-4 py-8">
            <FileSearch className="h-12 w-12 text-gray-400" />
            <p className="text-sm text-gray-600">No document processed yet</p>
            {onProcessFile && (
              <Button
                variant="outline"
                onClick={() => {
                  const input = document.createElement('input');
                  input.type = 'file';
                  input.accept = '.pdf,.png,.jpg,.jpeg,.tiff,.bmp';
                  input.onchange = (e) => {
                    const file = (e.target as HTMLInputElement).files?.[0];
                    if (file) onProcessFile(file);
                  };
                  input.click();
                }}
              >
                <FileText className="mr-2 h-4 w-4" />
                Select Document for OCR
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            OCR Extracted Text
          </CardTitle>
          <div className="flex items-center gap-2">
            {result.success ? (
              <Badge variant="success" className="flex items-center gap-1">
                <CheckCircle className="h-3 w-3" />
                Success
              </Badge>
            ) : (
              <Badge variant="destructive" className="flex items-center gap-1">
                <AlertCircle className="h-3 w-3" />
                Failed
              </Badge>
            )}
          </div>
        </div>
        <div className="flex flex-wrap gap-4 mt-2 text-sm text-gray-600">
          <span>{result.summary.word_count.toLocaleString()} words</span>
          <span>{result.summary.character_count.toLocaleString()} characters</span>
          <span>{result.summary.line_count.toLocaleString()} lines</span>
          {result.metadata.pages && <span>{result.metadata.pages} pages</span>}
        </div>
      </CardHeader>

      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="text" className="flex items-center gap-2">
              <Eye className="h-4 w-4" />
              Extracted Text
            </TabsTrigger>
            <TabsTrigger value="analysis" className="flex items-center gap-2">
              <Brain className="h-4 w-4" />
              Analysis
            </TabsTrigger>
            <TabsTrigger value="metadata" className="flex items-center gap-2">
              <FileSearch className="h-4 w-4" />
              Metadata
            </TabsTrigger>
          </TabsList>

          <TabsContent value="text" className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="flex-1 relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search in text..."
                  className="w-full pl-8 pr-4 py-2 border rounded-md"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleCopyText}
                disabled={!result.extracted_text}
              >
                {copiedText ? (
                  <>
                    <CheckCircle className="mr-2 h-4 w-4" />
                    Copied
                  </>
                ) : (
                  <>
                    <Copy className="mr-2 h-4 w-4" />
                    Copy
                  </>
                )}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleDownloadText}
                disabled={!result.extracted_text}
              >
                <Download className="mr-2 h-4 w-4" />
                Download
              </Button>
            </div>

            <ScrollArea className="h-[500px] w-full rounded-md border p-4">
              <pre className="whitespace-pre-wrap font-mono text-sm">
                {searchTerm 
                  ? highlightText(result.extracted_text, searchTerm)
                  : result.extracted_text
                }
              </pre>
            </ScrollArea>
          </TabsContent>

          <TabsContent value="analysis" className="space-y-4">
            {result.analysis ? (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm">Key Information</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      {result.analysis.key_information.emails.length > 0 && (
                        <div>
                          <p className="text-xs font-medium text-gray-600">Emails Found:</p>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {result.analysis.key_information.emails.map((email, i) => (
                              <Badge key={i} variant="secondary" className="text-xs">
                                {email}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                      {result.analysis.key_information.phone_numbers.length > 0 && (
                        <div>
                          <p className="text-xs font-medium text-gray-600">Phone Numbers:</p>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {result.analysis.key_information.phone_numbers.map((phone, i) => (
                              <Badge key={i} variant="secondary" className="text-xs">
                                {phone}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                      {result.analysis.key_information.dates.length > 0 && (
                        <div>
                          <p className="text-xs font-medium text-gray-600">Dates:</p>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {result.analysis.key_information.dates.slice(0, 5).map((date, i) => (
                              <Badge key={i} variant="secondary" className="text-xs">
                                {date}
                              </Badge>
                            ))}
                            {result.analysis.key_information.dates.length > 5 && (
                              <Badge variant="outline" className="text-xs">
                                +{result.analysis.key_information.dates.length - 5} more
                              </Badge>
                            )}
                          </div>
                        </div>
                      )}
                      {result.analysis.key_information.monetary_amounts.length > 0 && (
                        <div>
                          <p className="text-xs font-medium text-gray-600">Monetary Amounts:</p>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {result.analysis.key_information.monetary_amounts.map((amount, i) => (
                              <Badge key={i} variant="secondary" className="text-xs">
                                {amount}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm">Top Keywords</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-1">
                        {Object.entries(result.analysis.keyword_analysis.top_keywords)
                          .slice(0, 10)
                          .map(([word, count]) => (
                            <div key={word} className="flex justify-between items-center">
                              <span className="text-sm">{word}</span>
                              <Badge variant="outline" className="text-xs">
                                {count}
                              </Badge>
                            </div>
                          ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm">Document Characteristics</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>
                        <p className="text-xs text-gray-600">Readability</p>
                        <p className="text-sm font-medium capitalize">
                          {result.analysis.summary.readability_score}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600">Structure</p>
                        <p className="text-sm font-medium">
                          {result.analysis.summary.is_structured ? 'Structured' : 'Unstructured'}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600">Sentiment</p>
                        <p className="text-sm font-medium">
                          {(result.analysis.sentiment.sentiment_ratio * 100).toFixed(0)}% Positive
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600">Extraction Method</p>
                        <p className="text-sm font-medium">
                          {result.metadata.extraction_method.join(', ')}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            ) : (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  No analysis available for this document.
                </AlertDescription>
              </Alert>
            )}
          </TabsContent>

          <TabsContent value="metadata" className="space-y-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">Processing Information</CardTitle>
              </CardHeader>
              <CardContent>
                <dl className="space-y-2">
                  <div>
                    <dt className="text-xs text-gray-600">Source File</dt>
                    <dd className="text-sm font-medium">{result.metadata.source}</dd>
                  </div>
                  <div>
                    <dt className="text-xs text-gray-600">File Type</dt>
                    <dd className="text-sm font-medium uppercase">{result.metadata.type}</dd>
                  </div>
                  <div>
                    <dt className="text-xs text-gray-600">Extraction Method</dt>
                    <dd className="text-sm font-medium">{result.metadata.extraction_method.join(', ')}</dd>
                  </div>
                  <div>
                    <dt className="text-xs text-gray-600">Processed At</dt>
                    <dd className="text-sm font-medium">
                      {new Date(result.metadata.timestamp).toLocaleString()}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs text-gray-600">Text File Path</dt>
                    <dd className="text-sm font-medium break-all">{result.text_file_path}</dd>
                  </div>
                </dl>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};