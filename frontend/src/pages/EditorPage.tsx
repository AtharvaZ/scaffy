import { useState, useEffect, useRef } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAppStore } from "../store/useAppStore";
import { CodeEditor } from "../components/CodeEditor";
import { RunButton } from "../components/RunButton";
import { FeedbackCard } from "../components/FeedbackCard";
import { ProgressIndicator } from "../components/ProgressIndicator";
import { SuccessCelebration } from "../components/SuccessCelebration";
import { GetHint } from "../components/GetHint";
import { GetConceptExample } from "../components/GetConceptExample";
import { TodoList } from "../components/TodoList";
import { DarkModeToggle } from "../components/DarkModeToggle";
import { TestCaseResults } from "../components/TestCaseResults";
import { TestCasesPanel } from "../components/TestCasesPanel";
import { FileSelector } from "../components/FileSelector";
import { runCode, generateTestsFromCode } from "../api/endpoints";
import { safeApiCall } from "../api/client";
import { Button } from "../components/ui/button";
import { ArrowLeft, Lightbulb, Code2, Trash2, X, Sparkles } from "lucide-react";
import { AutoSaveIndicator } from "../components/SaveIndicator";

export function EditorPage() {
  const navigate = useNavigate();
  const {
    scaffold,
    parserOutput,
    currentTask,
    completedTasks,
    studentCode,
    runnerResult,
    isRunning,
    feedback,
    showFeedback,
    attemptCount,
    startTime,
    language,
    proficientLanguage,
    experienceLevel,
    error,
    currentFile,
    fileSessions,
    addCompletedTask,
    toggleCompletedTask,
    setStudentCode,
    setRunnerResult,
    setIsRunning,
    setFeedback,
    setShowFeedback,
    updateTestCases,
    setError,
    initializeFileSessions,
    saveCurrentFileSession,
    loadFileSession,
    toggleFileSessionTodo,
    updateFileSessionTestResults,
    reset,
  } = useAppStore();

  const [showHelpPanel, setShowHelpPanel] = useState(false);
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [helpMode, setHelpMode] = useState<"hint" | "example">("hint");
  const [autoTriggerQuestion, setAutoTriggerQuestion] = useState<
    string | undefined
  >(undefined);
  const [selectedTaskForExamples, setSelectedTaskForExamples] = useState<number | undefined>(undefined);
  const [lastTestResults, setLastTestResults] = useState<any[] | null>(null);
  const [isGeneratingTests, setIsGeneratingTests] = useState(false);

  // Track previous currentFile to detect changes
  const prevCurrentFileRef = useRef<string | null>(null);

  // Debug: Log when parserOutput changes (specifically when tests change)
  useEffect(() => {
    if (parserOutput?.files) {
      console.log("🔄 parserOutput.files changed:");
      parserOutput.files.forEach(file => {
        console.log(`  - ${file.filename}: ${file.tests?.length || 0} tests`);
      });
    }
  }, [parserOutput?.files]);

  // Redirect if no scaffold
  useEffect(() => {
    if (!scaffold) {
      navigate("/task");
    }
  }, [scaffold, navigate]);

  // Initialize file sessions when scaffold loads
  useEffect(() => {
    if (scaffold && scaffold.starter_files && fileSessions.size === 0) {
      const filenames = Object.keys(scaffold.starter_files);
      if (filenames.length > 0) {
        initializeFileSessions(filenames, scaffold.starter_files);
      }
    }
  }, [scaffold, fileSessions.size, initializeFileSessions]);

  // Sync student code with current file session when currentFile changes
  useEffect(() => {
    // Only sync when user actively switches files (not on initial mount/localStorage restore)
    if (currentFile && prevCurrentFileRef.current !== null && prevCurrentFileRef.current !== currentFile) {
      if (fileSessions.size > 0 && fileSessions.has(currentFile)) {
        const session = fileSessions.get(currentFile);
        if (session && session.code) {
          setStudentCode(session.code);
        }
      }
    }
    // Always update the ref to track the current file
    prevCurrentFileRef.current = currentFile;
  }, [currentFile, fileSessions.size]);

  // Save current file session before page unload
  useEffect(() => {
    const handleBeforeUnload = () => {
      saveCurrentFileSession();
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [saveCurrentFileSession]);

  // Get list of files and filter data for current file
  const files = scaffold?.starter_files ? Object.keys(scaffold.starter_files) : [];
  const hasMultipleFiles = files.length > 1;

  // Get task indices for the current file
  const getCurrentFileTasks = (): number[] => {
    if (!parserOutput?.files || !currentFile) return [];

    const taskIndices: number[] = [];
    let globalTaskIndex = 0;

    for (const file of parserOutput.files) {
      if (file.filename === currentFile) {
        // Found our file - add all its task indices
        // Handle both simple files (tasks) and multi-class files (classes)
        let taskCount = 0;
        if (file.tasks) {
          taskCount = file.tasks.length;
        } else if (file.classes) {
          taskCount = file.classes.reduce((sum, c) => sum + c.tasks.length, 0);
        }
        for (let i = 0; i < taskCount; i++) {
          taskIndices.push(globalTaskIndex + i);
        }
        break;
      }
      // Not our file - skip its tasks
      let fileTaskCount = 0;
      if (file.tasks) {
        fileTaskCount = file.tasks.length;
      } else if (file.classes) {
        fileTaskCount = file.classes.reduce((sum, c) => sum + c.tasks.length, 0);
      }
      globalTaskIndex += fileTaskCount;
    }

    return taskIndices;
  };

  // Filter todos for current file
  const currentFileTodos = (() => {
    if (!hasMultipleFiles || !parserOutput?.files) {
      return scaffold?.todo_list || [];
    }

    const taskIndices = getCurrentFileTasks();
    return taskIndices.map(idx => scaffold?.todo_list[idx] || '');
  })();

  // Get completed tasks mapped to local indices for current file
  const currentFileCompletedTasks = (() => {
    if (!hasMultipleFiles || !parserOutput?.files) {
      return completedTasks;
    }

    const taskIndices = getCurrentFileTasks();
    const localCompleted = new Set<number>();

    taskIndices.forEach((globalIndex, localIndex) => {
      if (completedTasks.has(globalIndex)) {
        localCompleted.add(localIndex);
      }
    });

    return localCompleted;
  })();

  // Get test cases for current file (tests are now per-file)
  const currentFileTests = (() => {
    // For single-file assignments, look for tests in the first file
    if (!hasMultipleFiles && parserOutput?.files?.[0]?.tests) {
      console.log("📋 currentFileTests (single-file):", parserOutput.files[0].tests.length, "tests");
      return parserOutput.files[0].tests;
    }

    // For multi-file assignments, get tests from current file
    if (hasMultipleFiles && parserOutput?.files && currentFile) {
      const fileData = parserOutput.files.find(f => f.filename === currentFile);
      console.log("📋 currentFileTests (multi-file):", fileData?.filename, "-", fileData?.tests?.length || 0, "tests");
      return fileData?.tests || [];
    }

    console.log("📋 currentFileTests: no tests found");
    return [];
  })();

  // Handle file switching
  const handleFileSelect = (filename: string) => {
    if (filename === currentFile) return;

    // Save current file's session
    saveCurrentFileSession();

    // Load the selected file's session
    loadFileSession(filename);
  };

  // Handle code changes - update both global state and file session
  const handleCodeChange = (code: string) => {
    setStudentCode(code);
    if (currentFile && hasMultipleFiles) {
      // Also update the file session's code
      const state = fileSessions.get(currentFile);
      if (state) {
        const sessions = new Map(fileSessions);
        sessions.set(currentFile, { ...state, code });
      }
    }
  };

  const handleRunTests = async () => {
    if (!scaffold || !studentCode) return;

    setIsRunning(true);
    setError(null);

    try {
      // Get test cases for current file
      const testCases = currentFileTests;

      // Run the student's code with test cases
      const result = await safeApiCall(
        () => runCode(studentCode, language, undefined, testCases),
        "Failed to run code"
      );

      if (result) {
        setRunnerResult(result);

        // Save test results for indicators
        if (result.test_results) {
          setLastTestResults(result.test_results);

          // Save test results to current file session
          if (currentFile) {
            updateFileSessionTestResults(currentFile, result.test_results, result);
          }
        }

        // If all tests passed, mark current task as completed
        if (result.tests_passed && result.tests_passed > 0 && result.tests_failed === 0) {
          addCompletedTask(currentTask);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsRunning(false);
    }
  };

  const handleContinue = () => {
    setShowFeedback(false);
    setFeedback(null);
  };

  const handleGenerateTests = async () => {
    console.log("🔄 handleGenerateTests called");
    console.log("  - studentCode length:", studentCode?.length || 0);
    console.log("  - currentFile:", currentFile);
    console.log("  - language:", language);

    if (!studentCode || !currentFile) {
      console.warn("❌ Missing studentCode or currentFile, returning early");
      return;
    }

    setIsGeneratingTests(true);
    setError(null);

    try {
      // Get assignment description from scaffold if available
      const assignmentDescription = parserOutput?.overview || undefined;
      console.log("  - assignmentDescription:", assignmentDescription ? "present" : "none");

      // Generate tests from user's code
      console.log("📡 Calling API to generate tests...");
      const result = await safeApiCall(
        () => generateTestsFromCode(studentCode, language, currentFile, assignmentDescription),
        "Failed to generate tests"
      );

      console.log("📥 API response received:", result);

      if (result && result.tests && result.tests.length > 0) {
        // Update test cases in store
        console.log(`✅ Updating test cases with ${result.tests.length} tests`);
        console.log("  - Tests:", result.tests);
        updateTestCases(result.tests);
        console.log(`✓ Generated ${result.tests.length} test cases`);
      } else {
        console.warn("⚠️ No tests generated:", result?.message);
        setError(result?.message || "No tests were generated. Please check your code.");
      }
    } catch (err) {
      console.error("❌ Error generating tests:", err);
      setError(err instanceof Error ? err.message : "An error occurred generating tests");
    } finally {
      console.log("🏁 handleGenerateTests complete");
      setIsGeneratingTests(false);
    }
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
        <div className="mx-auto max-w-[1600px] px-6 lg:px-8">
          <div className="flex h-20 items-center justify-between">
            <div className="flex items-center gap-6">
              <Button
                variant="ghost"
                size="default"
                onClick={() => navigate("/task")}
                className="text-base -ml-3"
              >
                <ArrowLeft className="mr-2 h-5 w-5" />
                Back to Tasks
              </Button>
              <Link to="/" className="flex items-center">
                <span className="text-xl font-semibold text-black dark:text-white">
                  Scaffi
                </span>
              </Link>
            </div>
            <div className="flex items-center gap-4">
              <AutoSaveIndicator hasUnsavedChanges={false} />
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowClearConfirm(true)}
                className="text-sm text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Clear Progress
              </Button>
              <DarkModeToggle />
            </div>
          </div>
        </div>
      </header>

      {/* Clear Progress Confirmation Dialog */}
      {showClearConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
              Clear All Progress?
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
              This will delete all your code, completed tasks, and test results. This action cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <Button
                variant="outline"
                onClick={() => setShowClearConfirm(false)}
                className="border-gray-200 dark:border-gray-800"
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={() => {
                  reset();
                  localStorage.removeItem('scaffy-app-storage');
                  setShowClearConfirm(false);
                  navigate('/task');
                }}
              >
                Clear Everything
              </Button>
            </div>
          </div>
        </div>
      )}

      <div className="flex h-[calc(100vh-80px)] overflow-hidden">
        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0 transition-all duration-300 overflow-y-auto overflow-x-hidden scroll-smooth" style={{ scrollbarGutter: 'stable' }}>
          <div className="mx-auto max-w-[1600px] w-full px-6 py-8 lg:px-8">
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
              <ProgressIndicator
                totalTasks={scaffold.todo_list.length}
                completedTasks={completedTasks.size}
                currentTask={currentTask}
              />
            )}

            {/* File Selector - only show if multiple files */}
            {hasMultipleFiles && files.length > 0 && (
              <FileSelector
                files={files}
                currentFile={currentFile}
                onFileSelect={handleFileSelect}
                fileHasChanges={(filename) => {
                  const session = fileSessions.get(filename);
                  return session ? session.code !== (scaffold?.starter_files?.[filename] || '') : false;
                }}
                fileContents={(() => {
                  const contents: Record<string, string> = {};
                  files.forEach(filename => {
                    const session = fileSessions.get(filename);
                    contents[filename] = session?.code || scaffold?.starter_files?.[filename] || '';
                  });
                  return contents;
                })()}
                originalStarterFiles={scaffold?.starter_files}
              />
            )}

            {/* Main Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Left Column - Code Editor */}
              <div className="lg:col-span-3">
                <div className="mb-6">
                  <CodeEditor
                    initialCode={studentCode}
                    language={language}
                    onChange={handleCodeChange}
                    scrollToTaskIndex={selectedTaskForExamples}
                    todos={currentFileTodos}
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
                          } else {
                            setHelpMode("example");
                            setShowHelpPanel(true);
                            // Keep the currently selected task, or default to first task
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
                    <div className="flex items-center gap-2">
                      <Button
                        onClick={handleGenerateTests}
                        disabled={isGeneratingTests || !studentCode}
                        size="lg"
                        className="bg-black text-white hover:bg-black/90 transition-all duration-150"
                      >
                        {isGeneratingTests ? (
                          <>
                            <Sparkles className="mr-2 h-4 w-4 animate-spin" />
                            Generating Tests...
                          </>
                        ) : (
                          <>
                            <Sparkles className="mr-2 h-4 w-4" />
                            Generate Tests
                          </>
                        )}
                      </Button>
                      <RunButton
                        onClick={handleRunTests}
                        loading={isRunning}
                        disabled={!studentCode || isRunning}
                      />
                    </div>
                  </div>

                  {/* Compilation Error Section - Show when error exists and all tests have no output */}
                  {runnerResult && runnerResult.error && runnerResult.test_results && runnerResult.test_results.length > 0 && runnerResult.test_results.every(
                    test => !test.actual_output || test.actual_output.trim() === ''
                  ) && (
                    <div className="mt-3 rounded-lg border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20 p-4">
                      <div className="flex items-start gap-3">
                        <div className="flex-shrink-0">
                          <div className="w-8 h-8 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                            <X className="h-5 w-5 text-red-600 dark:text-red-400" />
                          </div>
                        </div>
                        <div className="flex-1">
                          <h3 className="text-base font-semibold text-red-900 dark:text-red-100 mb-2">
                            Compilation Error
                          </h3>
                          <p className="text-sm text-red-800 dark:text-red-300 mb-3">
                            Your code has compilation errors. Fix these before running tests.
                          </p>
                          <div className="bg-red-100 dark:bg-red-950/50 rounded-lg p-3 border border-red-200 dark:border-red-800">
                            <pre className="text-xs font-mono text-red-900 dark:text-red-200 whitespace-pre-wrap overflow-x-auto">
                              {runnerResult.error}
                            </pre>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Test Cases Panel - Shows available test cases BEFORE running OR results AFTER running */}
                  {currentFileTests && currentFileTests.length > 0 && (
                    <div className="mt-3" style={{
                      height: runnerResult && runnerResult.test_results && runnerResult.test_results.length > 0
                        ? (runnerResult.test_results.length > 4 ? '400px' : `${runnerResult.test_results.length * 88 + 80}px`)
                        : '400px'
                    }}>
                      {runnerResult && runnerResult.test_results && runnerResult.test_results.length > 0 ? (
                        <div className="h-full rounded-lg border border-gray-200 dark:border-gray-800">
                          <TestCaseResults
                            testResults={runnerResult.test_results}
                            testsPassedCount={runnerResult.tests_passed}
                            testsFailedCount={runnerResult.tests_failed}
                            onEditTests={() => setRunnerResult(null)}
                          />
                        </div>
                      ) : (
                        <TestCasesPanel
                          testCases={currentFileTests}
                          onTestCasesChange={updateTestCases}
                          testResults={lastTestResults || undefined}
                        />
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Right Column - Task List */}
              <div className="lg:col-span-1">
                {scaffold && currentFileTodos && (
                  <TodoList
                    todos={currentFileTodos}
                    currentTask={currentTask}
                    onTaskSelect={(taskIndex: number) => {
                      // For multi-file mode, toggle the todo in the file session
                      if (hasMultipleFiles && currentFile) {
                        // Get the global task index for this file's local task index
                        const globalTaskIndices = getCurrentFileTasks();
                        const globalTaskIndex = globalTaskIndices[taskIndex];
                        if (globalTaskIndex !== undefined) {
                          toggleFileSessionTodo(currentFile, globalTaskIndex);
                          toggleCompletedTask(globalTaskIndex);
                        }
                      } else {
                        // Single file mode - use standard toggle
                        toggleCompletedTask(taskIndex);
                      }
                    }}
                    completedTasks={currentFileCompletedTasks}
                    selectedTaskForExamples={selectedTaskForExamples}
                    onTaskSelectForExamples={(taskIndex: number) => {
                      // Set the selected task for examples
                      setSelectedTaskForExamples(taskIndex);
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
                experienceLevel={experienceLevel}
                testResults={runnerResult?.test_results}
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
                currentFileTasks={hasMultipleFiles ? getCurrentFileTasks() : undefined}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
