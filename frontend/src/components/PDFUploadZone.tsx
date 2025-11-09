import { useState, useRef } from 'react';
import { Upload, FileText, X, Loader2, AlertCircle } from 'lucide-react';
import { extractPdfText } from '../api/endpoints';
import { safeApiCall } from '../api/client';

interface PDFUploadZoneProps {
  onTextExtracted: (text: string) => void;
  disabled?: boolean;
}

export function PDFUploadZone({ onTextExtracted, disabled = false }: PDFUploadZoneProps) {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractionError, setExtractionError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

  const validateFile = (file: File): string | null => {
    // Check file type
    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
      return 'Only PDF files are allowed';
    }
    
    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      return `File size must be less than ${MAX_FILE_SIZE / (1024 * 1024)}MB`;
    }
    
    if (file.size === 0) {
      return 'File is empty';
    }
    
    return null;
  };

  const handleFileSelect = async (file: File) => {
    // Validate file
    const error = validateFile(file);
    if (error) {
      setExtractionError(error);
      setUploadedFile(null);
      return;
    }

    setUploadedFile(file);
    setExtractionError(null);
    setIsExtracting(true);

    try {
      const result = await safeApiCall(
        () => extractPdfText(file),
        'Failed to extract text from PDF'
      );

      if (result && result.success) {
        onTextExtracted(result.extracted_text);
        setExtractionError(null);
      } else {
        const errorMsg = result?.error || 'Failed to extract text from PDF';
        setExtractionError(errorMsg);
        setUploadedFile(null);
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Failed to extract text from PDF';
      setExtractionError(errorMsg);
      setUploadedFile(null);
    } finally {
      setIsExtracting(false);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (disabled || isExtracting) return;
    
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (!disabled && !isExtracting) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleRemoveFile = () => {
    setUploadedFile(null);
    setExtractionError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="space-y-4">
      {/* File Upload Zone */}
      {!uploadedFile && (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => !disabled && !isExtracting && fileInputRef.current?.click()}
          className={`
            relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
            transition-all duration-200
            ${isDragging
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/10'
              : 'border-gray-300 dark:border-gray-700 hover:border-gray-400 dark:hover:border-gray-600'
            }
            ${disabled || isExtracting
              ? 'opacity-50 cursor-not-allowed'
              : 'hover:bg-gray-50 dark:hover:bg-gray-900/50'
            }
          `}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,application/pdf"
            onChange={handleFileInputChange}
            disabled={disabled || isExtracting}
            className="hidden"
          />
          
          {isExtracting ? (
            <div className="flex flex-col items-center gap-3">
              <Loader2 className="h-10 w-10 text-blue-600 dark:text-blue-400 animate-spin" />
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Extracting text from PDF...
              </p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3">
              <Upload className="h-10 w-10 text-gray-400 dark:text-gray-600" />
              <div>
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Click to upload or drag and drop
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                  PDF file (max {MAX_FILE_SIZE / (1024 * 1024)}MB)
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Uploaded File Preview */}
      {uploadedFile && !isExtracting && (
        <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 flex-1 min-w-0">
              <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                  {uploadedFile.name}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-500">
                  {formatFileSize(uploadedFile.size)}
                </p>
              </div>
            </div>
            <button
              onClick={handleRemoveFile}
              disabled={disabled}
              className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Remove file"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* Error Message */}
      {extractionError && (
        <div className="rounded-lg border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950/20 p-3">
          <div className="flex items-start gap-2">
            <AlertCircle className="h-4 w-4 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-800 dark:text-red-400">
              {extractionError}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

