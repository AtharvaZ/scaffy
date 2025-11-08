import { useState } from 'react';
import { Button } from './ui/button';
import { CheckCircle2, XCircle, ChevronDown, ChevronUp } from 'lucide-react';
import type { TestResultsProps } from '../types';

export function TestResults({ results, onRequestFeedback }: TestResultsProps) {
  const [showStdout, setShowStdout] = useState(true);  // Show output by default
  const [showStderr, setShowStderr] = useState(true);  // Show errors by default
  const allPassed = results.tests_failed === 0;

  return (
    <div className="rounded-lg border border-black/5 dark:border-border bg-white dark:bg-card p-6 vercel-shadow">
      <div className="mb-4 flex items-center gap-2">
        <h3 className="text-sm font-semibold tracking-tight text-black dark:text-foreground">
          {allPassed ? '✅ Code Executed Successfully' : '❌ Execution Error'}
        </h3>
      </div>
      <div className="space-y-4">
        <div className="flex items-center gap-6">
          <span className="text-sm text-gray-600 dark:text-muted-foreground">
            Execution Time: {results.runtime_ms || '< 5s'}
          </span>
        </div>

        {results.failed_tests.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-black">Failed Tests:</h4>
            {results.failed_tests.map((test, index) => (
              <div key={index} className="rounded-md border border-red-100 bg-red-50 p-3">
                <p className="text-sm font-medium text-black">{test.test_name}</p>
                <p className="mt-1 text-sm text-gray-600">
                  {test.error_message}
                </p>
                {test.line_number && (
                  <p className="mt-1 text-xs text-gray-500">
                    Line: {test.line_number}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}

        {results.stdout && (
          <div>
            <button
              onClick={() => setShowStdout(!showStdout)}
              className="flex items-center gap-2 text-sm font-medium text-black dark:text-foreground hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
            >
              {showStdout ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              📄 Output
            </button>
            {showStdout && (
              <pre className="mt-2 max-h-64 overflow-auto rounded-md border border-black/5 dark:border-border bg-gray-50 dark:bg-gray-900 p-3 text-sm text-gray-800 dark:text-gray-200 font-mono whitespace-pre-wrap">
                {results.stdout}
              </pre>
            )}
          </div>
        )}

        {results.stderr && (
          <div>
            <button
              onClick={() => setShowStderr(!showStderr)}
              className="flex items-center gap-2 text-sm font-medium text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 transition-colors"
            >
              {showStderr ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              ⚠️ Errors
            </button>
            {showStderr && (
              <pre className="mt-2 max-h-64 overflow-auto rounded-md border border-red-100 dark:border-red-900 bg-red-50 dark:bg-red-950/20 p-3 text-sm text-red-800 dark:text-red-300 font-mono whitespace-pre-wrap">
                {results.stderr}
              </pre>
            )}
          </div>
        )}

        {!allPassed && (
          <Button onClick={onRequestFeedback} variant="outline" className="w-full">
            Get Feedback
          </Button>
        )}
      </div>
    </div>
  );
}

