import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAppStore } from "../store/useAppStore";
import { AssignmentInput } from "../components/AssignmentInput";
import { ProcessingProgress } from "../components/ProcessingProgress";
import { parseAndScaffold, getConceptExample } from "../api/endpoints";
import { safeApiCall } from "../api/client";
import { Button } from "../components/ui/button";
import { DarkModeToggle } from "../components/DarkModeToggle";
import { ArrowRight, Loader2, Eye, X, Lightbulb } from "lucide-react";

export function TaskPage() {
  const navigate = useNavigate();
  const {
    language,
    proficientLanguage,
    parserOutput,
    scaffold,
    isLoading,
    error,
    setAssignmentText,
    setLanguage,
    setProficientLanguage,
    setExperienceLevel,
    setParserOutput,
    setScaffold,
    setStudentCode,
    setAssignmentId,
    setIsLoading,
    setError,
  } = useAppStore();

  // Check if we already have a scaffold loaded (coming back from editor)
  const [hasSubmitted, setHasSubmitted] = useState(
    !!scaffold && !!parserOutput
  );
  const [progressStage, setProgressStage] = useState<
    "parsing" | "generating" | "complete"
  >("parsing");
  const [progressTasks, setProgressTasks] = useState({
    completed: 0,
    total: 0,
  });

  // Concept examples state
  const [conceptExamples, setConceptExamples] = useState<
    Record<
      string,
      {
        concept: string;
        example_type:
          | "basic_syntax"
          | "intermediate_pattern"
          | "advanced_pattern";
        code_example: string;
        explanation: string;
        comparison_to_known: string | null;
      }
    >
  >({});
  const [loadingExample, setLoadingExample] = useState<string | null>(null);
  const [expandedConcept, setExpandedConcept] = useState<Record<number, string | null>>({});
  const [taskExamples, setTaskExamples] = useState<
    Record<
      number,
      {
        concept: string;
        example_type:
          | "basic_syntax"
          | "intermediate_pattern"
          | "advanced_pattern";
        code_example: string;
        explanation: string;
        comparison_to_known: string | null;
      }
    >
  >({});
  const [loadingTaskExample, setLoadingTaskExample] = useState<number | null>(
    null
  );

  // Update hasSubmitted when scaffold or parserOutput changes
  useEffect(() => {
    if (scaffold && parserOutput && !isLoading) {
      setHasSubmitted(true);
    }
  }, [scaffold, parserOutput, isLoading]);

  const handleAssignmentSubmit = async (
    text: string,
    lang: string,
    proficientLang: string,
    expLevel: string
  ) => {
    setAssignmentText(text);
    setLanguage(lang);
    setProficientLanguage(proficientLang);
    setExperienceLevel(expLevel);
    setIsLoading(true);
    setError(null);
    setProgressStage("parsing");

    try {
      const result = await safeApiCall(
        () =>
          parseAndScaffold(
            text,
            lang,
            proficientLang,
            expLevel,
            (stage, completed, total) => {
              setProgressStage(stage);
              setProgressTasks({ completed, total });
            }
          ),
        "Failed to parse and scaffold assignment"
      );

      if (result) {
        setProgressStage("complete");

        // Convert TaskBreakdownSchema to ParserOutput format for compatibility
        // Flatten files structure into tasks array for backward compatibility
        const allTasks = result.parser_output.files?.flatMap(file => {
          // Handle both simple files (with tasks) and multi-class files (with classes)
          if (file.tasks) {
            return file.tasks;
          } else if (file.classes) {
            return file.classes.flatMap(classObj => classObj.tasks);
          }
          return [];
        }) || [];
        const parserOutput = {
          tasks: allTasks,
          files: result.parser_output.files,
          overview: result.parser_output.overview,
          total_estimated_time: result.parser_output.total_estimated_time,
          // tests are now per-file (in files[].tests), not at top level
        };
        setParserOutput(parserOutput);
        setScaffold(result.scaffold_package);

        // Get the first starter file or use code_snippet
        const initialCode =
          result.scaffold_package.code_snippet ||
          (Object.keys(result.scaffold_package.starter_files).length > 0
            ? Object.values(result.scaffold_package.starter_files)[0]
            : "");
        setStudentCode(initialCode);

        // Generate assignment ID
        const newAssignmentId = `assignment-${Date.now()}`;
        setAssignmentId(newAssignmentId);

        setHasSubmitted(true);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  const handleContinueToEditor = () => {
    navigate("/editor");
  };

  const fetchConceptExample = async (
    concept: string,
    taskDescription: string,
    taskIndex: number
  ) => {
    // If already loaded, just toggle display for this task
    if (conceptExamples[concept]) {
      setExpandedConcept((prev) => ({
        ...prev,
        [taskIndex]: prev[taskIndex] === concept ? null : concept,
      }));
      return;
    }

    setLoadingExample(concept);
    try {
      const result = await safeApiCall(
        () =>
          getConceptExample(
            concept,
            language,
            proficientLanguage,
            taskDescription
          ),
        "Failed to get concept example"
      );

      if (result) {
        setConceptExamples((prev) => ({ ...prev, [concept]: result }));
        setExpandedConcept((prev) => ({ ...prev, [taskIndex]: concept }));
      }
    } catch (error) {
      console.error("Error fetching concept example:", error);
    } finally {
      setLoadingExample(null);
    }
  };

  const fetchTaskExample = async (
    taskIndex: number,
    taskDescription: string,
    concepts: string[]
  ) => {
    if (concepts.length === 0) return;

    setLoadingTaskExample(taskIndex);
    try {
      // Use the first concept as a general example for the task
      const concept = concepts[0];
      const result = await safeApiCall(
        () =>
          getConceptExample(
            concept,
            language,
            proficientLanguage,
            taskDescription
          ),
        "Failed to get task example"
      );

      if (result) {
        setTaskExamples((prev) => ({ ...prev, [taskIndex]: result }));
      }
    } catch (error) {
      console.error("Error fetching task example:", error);
    } finally {
      setLoadingTaskExample(null);
    }
  };

  return (
    <div className="min-h-screen bg-white dark:bg-black">
      {/* Header */}
      <header className="border-b border-gray-200/60 dark:border-gray-800/60 bg-white dark:bg-black">
        <div className="mx-auto max-w-[1440px] px-3 lg:px-4">
          <div className="flex h-16 items-center justify-between">
            <Link to="/" className="flex items-center">
              <span className="text-xl font-semibold text-black dark:text-white">
                Scaffi
              </span>
            </Link>
            <div className="flex items-center gap-8">
              <DarkModeToggle />
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate("/")}
                className="text-sm"
              >
                Home
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-[1440px] px-3 py-8 lg:px-4">
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
              <h2 className="text-xl font-semibold tracking-tight text-black dark:text-white">
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
                const task = parserOutput.tasks?.[taskIndex] || null;
                const taskConcepts = task?.concepts || [];
                const taskConceptExamples =
                  scaffold.task_concept_examples?.[`task_${taskIndex}`] || {};

                // Note: Code structure was previously retrieved here but is now unused
                // as the multi-file editor handles code display differently

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
                        <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                          {task?.description || todo}
                        </p>
                        {task?.estimated_time && (
                          <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                            Estimated time: {task.estimated_time}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="grid grid-cols-1 gap-6">
                      {/* Example Section */}
                      <div className="rounded-xl border border-gray-200/60 dark:border-gray-800/60 bg-gray-50/50 dark:bg-gray-900/50 p-6">
                        <div className="mb-3 flex items-center justify-between">
                          <h4 className="text-sm font-semibold text-black dark:text-white">
                            Example
                          </h4>
                          <span className="text-xs text-gray-500 dark:text-gray-500">
                            ({proficientLanguage})
                          </span>
                        </div>
                        {Object.keys(taskConceptExamples).length > 0 ||
                        taskExamples[taskIndex] ? (
                          <div className="space-y-4">
                            {Object.entries(taskConceptExamples).map(
                              ([concept, example], idx) => (
                                <div key={idx} className="space-y-2">
                                  <div className="text-xs font-medium text-blue-600 dark:text-blue-400">
                                    {concept}
                                  </div>
                                  <pre className="text-xs text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed font-mono bg-white dark:bg-black p-3 rounded border border-gray-200 dark:border-gray-800 overflow-x-auto">
                                    {example}
                                  </pre>
                                </div>
                              )
                            )}
                            {taskExamples[taskIndex] &&
                              loadingTaskExample !== taskIndex && (
                                <div className="space-y-3 text-left">
                                  <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                      <span className="text-xs font-semibold text-blue-700 dark:text-blue-300">
                                        {taskExamples[taskIndex].concept}
                                      </span>
                                      <span className="text-xs px-2 py-0.5 rounded bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300">
                                        {taskExamples[
                                          taskIndex
                                        ].example_type.replace("_", " ")}
                                      </span>
                                    </div>
                                    <Button
                                      onClick={() => {
                                        setTaskExamples((prev) => {
                                          const newExamples = { ...prev };
                                          delete newExamples[taskIndex];
                                          return newExamples;
                                        });
                                      }}
                                      variant="ghost"
                                      size="sm"
                                      className="h-6 w-6 p-0"
                                    >
                                      <X className="h-3 w-3" />
                                    </Button>
                                  </div>
                                  <pre className="text-xs text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed font-mono bg-white dark:bg-black p-3 rounded border border-gray-200 dark:border-gray-800 overflow-x-auto text-left">
                                    {taskExamples[taskIndex].code_example}
                                  </pre>
                                  <div className="text-xs text-gray-600 dark:text-gray-400">
                                    {taskExamples[taskIndex].explanation}
                                  </div>
                                  {taskExamples[taskIndex]
                                    .comparison_to_known && (
                                    <div className="text-xs text-blue-600 dark:text-blue-400 p-2 rounded bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
                                      <strong>Comparison:</strong>{" "}
                                      {
                                        taskExamples[taskIndex]
                                          .comparison_to_known
                                      }
                                    </div>
                                  )}
                                </div>
                              )}
                          </div>
                        ) : (
                          <div className="py-8 space-y-4">
                            <div className="flex flex-col items-center justify-center text-center space-y-4">
                              {taskConcepts.length > 0 && (
                                <Button
                                  onClick={() =>
                                    fetchTaskExample(
                                      taskIndex,
                                      task?.description || todo,
                                      taskConcepts
                                    )
                                  }
                                  disabled={
                                    loadingTaskExample === taskIndex ||
                                    isLoading
                                  }
                                  variant="outline"
                                  size="sm"
                                  className="border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-900"
                                >
                                  {loadingTaskExample === taskIndex ? (
                                    <>
                                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                      Loading...
                                    </>
                                  ) : (
                                    <>
                                      <Lightbulb className="mr-2 h-4 w-4" />
                                      Get Example
                                    </>
                                  )}
                                </Button>
                              )}
                            </div>
                          </div>
                        )}
                        {/* Concepts used section */}
                        {taskConcepts.length > 0 && (
                          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-800">
                            <div className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">
                              Concepts used:
                            </div>
                            <div className="space-y-2">
                              <div className="flex flex-wrap gap-2">
                                {taskConcepts.map((concept, idx) => (
                                  <div
                                    key={idx}
                                    className="flex items-center gap-1"
                                  >
                                    <span className="text-xs px-2 py-1 rounded bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-800">
                                      {concept}
                                    </span>
                                    <button
                                      onClick={() =>
                                        fetchConceptExample(
                                          concept,
                                          task?.description || todo,
                                          taskIndex
                                        )
                                      }
                                      disabled={
                                        loadingExample === concept || isLoading
                                      }
                                      className="p-1 rounded hover:bg-blue-100 dark:hover:bg-blue-900/30 text-blue-600 dark:text-blue-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                      title="Show example"
                                    >
                                      {loadingExample === concept ? (
                                        <Loader2 className="h-3 w-3 animate-spin" />
                                      ) : (
                                        <Eye className="h-3 w-3" />
                                      )}
                                    </button>
                                  </div>
                                ))}
                              </div>

                              {/* Display concept examples */}
                              {expandedConcept[taskIndex] &&
                                conceptExamples[expandedConcept[taskIndex]] && (
                                  <div className="mt-3 p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
                                    <div className="flex items-start justify-between mb-2">
                                      <div className="flex items-center gap-2">
                                        <span className="text-xs font-medium text-blue-600 dark:text-blue-400">
                                          {expandedConcept[taskIndex]}
                                        </span>
                                        <span className="text-xs px-1.5 py-0.5 rounded bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300">
                                          {conceptExamples[
                                            expandedConcept[taskIndex]
                                          ].example_type.replace("_", " ")}
                                        </span>
                                      </div>
                                      <button
                                        onClick={() => setExpandedConcept((prev) => ({ ...prev, [taskIndex]: null }))}
                                        className="p-0.5 rounded hover:bg-blue-200 dark:hover:bg-blue-800 text-blue-600 dark:text-blue-400"
                                      >
                                        <X className="h-3 w-3" />
                                      </button>
                                    </div>
                                    <pre className="text-xs text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed font-mono bg-white dark:bg-black p-3 rounded border border-blue-200 dark:border-blue-800 overflow-x-auto mb-2">
                                      {
                                        conceptExamples[expandedConcept[taskIndex]]
                                          .code_example
                                      }
                                    </pre>
                                    <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                                      {
                                        conceptExamples[expandedConcept[taskIndex]]
                                          .explanation
                                      }
                                    </p>
                                    {conceptExamples[expandedConcept[taskIndex]]
                                      .comparison_to_known && (
                                      <div className="mt-2 pt-2 border-t border-blue-200 dark:border-blue-800">
                                        <p className="text-xs font-medium text-blue-600 dark:text-blue-400 mb-1">
                                          Comparison to {proficientLanguage}:
                                        </p>
                                        <p className="text-xs text-gray-600 dark:text-gray-400">
                                          {
                                            conceptExamples[expandedConcept[taskIndex]]
                                              .comparison_to_known
                                          }
                                        </p>
                                      </div>
                                    )}
                                  </div>
                                )}
                            </div>
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
