import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { CodeEditor } from '../components/CodeEditor';
import { RunButton } from '../components/RunButton';
import { TestResults } from '../components/TestResults';
import { FeedbackCard } from '../components/FeedbackCard';
import { ProgressIndicator } from '../components/ProgressIndicator';
import { SuccessCelebration } from '../components/SuccessCelebration';
import { GetHint } from '../components/GetHint';
import { GetConceptExample } from '../components/GetConceptExample';
import { TodoChecklist } from '../components/TodoChecklist';
import { DarkModeToggle } from '../components/DarkModeToggle';
import { runCode, getFeedback } from '../api/endpoints';
import { safeApiCall } from '../api/client';
import { Button } from '../components/ui/button';
import { ArrowLeft, Lightbulb, Code2 } from 'lucide-react';

export function EditorPage() {
  const navigate = useNavigate();
  const {
    scaffold,
    currentTask,
    completedTasks,
    studentCode,
    runnerResult,
    isRunning,
    feedback,
    showFeedback,
    attemptCount,
    studentId,
    assignmentId,
    startTime,
    language,
    proficientLanguage,
    isLoading,
    error,
    addCompletedTask,
    setStudentCode,
    setRunnerResult,
    setIsRunning,
    setFeedback,
    setShowFeedback,
    incrementAttemptCount,
    setIsLoading,
    setError,
  } = useAppStore();

  const [showHelpPanel, setShowHelpPanel] = useState(false);
  const [helpMode, setHelpMode] = useState<'hint' | 'example'>('hint');
  const [currentTodoIndex, setCurrentTodoIndex] = useState(0);
  const [completedTodos, setCompletedTodos] = useState<Set<number>>(new Set());

  // Redirect if no scaffold
  useEffect(() => {
    if (!scaffold) {
      navigate('/task');
    }
  }, [scaffold, navigate]);

  const handleRunTests = async () => {
    if (!scaffold || !studentCode) return;

    setIsRunning(true);
    setError(null);

    try {
      // Run the student's code
      const result = await safeApiCall(
        () => runCode(studentCode, language),
        'Failed to run code'
      );

      if (result) {
        // Convert to runner result format that TestResults component expects
        const runnerResult = {
          tests_passed: result.success ? 1 : 0,
          tests_failed: result.success ? 0 : 1,
          runtime_ms: result.execution_time,
          stdout: result.output || '',
          stderr: result.error || '',
          failed_tests: result.success ? [] : [{
            test_name: 'Code Execution',
            error_message: result.error || 'Unknown error',
            line_number: null
          }],
          execution_time: result.execution_time,
          output: result.output,
          errors: result.error ? [result.error] : [],
        };
        
        setRunnerResult(runnerResult);

        // If code runs successfully, mark current task as completed
        if (result.success && !result.error) {
          addCompletedTask(currentTask);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsRunning(false);
    }
  };

  const handleGetFeedback = async () => {
    if (!scaffold || !studentCode) return;

    setIsLoading(true);
    setError(null);

    try {
      // Note: getFeedback endpoint is not available in the backend
      // This is a placeholder for future implementation
      setError('Feedback feature is not yet available. This will be implemented in a future update.');
      // const taskId = `task_${currentTask}`;
      // const result = await safeApiCall(
      //   () =>
      //     getFeedback(
      //       studentCode,
      //       runnerResult,
      //       scaffold,
      //       studentId,
      //       assignmentId,
      //       taskId
      //     ),
      //   'Failed to get feedback'
      // );

      // if (result) {
      //   setFeedback(result);
      //   setShowFeedback(true);
      //   incrementAttemptCount();
      // }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleContinue = () => {
    setShowFeedback(false);
    setFeedback(null);
  };

  // Keyboard shortcut for running tests
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        e.preventDefault();
        if (!isRunning && scaffold) {
          handleRunTests();
        }
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [isRunning, scaffold]);

  const allTestsPassed =
    runnerResult?.tests_failed === 0 &&
    scaffold &&
    completedTasks.size === scaffold.todo_list.length;

  if (!scaffold) {
    return null;
  }

  return (
    <div className="min-h-screen bg-white dark:bg-black">
      {/* Header */}
      <header className="border-b border-gray-200/60 dark:border-gray-800/60 bg-white dark:bg-black">
        <div className="mx-auto max-w-[1440px] px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" onClick={() => navigate('/task')} className="text-sm">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Tasks
              </Button>
              <Link to="/" className="flex items-center">
                <span className="text-[15px] font-semibold text-black dark:text-white">Scaffy</span>
              </Link>
            </div>
            <div className="flex items-center gap-8">
              <DarkModeToggle />
            </div>
          </div>
        </div>
      </header>

      <div className="flex h-[calc(100vh-80px)] overflow-hidden">
        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0 transition-all duration-300">
          <div className="flex-1 overflow-y-auto mx-auto max-w-[1440px] w-full px-6 py-8 lg:px-8">
            {/* Error Display */}
            {error && (
              <div className="mb-6 rounded-lg border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950/20 p-4">
                <p className="text-sm text-red-800 dark:text-red-400">{error}</p>
              </div>
            )}

            {/* Progress Indicator */}
            {scaffold && (() => {
              const currentTodos = scaffold.task_todos?.[`task_${currentTask}`] || scaffold.todos || [];
              const totalTodos = currentTodos.length;
              const completedTodosCount = completedTodos.size;
              
              return totalTodos > 0 ? (
                <div className="mb-4">
                  <ProgressIndicator
                    totalTasks={totalTodos}
                    completedTasks={completedTodosCount}
                    currentTask={currentTodoIndex}
                  />
                </div>
              ) : (
                <div className="mb-4">
                  <ProgressIndicator
                    totalTasks={scaffold.todo_list.length}
                    completedTasks={completedTasks.size}
                    currentTask={currentTask}
                  />
                </div>
              );
            })()}

            {/* Main Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column - Code Editor */}
              <div className="lg:col-span-2 space-y-6">
                <CodeEditor
                  initialCode={studentCode}
                  language={language}
                  onChange={setStudentCode}
                />

                <div className="flex items-center justify-between gap-3 -mt-2">
                  <div className="flex items-center gap-2">
                    <Button
                      onClick={() => {
                        if (showHelpPanel && helpMode === 'hint') {
                          setShowHelpPanel(false);
                        } else {
                          setHelpMode('hint');
                          setShowHelpPanel(true);
                        }
                      }}
                      variant="outline"
                      size="sm"
                      className={`border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-900 ${
                        showHelpPanel && helpMode === 'hint' ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-500 text-blue-700 dark:text-blue-300' : ''
                      }`}
                    >
                      <Lightbulb className="mr-2 h-4 w-4" />
                      Get Hint
                    </Button>
                    <Button
                      onClick={() => {
                        if (showHelpPanel && helpMode === 'example') {
                          setShowHelpPanel(false);
                        } else {
                          setHelpMode('example');
                          setShowHelpPanel(true);
                        }
                      }}
                      variant="outline"
                      size="sm"
                      className={`border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-900 ${
                        showHelpPanel && helpMode === 'example' ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-500 text-blue-700 dark:text-blue-300' : ''
                      }`}
                    >
                      <Code2 className="mr-2 h-4 w-4" />
                      Examples
                    </Button>
                  </div>
                  <RunButton
                    onClick={handleRunTests}
                    loading={isRunning}
                    disabled={!studentCode || isRunning}
                  />
                </div>

                {/* Test Results */}
                {runnerResult && (
                  <div className="mt-6">
                    <TestResults
                      results={runnerResult}
                      onRequestFeedback={handleGetFeedback}
                    />
                  </div>
                )}
              </div>

              {/* Right Column - TODO Checklist */}
              <div className="lg:col-span-1">
                {scaffold && (
                  <TodoChecklist
                    todos={scaffold.task_todos?.[`task_${currentTask}`] || scaffold.todos || []}
                    currentTodoIndex={currentTodoIndex}
                    onTodoIndexChange={(index) => {
                      setCurrentTodoIndex(index);
                    }}
                    onTodoToggle={(index) => {
                      setCompletedTodos(prev => {
                        const newSet = new Set(prev);
                        if (newSet.has(index)) {
                          newSet.delete(index);
                        } else {
                          newSet.add(index);
                        }
                        return newSet;
                      });
                    }}
                    completedTodos={completedTodos}
                  />
                )}
              </div>
            </div>

            {/* Feedback Card */}
            {showFeedback && feedback && (
              <div className="mt-8">
                <FeedbackCard
                  feedback={feedback}
                  attemptNumber={attemptCount}
                  onDismiss={() => setShowFeedback(false)}
                />
              </div>
            )}

            {/* Success Celebration */}
            {allTestsPassed && (
              <SuccessCelebration
                onContinue={handleContinue}
                stats={{
                  totalAttempts: attemptCount,
                  timeSpent: Date.now() - (startTime?.getTime() || Date.now()),
                  testsRun: runnerResult?.tests_passed || 0,
                }}
              />
            )}
          </div>
        </div>

        {/* Help Panel Sidebar */}
        {showHelpPanel && (
          <div className="w-[400px] h-full bg-white dark:bg-black border-l border-gray-200/60 dark:border-gray-800/60 flex-shrink-0">
            {helpMode === 'hint' ? (
              <GetHint
                code={studentCode}
                language={language}
                currentTask={currentTask}
                scaffold={scaffold}
                currentTodoIndex={currentTodoIndex}
                knownLanguage={proficientLanguage}
                onClose={() => setShowHelpPanel(false)}
              />
            ) : (
              <GetConceptExample
                language={language}
                currentTask={currentTask}
                scaffold={scaffold}
                knownLanguage={proficientLanguage}
                onClose={() => setShowHelpPanel(false)}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
}

