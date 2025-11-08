import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { X, Lightbulb } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { FeedbackCardProps } from '../types';

export function FeedbackCard({ feedback, attemptNumber, onDismiss }: FeedbackCardProps) {
  const getHintLevel = () => {
    if (attemptNumber <= 2) return 1;
    if (attemptNumber <= 5) return 2;
    return 3;
  };

  const hintLevel = getHintLevel();
  const hintColorClass = {
    1: 'text-hint-level-1',
    2: 'text-hint-level-2',
    3: 'text-hint-level-3',
  }[hintLevel];

  const hintColors = {
    1: 'bg-blue-50 border-blue-100 text-blue-900',
    2: 'bg-amber-50 border-amber-100 text-amber-900',
    3: 'bg-green-50 border-green-100 text-green-900',
  }[hintLevel];

  return (
    <div className="animate-slideIn rounded-lg border border-black/5 bg-white p-6 vercel-shadow">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Lightbulb className="h-4 w-4 text-black" />
          <h3 className="text-sm font-semibold tracking-tight text-black">Feedback</h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-700">
            Attempt {attemptNumber}
          </span>
          <Button variant="ghost" size="icon" onClick={onDismiss} className="h-8 w-8">
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>
      <div className="space-y-4">
        <div>
          <h4 className="mb-1 text-sm font-medium text-black">Diagnosis</h4>
          <p className="text-sm text-gray-600">{feedback.diagnosis}</p>
        </div>
        <div>
          <h4 className="mb-1 text-sm font-medium text-black">Explanation</h4>
          <p className="text-sm text-gray-600">{feedback.explanation}</p>
        </div>
        <div>
          <h4 className="mb-1 text-sm font-medium text-black">Quick Fix</h4>
          <p className="text-sm text-gray-600">{feedback.small_fix}</p>
        </div>
        <div className={cn('rounded-md border p-3', hintColors)}>
          <h4 className="mb-1 text-sm font-medium">Hint (Level {hintLevel})</h4>
          <p className="text-sm">{feedback.next_hint}</p>
        </div>
        {feedback.line_numbers && feedback.line_numbers.length > 0 && (
          <div>
            <p className="text-xs text-gray-500">
              Relevant lines: {feedback.line_numbers.join(', ')}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

