import { useState } from "react";
import { Button } from "./ui/button";
import { FileText, Download, ChevronDown } from "lucide-react";
import { downloadFile, downloadAllFilesAsZip } from "../utils/fileDownload";

interface FileSelectorProps {
  files: string[];
  currentFile: string;
  onFileSelect: (filename: string) => void;
  fileHasChanges?: (filename: string) => boolean;
  fileContents?: Record<string, string>;
  originalStarterFiles?: Record<string, string>;
}

export function FileSelector({
  files,
  currentFile,
  onFileSelect,
  fileHasChanges,
  fileContents,
  originalStarterFiles
}: FileSelectorProps) {
  const [showDownloadMenu, setShowDownloadMenu] = useState(false);

  const handleDownloadFile = (filename: string, event: React.MouseEvent) => {
    event.stopPropagation(); // Prevent file selection
    if (fileContents && fileContents[filename]) {
      downloadFile(filename, fileContents[filename]);
    }
  };

  const handleDownloadAllWithCode = () => {
    if (fileContents && Object.keys(fileContents).length > 0) {
      downloadAllFilesAsZip(fileContents, 'scaffy-project-with-code.zip');
    }
    setShowDownloadMenu(false);
  };

  const handleDownloadAllStarter = () => {
    if (originalStarterFiles && Object.keys(originalStarterFiles).length > 0) {
      downloadAllFilesAsZip(originalStarterFiles, 'scaffy-project-starter.zip');
    }
    setShowDownloadMenu(false);
  };

  return (
    <div className="mb-8 border-b border-gray-200/60 dark:border-gray-800/60 pb-4">
      <div className="flex items-center gap-3 mb-4">
        <FileText className="h-6 w-6 text-gray-700 dark:text-gray-300" />
        <span className="text-xl font-bold text-gray-900 dark:text-gray-100">
          Files
        </span>
      </div>
      <div className="flex items-center gap-3 relative">
        {/* Scrollable file names container */}
        <div className="flex-1 overflow-x-auto overflow-y-hidden scrollbar-thin relative" style={{ scrollbarWidth: 'thin' }}>
          <div className="flex gap-3 items-center pb-2">
            {files.map((filename) => {
              const isSelected = filename === currentFile;
              const hasChanges = fileHasChanges?.(filename);

              return (
                <div key={filename} className="relative group flex-shrink-0">
                  <Button
                    onClick={() => onFileSelect(filename)}
                    variant={isSelected ? "default" : "outline"}
                    size="default"
                    className={`
                      relative px-5 py-2 pr-10
                      ${isSelected
                        ? "bg-blue-600 hover:bg-blue-700 text-white border-blue-600"
                        : "border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-900 text-gray-700 dark:text-gray-300"
                      }
                    `}
                  >
                    <span className="font-mono text-sm font-semibold">{filename}</span>
                    {hasChanges && !isSelected && (
                      <span className="absolute -top-1 -right-1 w-3 h-3 bg-blue-600 rounded-full" />
                    )}
                  </Button>
                  {fileContents && (
                    <button
                      onClick={(e) => handleDownloadFile(filename, e)}
                      className={`
                        absolute right-2 top-1/2 -translate-y-1/2
                        p-1 rounded transition-opacity
                        ${isSelected
                          ? "text-white hover:bg-blue-700"
                          : "text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"
                        }
                      `}
                      title={`Download ${filename}`}
                      aria-label={`Download ${filename}`}
                    >
                      <Download className="h-3.5 w-3.5" />
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Download button with gradient shadow on the left */}
        {files.length > 1 && fileContents && (
          <div className="relative flex-shrink-0 pl-4">
            {/* Gradient shadow overlay */}
            <div className="absolute left-0 top-0 bottom-0 w-12 pointer-events-none bg-gradient-to-r from-white via-white to-transparent dark:from-black dark:via-black dark:to-transparent" style={{ marginLeft: '-3rem' }}></div>

            <Button
              variant="outline"
              size="default"
              onClick={() => setShowDownloadMenu(!showDownloadMenu)}
              className="text-sm border-gray-200 dark:border-gray-800 px-5 py-2 bg-white dark:bg-black relative z-10"
            >
              <Download className="mr-2 h-4 w-4" />
              Download Files
              <ChevronDown className="ml-2 h-3.5 w-3.5" />
            </Button>

            {showDownloadMenu && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setShowDownloadMenu(false)}
                />
                <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg shadow-lg z-20">
                  <div className="p-1">
                    <button
                      onClick={handleDownloadAllWithCode}
                      className="w-full text-left px-3 py-2 text-sm rounded hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-900 dark:text-gray-100"
                    >
                      <div className="font-medium">With Your Code</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        Download files with all your changes
                      </div>
                    </button>
                    <button
                      onClick={handleDownloadAllStarter}
                      className="w-full text-left px-3 py-2 text-sm rounded hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-900 dark:text-gray-100"
                    >
                      <div className="font-medium">Original Starter Files</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        Download original scaffolded code
                      </div>
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
