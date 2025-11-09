import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { AssignmentInput } from '../components/AssignmentInput';
import { ProcessingProgress } from '../components/ProcessingProgress';
import { parseAndScaffold } from '../api/endpoints';
import { safeApiCall } from '../api/client';
import { Button } from '../components/ui/button';
import { DarkModeToggle } from '../components/DarkModeToggle';
import { ArrowRight, Code2 } from 'lucide-react';

export function TaskPage() {
  const navigate = useNavigate();
  const {
    assignmentText,
    language,
    proficientLanguage,
    parserOutput,
    scaffold,
    isLoading,
    error,
    setAssignmentText,
    setLanguage,
    setProficientLanguage,
    setParserOutput,
    setScaffold,
    setStudentCode,
    setAssignmentId,
    setIsLoading,
    setError,
  } = useAppStore();

  // Check if we already have a scaffold loaded (coming back from editor)
  const [hasSubmitted, setHasSubmitted] = useState(!!scaffold && !!parserOutput);
  const [progressStage, setProgressStage] = useState<'parsing' | 'generating' | 'complete'>('parsing');
  const [progressTasks, setProgressTasks] = useState({ completed: 0, total: 0 });

  // Update hasSubmitted when scaffold or parserOutput changes
  useEffect(() => {
    if (scaffold && parserOutput && !isLoading) {
      setHasSubmitted(true);
    }
  }, [scaffold, parserOutput, isLoading]);

  const handleAssignmentSubmit = async (text: string, lang: string, proficientLang: string) => {
    setAssignmentText(text);
    setLanguage(lang);
    setProficientLanguage(proficientLang);
    setIsLoading(true);
    setError(null);
    setProgressStage('parsing');

    try {
      const result = await safeApiCall(
        () => parseAndScaffold(
          text, 
          lang, 
          proficientLang, 
          'intermediate',
          (stage, completed, total) => {
            setProgressStage(stage);
            setProgressTasks({ completed, total });
          }
        ),
        'Failed to parse and scaffold assignment'
      );

      if (result) {
        setProgressStage('complete');
        
        // Convert TaskBreakdownSchema to ParserOutput format for compatibility
        const parserOutput = {
          tasks: result.parser_output.tasks,
          overview: result.parser_output.overview,
          total_estimated_time: result.parser_output.total_estimated_time,
        };
        setParserOutput(parserOutput);
        setScaffold(result.scaffold_package);
        
        // Get the first starter file or use code_snippet
        const initialCode = result.scaffold_package.code_snippet || 
          (Object.keys(result.scaffold_package.starter_files).length > 0
            ? Object.values(result.scaffold_package.starter_files)[0]
            : '');
        setStudentCode(initialCode);
        
        // Generate assignment ID
        const newAssignmentId = `assignment-${Date.now()}`;
        setAssignmentId(newAssignmentId);
        
        setHasSubmitted(true);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleContinueToEditor = () => {
    navigate('/editor');
  };

  return (
    <div className="min-h-screen bg-white dark:bg-black">
      {/* Header */}
      <header className="border-b border-gray-200/60 dark:border-gray-800/60 bg-white dark:bg-black">
        <div className="mx-auto max-w-[1440px] px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <Link to="/" className="flex items-center">
              <span className="text-[15px] font-semibold text-black dark:text-white">Scaffy</span>
            </Link>
            <div className="flex items-center gap-8">
              <DarkModeToggle />
              <Button variant="ghost" size="sm" onClick={() => navigate('/')} className="text-sm">
                Home
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-[1440px] px-6 py-8 lg:px-8">
        {/* Error Display */}
        {error && (
          <div className="mb-6 rounded-lg border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950/20 p-4">
            <p className="text-sm text-red-800 dark:text-red-400">{error}</p>
          </div>
        )}

        {/* Loading Progress */}
        {isLoading && (
          <div className="flex min-h-[calc(100vh-200px)] items-center justify-center py-16">
            <ProcessingProgress
              stage={progressStage}
              tasksTotal={progressTasks.total}
              tasksCompleted={progressTasks.completed}
            />
          </div>
        )}

        {/* Assignment Input */}
        {!hasSubmitted && !isLoading && (
          <div className="flex min-h-[calc(100vh-200px)] items-center justify-center py-16">
            <AssignmentInput
              onAssignmentSubmit={handleAssignmentSubmit}
              loading={isLoading}
            />
          </div>
        )}

        {/* Task Breakdown - Individual Task Containers */}
        {hasSubmitted && scaffold && parserOutput && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-semibold tracking-tight text-black dark:text-white">
                Task Breakdown
              </h2>
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={() => {
                    setHasSubmitted(false);
                    setError(null);
                  }}
                  className="border-gray-200 dark:border-gray-800"
                >
                  New Assignment
                </Button>
                <Button
                  onClick={handleContinueToEditor}
                  className="bg-gradient-to-r from-blue-600 to-blue-500 text-white hover:from-blue-700 hover:to-blue-600 dark:from-blue-500 dark:to-blue-400 dark:hover:from-blue-600 dark:hover:to-blue-500 shadow-md shadow-blue-500/20"
                >
                  Continue to Editor
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </div>
            
            {/* Vertical Container with Individual Task Containers */}
            <div className="space-y-6">
              {scaffold.todo_list.map((todo, taskIndex) => {
                const taskId = `task_${taskIndex}`;
                const task = parserOutput.tasks?.[taskIndex] || null;
                const taskConcepts = task?.concepts || [];
                const taskConceptExamples = scaffold.task_concept_examples?.[`task_${taskIndex}`] || {};
                
                // Get starter code structure for this specific task
                const getTaskCodeStructure = () => {
                  if (!scaffold.starter_files || Object.keys(scaffold.starter_files).length === 0) {
                    return null;
                  }
                  const starterCode = Object.values(scaffold.starter_files)[0];
                  
                  // Extract code snippet relevant to this specific task
                  // Look for TODO comments with task numbers or extract by task index
                  const lines = starterCode.split('\n');
                  const taskNumber = taskIndex + 1;
                  
                  // Try to find code block for this specific task
                  // Look for patterns like "TODO: task 1", "TODO 1", or task-specific markers
                  const taskPatterns = [
                    new RegExp(`TODO.*${taskNumber}`, 'i'),
                    new RegExp(`TODO.*task.*${taskNumber}`, 'i'),
                    new RegExp(`# TODO ${taskNumber}`, 'i'),
                    new RegExp(`// TODO ${taskNumber}`, 'i'),
                  ];
                  
                  let startIdx = -1;
                  let endIdx = lines.length;
                  
                  // Find the start of this task's code block
                  for (let i = 0; i < lines.length; i++) {
                    const line = lines[i];
                    if (taskPatterns.some(pattern => pattern.test(line))) {
                      startIdx = i;
                      break;
                    }
                  }
                  
                  // If we found a start, look for the next task or end of function/block
                  if (startIdx !== -1) {
                    // Look for the next task's TODO or end of current block
                    for (let i = startIdx + 1; i < lines.length; i++) {
                      const line = lines[i];
                      const nextTaskNumber = taskNumber + 1;
                      const nextTaskPatterns = [
                        new RegExp(`TODO.*${nextTaskNumber}`, 'i'),
                        new RegExp(`TODO.*task.*${nextTaskNumber}`, 'i'),
                        new RegExp(`# TODO ${nextTaskNumber}`, 'i'),
                        new RegExp(`// TODO ${nextTaskNumber}`, 'i'),
                      ];
                      
                      if (nextTaskPatterns.some(pattern => pattern.test(line))) {
                        endIdx = i;
                        break;
                      }
                    }
                    
                    // Extract the relevant code snippet
                    const relevantLines = lines.slice(startIdx, endIdx);
                    return relevantLines.join('\n');
                  }
                  
                  // Fallback: if we can't find task-specific code, show a portion based on task index
                  // Divide code into chunks based on number of tasks
                  const totalTasks = scaffold.todo_list.length;
                  const linesPerTask = Math.ceil(lines.length / totalTasks);
                  const startLine = taskIndex * linesPerTask;
                  const endLine = Math.min(startLine + linesPerTask, lines.length);
                  
                  return lines.slice(startLine, endLine).join('\n');
                };
                
                const codeStructure = getTaskCodeStructure();
                
                return (
                  <div
                    key={taskIndex}
                    className="rounded-2xl border border-gray-200/60 dark:border-gray-800/60 bg-white dark:bg-black p-8 shadow-sm"
                  >
                    <div className="mb-6 flex items-start gap-4">
                      <span className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-blue-600 dark:bg-blue-500 text-sm font-semibold text-white">
                        {taskIndex + 1}
                      </span>
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold tracking-tight text-black dark:text-white mb-2">
                          {task?.title || `Task ${taskIndex + 1}`}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">{task?.description || todo}</p>
                        {task?.estimated_time && (
                          <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">Estimated time: {task.estimated_time}</p>
                        )}
                      </div>
                    </div>

                    <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                      {/* Example Section */}
                      <div className="rounded-xl border border-gray-200/60 dark:border-gray-800/60 bg-gray-50/50 dark:bg-gray-900/50 p-6">
                        <div className="mb-3 flex items-center justify-between">
                          <h4 className="text-sm font-semibold text-black dark:text-white">Example</h4>
                          <span className="text-xs text-gray-500 dark:text-gray-500">({proficientLanguage})</span>
                        </div>
                        {Object.keys(taskConceptExamples).length > 0 ? (
                          <div className="space-y-4">
                            {Object.entries(taskConceptExamples).map(([concept, example], idx) => (
                              <div key={idx} className="space-y-2">
                                <div className="text-xs font-medium text-blue-600 dark:text-blue-400">
                                  {concept}
                                </div>
                                <pre className="text-xs text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed font-mono bg-white dark:bg-black p-3 rounded border border-gray-200 dark:border-gray-800 overflow-x-auto">
                                  {example}
                                </pre>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="flex flex-col items-center justify-center py-8 text-center">
                            <Code2 className="h-10 w-10 text-gray-400 dark:text-gray-600 mb-2" />
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              No examples needed for this task
                            </p>
                          </div>
                        )}
                        {/* Concepts used section */}
                        {taskConcepts.length > 0 && (
                          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-800">
                            <div className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">
                              Concepts used:
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {taskConcepts.map((concept, idx) => (
                                <span
                                  key={idx}
                                  className="text-xs px-2 py-1 rounded bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-800"
                                >
                                  {concept}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Code Structure/Template Section */}
                      <div className="rounded-xl border border-gray-200/60 dark:border-gray-800/60 bg-gray-50/50 dark:bg-gray-900/50 p-6">
                        <h4 className="mb-3 text-sm font-semibold text-black dark:text-white">Code Structure</h4>
                        {codeStructure ? (
                          <div className="space-y-2">
                            <pre className="text-xs text-gray-800 dark:text-gray-300 whitespace-pre-wrap leading-relaxed font-mono bg-white dark:bg-black p-4 rounded-lg border border-gray-200 dark:border-gray-800 overflow-x-auto max-h-[400px] overflow-y-auto">
                              {codeStructure}
                            </pre>
                            <p className="text-xs text-gray-500 dark:text-gray-500 mt-2 italic">
                              Fill in the TODO sections and complete the structure above
                            </p>
                          </div>
                        ) : (
                          <div className="flex flex-col items-center justify-center py-8 text-center">
                            <Code2 className="h-10 w-10 text-gray-400 dark:text-gray-600 mb-2" />
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              Code structure template will appear here
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

