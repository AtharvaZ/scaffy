import { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { X, Lightbulb, Loader2 } from 'lucide-react';
import { getHint } from '../api/endpoints';
import { safeApiCall } from '../api/client';
import type { ScaffoldPackage } from '../types';

interface GetHintProps {
  code: string;
  language: string;
  currentTask: number;
  scaffold?: ScaffoldPackage;
  currentTodoIndex?: number;
  knownLanguage?: string;
  onClose: () => void;
  autoTrigger?: boolean;
  autoTriggerQuestion?: string;
}

export function GetHint({ code, language, currentTask, scaffold, currentTodoIndex = 0, knownLanguage, onClose, autoTrigger = false, autoTriggerQuestion }: GetHintProps) {
  const [hint, setHint] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [helpCount, setHelpCount] = useState(0);
  const [previousHints, setPreviousHints] = useState<string[]>([]);

  const handleGetHint = async (questionOverride?: string) => {
    if (!scaffold) return;

    setIsLoading(true);
    try {
      // Get current TODO if available
      const todos = scaffold.task_todos?.[`task_${currentTask}`] || scaffold.todos || [];
      const currentTodo = todos[currentTodoIndex] || null;
      
      // Build question - use override if provided, otherwise use TODO or default
      const question = questionOverride || (currentTodo 
        ? `I'm stuck on: ${currentTodo}`
        : `I'm stuck on task ${currentTask + 1}`);

      // Get task description and concepts
      const taskDescription = scaffold.todo_list?.[currentTask] || 'Current task';
      const concepts = scaffold.task_concepts?.[`task_${currentTask}`] || [];

      // Ensure all values are serializable (strings/arrays/numbers only)
      const cleanCode = typeof code === 'string' ? code : String(code || '');
      const cleanConcepts = Array.isArray(concepts) ? concepts.map(c => typeof c === 'string' ? c : String(c)) : [];
      const cleanQuestion = typeof question === 'string' ? question : String(question || '');
      const cleanTaskDescription = typeof taskDescription === 'string' ? taskDescription : String(taskDescription || '');
      const cleanPreviousHints = Array.isArray(previousHints) ? previousHints.map(h => typeof h === 'string' ? h : String(h)) : [];
      const cleanKnownLanguage = knownLanguage ? (typeof knownLanguage === 'string' ? knownLanguage : String(knownLanguage)) : undefined;
      const cleanTargetLanguage = language ? (typeof language === 'string' ? language : String(language)) : undefined;

      // Get hint from backend
      // Note: knownLanguage should be passed as prop or retrieved from store
      const result = await safeApiCall(
        () => getHint(
          cleanTaskDescription,
          cleanConcepts,
          cleanCode,
          cleanQuestion,
          cleanPreviousHints,
          helpCount + 1,
          cleanKnownLanguage,
          cleanTargetLanguage
        ),
        'Failed to get hint'
      );

      if (result) {
        setHint(result.hint);
        setPreviousHints(prev => [...prev, result.hint]);
        setHelpCount(prev => prev + 1);
      }
    } catch (error) {
      console.error('Error getting hint:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Auto-trigger hint when component mounts with autoTrigger prop
  useEffect(() => {
    if (autoTrigger && scaffold && autoTriggerQuestion && helpCount === 0 && !isLoading) {
      handleGetHint(autoTriggerQuestion);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoTrigger, autoTriggerQuestion]);

  const getHintLevel = () => {
    if (helpCount === 0) return 1;
    if (helpCount === 1) return 2;
    return 3;
  };

  const hintLevel = getHintLevel();
  const hintLevelLabels = {
    1: 'Gentle Guidance',
    2: 'More Specific',
    3: 'Detailed Hint'
  };

  return (
    <div className="h-full w-full bg-white dark:bg-background border-l border-black/10 dark:border-border flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-black/5 dark:border-border flex-shrink-0">
        <div className="flex items-center gap-2">
          <Lightbulb className="h-4 w-4 text-black dark:text-foreground" />
          <h3 className="text-sm font-semibold tracking-tight text-black dark:text-foreground">Get Hint</h3>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose} className="h-7 w-7">
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {!hint && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <Lightbulb className="h-12 w-12 text-gray-400 dark:text-gray-600 mb-4" />
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              Need help with your code?
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-500">
              Click the button below to get a contextual hint based on your current progress.
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
              Hints get more specific with each request.
            </p>
          </div>
        )}

        {isLoading && (
          <div className="flex flex-col items-center justify-center h-full">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600 dark:text-blue-400 mb-2" />
            <p className="text-sm text-gray-600 dark:text-gray-400">Getting hint...</p>
          </div>
        )}

        {hint && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium px-2 py-1 rounded bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300">
                  {hintLevelLabels[hintLevel]}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-500">
                  Hint #{helpCount}
                </span>
              </div>
            </div>
            
            <div className="rounded-lg p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
              <p className="text-sm leading-relaxed whitespace-pre-wrap text-gray-900 dark:text-gray-100">
                {hint}
              </p>
            </div>

            {helpCount < 3 && (
              <p className="text-xs text-gray-500 dark:text-gray-500 text-center">
                Need more help? Click "Get Hint" again for a more specific hint.
              </p>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-black/5 dark:border-border flex-shrink-0 bg-white dark:bg-background">
        <Button
          onClick={handleGetHint}
          disabled={isLoading}
          className="w-full bg-gradient-to-r from-blue-600 to-blue-500 text-white hover:from-blue-700 hover:to-blue-600 dark:from-blue-500 dark:to-blue-400 dark:hover:from-blue-600 dark:hover:to-blue-500"
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Getting Hint...
            </>
          ) : (
            <>
              <Lightbulb className="mr-2 h-4 w-4" />
              Get Hint
            </>
          )}
        </Button>
      </div>
    </div>
  );
}

