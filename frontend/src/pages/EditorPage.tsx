import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAppStore } from "../store/useAppStore";
import { CodeEditor } from "../components/CodeEditor";
import { RunButton } from "../components/RunButton";
import { TestResults } from "../components/TestResults";
import { FeedbackCard } from "../components/FeedbackCard";
import { ProgressIndicator } from "../components/ProgressIndicator";
import { SuccessCelebration } from "../components/SuccessCelebration";
import { GetHint } from "../components/GetHint";
import { GetConceptExample } from "../components/GetConceptExample";
import { TodoList } from "../components/TodoList";
import { DarkModeToggle } from "../components/DarkModeToggle";
import { runCode } from "../api/endpoints";
import { safeApiCall } from "../api/client";
import { Button } from "../components/ui/button";
import { ArrowLeft, Lightbulb, Code2 } from "lucide-react";
import type { RunnerResult } from "../types";

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
    // studentId,
    // assignmentId,
    startTime,
    language,
    proficientLanguage,
    //isLoading,
    error,
    addCompletedTask,
    toggleCompletedTask,
    setStudentCode,
    setRunnerResult,
    setIsRunning,
    setFeedback,
    setShowFeedback,
    // incrementAttemptCount,
    // setIsLoading,
    setError,
  } = useAppStore();

  const [showHelpPanel, setShowHelpPanel] = useState(false);
  const [helpMode, setHelpMode] = useState<"hint" | "example">("hint");
  const [autoTriggerQuestion, setAutoTriggerQuestion] = useState<
    string | undefined
  >(undefined);
  const [selectedTaskForExamples, setSelectedTaskForExamples] = useState<number | undefined>(undefined);

  // Redirect if no scaffold
  useEffect(() => {
    if (!scaffold) {
      navigate("/task");
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
        "Failed to run code"
      );

      if (result) {
        // Convert to runner result format that TestResults component expects
        const runnerResult: RunnerResult = {
          exit_code: result.exit_code || 0,
          tests_passed: result.tests_passed || 0,
          tests_failed: result.tests_failed || 0,
          runtime_ms: result.runtime_ms || 0,
          stdout: result.stdout || "",
          stderr: result.stderr || "",
          failed_tests: result.failed_tests || [],
          timeout: result.timeout,
          security_violation: result.security_violation,
        };

        setRunnerResult(runnerResult);

        // If code runs successfully, mark current task as completed
        if (result.tests_passed > 0 && result.tests_failed === 0) {
          addCompletedTask(currentTask);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsRunning(false);
    }
  };

  const handleGetFeedback = () => {
    if (!scaffold || !studentCode || !runnerResult) return;

    // Build error message from runner result
    const errorMessages: string[] = [];

    if (runnerResult.stderr) {
      errorMessages.push(runnerResult.stderr);
    }

    if (runnerResult.failed_tests && runnerResult.failed_tests.length > 0) {
      runnerResult.failed_tests.forEach((test) => {
        if (test.error_message) {
          errorMessages.push(test.error_message);
        }
      });
    }

    // Create a question that includes the error information
    const errorText =
      errorMessages.length > 0
        ? errorMessages.join("\n").substring(0, 500) // Limit error text length
        : "My code has an error and I need help fixing it.";

    const question = `My code has errors when I run it. Here are the error messages:\n\n${errorText}\n\nCan you help me understand what's wrong and how to fix it?`;

    // Open the help panel with hint mode and auto-trigger
    setHelpMode("hint");
    setShowHelpPanel(true);

    // Store the question for the GetHint component to use
    setAutoTriggerQuestion(question);
  };

  const handleContinue = () => {
    setShowFeedback(false);
    setFeedback(null);
  };

  // Keyboard shortcut for running tests
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        e.preventDefault();
        if (!isRunning && scaffold) {
          handleRunTests();
        }
      }
    };

    window.addEventListener("keydown", handleKeyPress);
    return () => window.removeEventListener("keydown", handleKeyPress);
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
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate("/task")}
                className="text-sm"
              >
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Tasks
              </Button>
              <Link to="/" className="flex items-center">
                <span className="text-[15px] font-semibold text-black dark:text-white">
                  Scaffy
                </span>
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
                <p className="text-sm text-red-800 dark:text-red-400">
                  {error}
                </p>
              </div>
            )}

            {/* Progress Indicator */}
            {scaffold && (
              <div className="mb-4">
                <ProgressIndicator
                  totalTasks={scaffold.todo_list.length}
                  completedTasks={completedTasks.size}
                  currentTask={currentTask}
                />
              </div>
            )}

            {/* Main Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column - Code Editor */}
              <div className="lg:col-span-2">
                <div className="mb-6">
                  <CodeEditor
                    initialCode={studentCode}
                    language={language}
                    onChange={setStudentCode}
                  />
                </div>

                {/* Buttons and Test Results in a flex column - no spacing issues */}
                <div className="flex flex-col -mt-2">
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <Button
                        onClick={() => {
                          if (showHelpPanel && helpMode === "hint") {
                            setShowHelpPanel(false);
                          } else {
                            setHelpMode("hint");
                            setShowHelpPanel(true);
                          }
                        }}
                        variant="outline"
                        size="sm"
                        className={`border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-900 ${
                          showHelpPanel && helpMode === "hint"
                            ? "bg-blue-50 dark:bg-blue-900/20 border-blue-500 text-blue-700 dark:text-blue-300"
                            : ""
                        }`}
                      >
                        <Lightbulb className="mr-2 h-4 w-4" />
                        Get Hint
                      </Button>
                      <Button
                        onClick={() => {
                          if (showHelpPanel && helpMode === "example") {
                            setShowHelpPanel(false);
                            setSelectedTaskForExamples(undefined);
                          } else {
                            setHelpMode("example");
                            setShowHelpPanel(true);
                            // Initialize with first task if not already selected
                            if (selectedTaskForExamples === undefined) {
                              setSelectedTaskForExamples(0);
                            }
                          }
                        }}
                        variant="outline"
                        size="sm"
                        className={`border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-900 ${
                          showHelpPanel && helpMode === "example"
                            ? "bg-blue-50 dark:bg-blue-900/20 border-blue-500 text-blue-700 dark:text-blue-300"
                            : ""
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

                  {/* Test Results - appears inline, no extra spacing */}
                  {runnerResult && (
                    <div className="mt-2">
                      <TestResults
                        results={runnerResult}
                        onRequestFeedback={handleGetFeedback}
                      />
                    </div>
                  )}
                </div>
              </div>

              {/* Right Column - Task List */}
              <div className="lg:col-span-1">
                {scaffold && scaffold.todo_list && (
                  <TodoList
                    todos={scaffold.todo_list}
                    currentTask={currentTask}
                    onTaskSelect={(taskIndex: number) => {
                      // Toggle task completion when checkbox is clicked
                      toggleCompletedTask(taskIndex);
                    }}
                    completedTasks={completedTasks}
                    selectedTaskForExamples={selectedTaskForExamples}
                    onTaskSelectForExamples={(taskIndex: number) => {
                      // Only change task selection if example panel is already open
                      if (showHelpPanel && helpMode === "example") {
                        setSelectedTaskForExamples(taskIndex);
                      }
                    }}
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
            {helpMode === "hint" ? (
              <GetHint
                code={studentCode}
                language={language}
                currentTask={currentTask}
                scaffold={scaffold}
                currentTodoIndex={0}
                knownLanguage={proficientLanguage}
                onClose={() => {
                  setShowHelpPanel(false);
                  setAutoTriggerQuestion(undefined);
                }}
                autoTrigger={!!autoTriggerQuestion}
                autoTriggerQuestion={autoTriggerQuestion}
              />
            ) : (
              <GetConceptExample
                language={language}
                currentTask={currentTask}
                scaffold={scaffold}
                knownLanguage={proficientLanguage}
                onClose={() => setShowHelpPanel(false)}
                selectedTaskForExamples={selectedTaskForExamples}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
