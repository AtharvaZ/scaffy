import { useState } from 'react';
import { Button } from './ui/button';
import { X, Code2, Loader2, Eye } from 'lucide-react';
import { getConceptExample } from '../api/endpoints';
import { safeApiCall } from '../api/client';
import type { ScaffoldPackage } from '../types';

interface GetConceptExampleProps {
  language: string;
  currentTask: number;
  scaffold?: ScaffoldPackage;
  knownLanguage?: string;
  onClose: () => void;
}

export function GetConceptExample({ language, currentTask, scaffold, knownLanguage, onClose }: GetConceptExampleProps) {
  const [selectedConcept, setSelectedConcept] = useState<string | null>(null);
  const [example, setExample] = useState<{
    concept: string;
    example_type: 'basic_syntax' | 'intermediate_pattern' | 'advanced_pattern';
    code_example: string;
    explanation: string;
    comparison_to_known: string | null;
  } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Get concepts for current task
  const concepts = scaffold?.task_concepts?.[`task_${currentTask}`] || [];
  const taskDescription = scaffold?.todo_list?.[currentTask] || 'Current task';

  const handleGetExample = async (concept: string) => {
    setSelectedConcept(concept);
    setIsLoading(true);
    setExample(null);

    try {
      // Get concept example from backend
      const result = await safeApiCall(
        () => getConceptExample(
          concept,
          language,
          knownLanguage, // knownLanguage
          taskDescription // context
        ),
        'Failed to get concept example'
      );

      if (result) {
        setExample(result);
      }
    } catch (error) {
      console.error('Error getting concept example:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-full w-full bg-white dark:bg-background border-l border-black/10 dark:border-border flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-black/5 dark:border-border flex-shrink-0">
        <div className="flex items-center gap-2">
          <Code2 className="h-4 w-4 text-black dark:text-foreground" />
          <h3 className="text-sm font-semibold tracking-tight text-black dark:text-foreground">Concept Examples</h3>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose} className="h-7 w-7">
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {concepts.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <Code2 className="h-12 w-12 text-gray-400 dark:text-gray-600 mb-4" />
            <p className="text-sm text-gray-600 dark:text-gray-400">
              No concepts available for this task.
            </p>
          </div>
        ) : (
          <>
            <div>
              <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-3">
                Select a concept to see an example:
              </p>
              <div className="space-y-2">
                {concepts.map((concept, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleGetExample(concept)}
                    disabled={isLoading}
                    className={`w-full text-left px-3 py-2 rounded-lg border transition-all ${
                      selectedConcept === concept
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                        : 'border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 hover:border-blue-300 dark:hover:border-blue-700 text-gray-900 dark:text-gray-100'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">{concept}</span>
                      <Eye className="h-4 w-4" />
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {isLoading && (
              <div className="flex flex-col items-center justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-blue-600 dark:text-blue-400 mb-2" />
                <p className="text-sm text-gray-600 dark:text-gray-400">Loading example...</p>
              </div>
            )}

            {example && !isLoading && (
              <div className="space-y-4 pt-4 border-t border-gray-200 dark:border-gray-800">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-black dark:text-white">
                      {example.concept}
                    </span>
                    <span className="text-xs px-2 py-1 rounded bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300">
                      {example.example_type.replace('_', ' ')}
                    </span>
                  </div>
                </div>

                <div className="rounded-lg p-4 bg-gray-900 dark:bg-black border border-gray-700 dark:border-gray-800">
                  <pre className="text-xs text-gray-100 whitespace-pre-wrap leading-relaxed font-mono overflow-x-auto">
                    {example.code_example}
                  </pre>
                </div>

                <div className="rounded-lg p-4 bg-gray-50 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-800">
                  <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">Explanation:</p>
                  <p className="text-sm leading-relaxed text-gray-900 dark:text-gray-100">
                    {example.explanation}
                  </p>
                </div>

                {example.comparison_to_known && (
                  <div className="rounded-lg p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
                    <p className="text-xs font-medium text-blue-600 dark:text-blue-400 mb-2">Comparison:</p>
                    <p className="text-sm leading-relaxed text-gray-900 dark:text-gray-100">
                      {example.comparison_to_known}
                    </p>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

