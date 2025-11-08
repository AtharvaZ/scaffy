import { useState } from 'react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Select } from './ui/select';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import type { AssignmentInputProps } from '../types';
import { Loader2 } from 'lucide-react';

export function AssignmentInput({ onAssignmentSubmit, loading }: AssignmentInputProps) {
  const [assignmentText, setAssignmentText] = useState('');
  const [language, setLanguage] = useState('python');
  const [proficientLanguage, setProficientLanguage] = useState('python');

  const handleSubmit = () => {
    if (assignmentText.trim()) {
      onAssignmentSubmit(assignmentText, language, proficientLanguage);
    }
  };

  return (
    <div className="w-full max-w-2xl">
      <div className="rounded-lg border border-black/5 dark:border-border bg-white dark:bg-card p-8 vercel-shadow">
        <div className="mb-6">
          <h2 className="text-xl font-semibold tracking-tight text-black dark:text-foreground">Create Assignment</h2>
          <p className="mt-1 text-sm text-gray-600 dark:text-muted-foreground">Enter your assignment details to get started</p>
        </div>
        <div className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="assignment-text" className="text-sm font-medium text-black dark:text-foreground">
              Assignment Description
            </label>
            <Textarea
              id="assignment-text"
              placeholder="Paste or type your assignment here..."
              value={assignmentText}
              onChange={(e) => setAssignmentText(e.target.value)}
              rows={8}
              disabled={loading}
              className="resize-none border-black/10 dark:border-border focus:border-black/20 dark:focus:border-border focus:ring-0"
            />
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <label htmlFor="language" className="text-sm font-medium text-black dark:text-foreground">
                Language to Learn
              </label>
              <Select
                id="language"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                disabled={loading}
                className="border-black/10 dark:border-border focus:border-black/20 dark:focus:border-border"
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="java">Java</option>
              </Select>
            </div>
            <div className="space-y-2">
              <label htmlFor="proficient-language" className="text-sm font-medium text-black dark:text-foreground">
                Language You Know
              </label>
              <Select
                id="proficient-language"
                value={proficientLanguage}
                onChange={(e) => setProficientLanguage(e.target.value)}
                disabled={loading}
                className="border-black/10 dark:border-border focus:border-black/20 dark:focus:border-border"
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
            className="w-full bg-black text-white hover:bg-black/90 dark:bg-primary dark:text-primary-foreground dark:hover:bg-primary/90 transition-all duration-150 disabled:bg-gray-400 dark:disabled:bg-gray-600 disabled:hover:bg-gray-400 dark:disabled:hover:bg-gray-600"
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

