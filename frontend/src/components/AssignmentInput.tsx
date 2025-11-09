import { useState } from 'react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Select } from './ui/select';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import type { AssignmentInputProps } from '../types';
import { Loader2, FileText, Type } from 'lucide-react';
import { PDFUploadZone } from './PDFUploadZone';

export function AssignmentInput({ onAssignmentSubmit, loading }: AssignmentInputProps) {
  const [inputMode, setInputMode] = useState<'text' | 'pdf'>('text');
  const [assignmentText, setAssignmentText] = useState('');
  const [language, setLanguage] = useState('python');
  const [proficientLanguage, setProficientLanguage] = useState('python');

  const handleSubmit = () => {
    if (assignmentText.trim()) {
      onAssignmentSubmit(assignmentText, language, proficientLanguage);
    }
  };

  const handleTextExtracted = (text: string) => {
    setAssignmentText(text);
    // Switch to text mode after extraction so user can edit
    setInputMode('text');
  };

  return (
    <div className="w-full max-w-2xl">
      <div className="rounded-2xl border border-gray-200/60 dark:border-gray-800/60 bg-white dark:bg-black p-8 shadow-sm">
        <div className="mb-6">
          <h2 className="text-xl font-semibold tracking-tight text-black dark:text-white">Create Assignment</h2>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">Enter your assignment details to get started</p>
        </div>
        <div className="space-y-6">
          {/* Mode Toggle */}
          <div className="flex items-center gap-2 p-1 rounded-lg bg-gray-100 dark:bg-gray-900 border border-gray-200 dark:border-gray-800">
            <button
              type="button"
              onClick={() => setInputMode('text')}
              disabled={loading}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                inputMode === 'text'
                  ? 'bg-white dark:bg-gray-800 text-black dark:text-white shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <Type className="h-4 w-4" />
              Enter Text
            </button>
            <button
              type="button"
              onClick={() => setInputMode('pdf')}
              disabled={loading}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                inputMode === 'pdf'
                  ? 'bg-white dark:bg-gray-800 text-black dark:text-white shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <FileText className="h-4 w-4" />
              Upload PDF
            </button>
          </div>

          {/* Text Input Mode */}
          {inputMode === 'text' && (
            <div className="space-y-2">
              <label htmlFor="assignment-text" className="text-sm font-medium text-black dark:text-white">
                Assignment Description
              </label>
              <Textarea
                id="assignment-text"
                placeholder="Paste or type your assignment here..."
                value={assignmentText}
                onChange={(e) => setAssignmentText(e.target.value)}
                rows={8}
                disabled={loading}
                className="resize-none border-gray-200 dark:border-gray-800 focus:border-blue-500 dark:focus:border-blue-500 focus:ring-0"
              />
            </div>
          )}

          {/* PDF Upload Mode */}
          {inputMode === 'pdf' && (
            <div className="space-y-2">
              <label className="text-sm font-medium text-black dark:text-white">
                Upload PDF Assignment
              </label>
              <PDFUploadZone
                onTextExtracted={handleTextExtracted}
                disabled={loading}
              />
              {assignmentText && (
                <div className="mt-4 space-y-2">
                  <label className="text-sm font-medium text-black dark:text-white">
                    Extracted Text (editable)
                  </label>
                  <Textarea
                    placeholder="Extracted text will appear here..."
                    value={assignmentText}
                    onChange={(e) => setAssignmentText(e.target.value)}
                    rows={8}
                    disabled={loading}
                    className="resize-none border-gray-200 dark:border-gray-800 focus:border-blue-500 dark:focus:border-blue-500 focus:ring-0"
                  />
                </div>
              )}
            </div>
          )}

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <label htmlFor="language" className="text-sm font-medium text-black dark:text-white">
                Language to Learn
              </label>
              <Select
                id="language"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                disabled={loading}
                className="border-gray-200 dark:border-gray-800 focus:border-blue-500 dark:focus:border-blue-500"
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="java">Java</option>
              </Select>
            </div>
            <div className="space-y-2">
              <label htmlFor="proficient-language" className="text-sm font-medium text-black dark:text-white">
                Language You Know
              </label>
              <Select
                id="proficient-language"
                value={proficientLanguage}
                onChange={(e) => setProficientLanguage(e.target.value)}
                disabled={loading}
                className="border-gray-200 dark:border-gray-800 focus:border-blue-500 dark:focus:border-blue-500"
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="java">Java</option>
                <option value="c++">C++</option>
                <option value="c">C</option>
                <option value="typescript">TypeScript</option>
              </Select>
            </div>
          </div>
          <Button
            onClick={handleSubmit}
            disabled={!assignmentText.trim() || loading}
            className="w-full bg-gradient-to-r from-blue-600 to-blue-500 text-white hover:from-blue-700 hover:to-blue-600 dark:from-blue-500 dark:to-blue-400 dark:hover:from-blue-600 dark:hover:to-blue-500 shadow-md shadow-blue-500/20 transition-all duration-150 disabled:bg-gray-400 dark:disabled:bg-gray-600 disabled:hover:bg-gray-400 dark:disabled:hover:bg-gray-600"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              'Submit Assignment'
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

