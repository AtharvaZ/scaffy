import apiCall from "./client";
import type {
  TaskBreakdownSchema,
  TaskSchema,
  StarterCode,
  HintSchema,
  ParserOutput,
  ScaffoldPackage,
  RunnerResult,
  TestResult,
  TestCase,
} from "../types";

// Health check
export async function checkHealth(): Promise<{
  status: string;
  agents?: any;
  api_key_set?: boolean;
}> {
  return apiCall<{ status: string; agents?: any; api_key_set?: boolean }>(
    "/health",
    { method: "GET" }
  );
}

// Parse assignment - matches backend /parse-assignment endpoint
export async function parseAssignment(
  assignmentText: string,
  targetLanguage: string,
  knownLanguage?: string,
  experienceLevel: string = "intermediate"
): Promise<ParserOutput> {
  return apiCall<ParserOutput>("/parse-assignment", {
    method: "POST",
    body: JSON.stringify({
      assignment_text: assignmentText,
      target_language: targetLanguage,
      known_language: knownLanguage || null,
      experience_level: experienceLevel,
    }),
  });
}

// Generate starter code - matches backend /generate-starter-code endpoint (UPDATED FOR MULTI-FILE)
export async function generateStarterCodeBatch(
  tasks: Array<{
    task_description: string;
    programming_language: string;
    concepts: string[];
    known_language?: string;
    experience_level?: string;
    filename: string;  // NEW: required for multi-file support
  }>
): Promise<{
  tasks: StarterCode[];
  total_tasks: number;
  generation_time: string;
}> {
  return apiCall("/generate-starter-code-batch", {
    method: "POST",
    body: JSON.stringify({ tasks }),
  });
}

// Get hint - matches backend /get-hint endpoint
export async function getHint(
  taskDescription: string,
  concepts: string[],
  studentCode: string,
  question: string,
  previousHints: string[],
  helpCount: number,
  knownLanguage?: string,
  targetLanguage?: string,
  experienceLevel?: string,
  testResults?: TestResult[]  // NEW: Optional test results for test case debugging
): Promise<HintSchema> {
  // Ensure all values are serializable
  const payload = {
    task_description: String(taskDescription || ""),
    concepts: Array.isArray(concepts) ? concepts.map((c) => String(c)) : [],
    student_code: String(studentCode || ""),
    question: String(question || ""),
    previous_hints: Array.isArray(previousHints)
      ? previousHints.map((h) => String(h))
      : [],
    help_count: Number(helpCount) || 1,
    known_language: knownLanguage ? String(knownLanguage) : null,
    target_language: targetLanguage ? String(targetLanguage) : null,
    experience_level: experienceLevel ? String(experienceLevel) : null,
    test_results: testResults || null,  // NEW: Pass test results for analysis
  };

  return apiCall<HintSchema>("/get-hint", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// Run code execution
export async function runCode(
  code: string,
  language: string,
  stdin?: string,
  testCases?: any[]
): Promise<RunnerResult> {
  return apiCall<RunnerResult>("/run-code", {
    method: "POST",
    body: JSON.stringify({
      code,
      language,
      stdin: stdin || null,
      test_cases: testCases || null,
    }),
  });
}

// Generate test cases from user's code
export async function generateTestsFromCode(
  code: string,
  language: string,
  filename: string,
  assignmentDescription?: string
): Promise<{ tests: TestCase[]; message: string }> {
  return apiCall("/generate-tests", {
    method: "POST",
    body: JSON.stringify({
      code,
      language,
      filename,
      assignment_description: assignmentDescription || null,
    }),
  });
}

// Helper function to parse assignment and generate starter code for all tasks (UPDATED FOR MULTI-FILE)
export async function parseAndScaffold(
  assignmentText: string,
  targetLanguage: string,
  knownLanguage?: string,
  experienceLevel: string = "intermediate",
  onProgress?: (
    stage: "parsing" | "generating",
    completed: number,
    total: number
  ) => void
): Promise<{
  parser_output: TaskBreakdownSchema;
  scaffold_package: ScaffoldPackage;
}> {
  // First, parse the assignment
  if (onProgress) onProgress("parsing", 0, 1);
  const taskBreakdown = await parseAssignment(
    assignmentText,
    targetLanguage,
    knownLanguage,
    experienceLevel
  );

  // Extract global template variables from template_structure (for entire assignment)
  const globalTemplateVariables = taskBreakdown.template_structure?.variable_names || [];

  // Extract all tasks from files structure with class, template, and method info
  const allTasksWithFiles: Array<{
    task: TaskSchema,
    filename: string,
    className?: string,
    templateVariables?: string[],
    methodSignatures?: string[]
  }> = [];

  if (taskBreakdown.files) {
    // New format with files
    for (const file of taskBreakdown.files) {
      // Handle both simple files (with tasks) and multi-class files (with classes)
      if (file.tasks) {
        for (const task of file.tasks) {
          allTasksWithFiles.push({
            task,
            filename: file.filename,
            // Use task-specific template vars if present, otherwise use global ones
            templateVariables: task.template_variables || (globalTemplateVariables.length > 0 ? globalTemplateVariables : undefined)
          });
        }
      } else if (file.classes) {
        for (const classObj of file.classes) {
          for (const task of classObj.tasks) {
            allTasksWithFiles.push({
              task,
              filename: file.filename,
              className: classObj.class_name,  // Track which class this task belongs to
              // Use task-specific template vars if present, otherwise use global ones
              templateVariables: task.template_variables || (globalTemplateVariables.length > 0 ? globalTemplateVariables : undefined),
              // Pass method signatures from the class
              methodSignatures: classObj.method_signatures || undefined
            });
          }
        }
      }
    }
  } else if (taskBreakdown.tasks) {
    // Legacy format - single file
    const extensionMap: Record<string, string> = {
      'python': 'py',
      'javascript': 'js',
      'java': 'java',
      'csharp': 'cs',
      'c': 'c',
      'c++': 'cpp',
      'typescript': 'ts'
    };
    const extension = extensionMap[targetLanguage] || 'txt';

    for (const task of taskBreakdown.tasks) {
      allTasksWithFiles.push({
        task,
        filename: `main.${extension}`
      });
    }
  }

  // Build batch request with filename, class_name, template_variables, and method_signatures
  const batchRequest = allTasksWithFiles.map(({ task, filename, className, templateVariables, methodSignatures }) => ({
    task_description: task.description,
    programming_language: targetLanguage,
    concepts: task.concepts,
    known_language: knownLanguage || undefined,
    experience_level: experienceLevel,
    filename: filename,
    class_name: className || undefined,  // Pass class name if present
    template_variables: templateVariables || undefined,  // Pass template vars if present
    method_signatures: methodSignatures || undefined  // Pass method signatures if present
  }));

  // Simulate smooth progress during batch generation
  const totalTasks = allTasksWithFiles.length;
  let currentProgress = 0;

  if (onProgress) onProgress("generating", 0, totalTasks);

  const progressInterval = setInterval(() => {
    if (currentProgress < totalTasks - 1) {
      currentProgress++;
      if (onProgress) onProgress("generating", currentProgress, totalTasks);
    }
  }, 2500); // Update every 2.5 seconds for smooth feel

  try {
    // Single API call for all tasks
    const batchResponse = await generateStarterCodeBatch(batchRequest);
    const starterCodes = batchResponse.tasks;

    // Clear interval and show complete
    clearInterval(progressInterval);
    if (onProgress) onProgress("generating", totalTasks, totalTasks);

    // Verify we have the same number of tasks
    if (starterCodes.length !== allTasksWithFiles.length) {
      console.error(
        `Mismatch: Expected ${allTasksWithFiles.length} starter codes, got ${starterCodes.length}`
      );
    }

    // Debug: Log the todos for each task
    console.log("Task todos mapping:");
    starterCodes.forEach((code, index) => {
      console.log(`task_${index}:`, code.todos);
    });

    // Get language-specific comment syntax
    const getCommentSyntax = (lang: string): { start: string; end: string } => {
      const language = lang.toLowerCase();
      if (language === 'python') {
        return { start: '#', end: '' };
      } else if (['javascript', 'typescript', 'java', 'csharp', 'c#', 'cs', 'c++', 'cpp', 'c', 'go', 'rust', 'swift'].includes(language)) {
        return { start: '//', end: '' };
      } else if (language === 'html' || language === 'xml') {
        return { start: '<!--', end: '-->' };
      } else if (language === 'css') {
        return { start: '/*', end: '*/' };
      }
      // Default to //
      return { start: '//', end: '' };
    };

    const commentSyntax = getCommentSyntax(targetLanguage);

    // Group code snippets by filename
    const fileContents: Record<string, string> = {};
    starterCodes.forEach((code, index) => {
      const filename = code.filename;
      const taskNumber = index + 1;
      const taskTitle = allTasksWithFiles[index].task.title;
      const taskHeader = commentSyntax.end
        ? `${commentSyntax.start} ===== TASK ${taskNumber}: ${taskTitle} ===== ${commentSyntax.end}`
        : `${commentSyntax.start} ===== TASK ${taskNumber}: ${taskTitle} =====`;
      const taskCode = `${taskHeader}\n${code.code_snippet}`;

      if (fileContents[filename]) {
        fileContents[filename] += `\n\n${taskCode}`;
      } else {
        fileContents[filename] = taskCode;
      }
    });

    // For single-file view in editor, combine all files
    const combinedCode = Object.entries(fileContents)
      .map(([filename, content]) => {
        const fileHeader = commentSyntax.end
          ? `${commentSyntax.start} ===== FILE: ${filename} ===== ${commentSyntax.end}`
          : `${commentSyntax.start} ===== FILE: ${filename} =====`;
        return `${fileHeader}\n${content}`;
      })
      .join("\n\n");

    // Flatten all todos from all tasks into one array
    const allTodos = starterCodes.flatMap((code) => code.todos || []);

    // Build scaffold package
    const scaffoldPackage: ScaffoldPackage = {
      todo_list: allTasksWithFiles.map((item) => item.task.description),
      starter_files: fileContents,  // Now organized by actual filenames
      unit_tests: {},
      per_task_hints: {},
      code_snippet: combinedCode, // Combined code for editor
      instructions: starterCodes[0]?.instructions,
      todos: allTodos, // All todos flattened
      concept_examples: starterCodes[0]?.concept_examples,
      task_concepts: allTasksWithFiles.reduce((acc, item, index) => {
        acc[`task_${index}`] = item.task.concepts;
        return acc;
      }, {} as Record<string, string[]>),
      task_concept_examples: starterCodes.reduce((acc, code, index) => {
        // Always set concept_examples, even if undefined
        acc[`task_${index}`] = code.concept_examples || {};
        return acc;
      }, {} as Record<string, Record<string, string>>),
      task_todos: starterCodes.reduce((acc, code, index) => {
        // Ensure we always set todos, even if empty array
        acc[`task_${index}`] = code.todos || [];
        return acc;
      }, {} as Record<string, string[]>),
    };

    console.log("Final task_todos:", scaffoldPackage.task_todos);
    console.log("Files created:", Object.keys(fileContents));

    // Convert taskBreakdown to proper TaskBreakdownSchema format
    const parserOutput: TaskBreakdownSchema = {
      overview: taskBreakdown.overview,
      total_estimated_time: taskBreakdown.total_estimated_time,
      files: taskBreakdown.files || [],
      // tests are now per-file (in files[].tests), not at top level
    };

    // Debug: Check if tests were generated (now per-file)
    const totalTests = parserOutput.files.reduce((sum, file) => sum + (file.tests?.length || 0), 0);
    if (totalTests === 0) {
      console.warn("⚠️ No test cases were generated for this assignment");
      console.warn("This may be due to:");
      console.warn("  - API rate limiting");
      console.warn("  - Test generation failing on backend");
      console.warn("  - Assignment not having testable functions");
      console.warn("Check backend logs for more details");
    } else {
      console.log(`✓ Generated ${totalTests} test cases across ${parserOutput.files.length} file(s)`);
    }

    return {
      parser_output: parserOutput,
      scaffold_package: scaffoldPackage,
    };
  } catch (error) {
    clearInterval(progressInterval);
    throw error;
  }
}
// Extract text from PDF - matches backend /extract-pdf-text endpoint
export async function extractPdfText(file: File): Promise<{
  success: boolean;
  extracted_text: string;
  page_count: number;
  error: string | null;
}> {
  const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
  const url = `${API_BASE_URL}/extract-pdf-text`;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(url, {
      method: "POST",
      body: formData,
      // Don't set Content-Type header - browser will set it with boundary for FormData
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API Error: ${response.status} - ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error(
        `Network error: Cannot connect to ${url}. Check if backend is running and CORS is configured.`
      );
    }
    throw error;
  }
}

// Get concept example - matches backend /get-concept-example endpoint
export async function getConceptExample(
  concept: string,
  programmingLanguage: string,
  knownLanguage?: string,
  context?: string
): Promise<{
  concept: string;
  example_type: "basic_syntax" | "intermediate_pattern" | "advanced_pattern";
  code_example: string;
  explanation: string;
  comparison_to_known: string | null;
}> {
  return apiCall("/get-concept-example", {
    method: "POST",
    body: JSON.stringify({
      concept: concept,
      programming_language: programmingLanguage,
      known_language: knownLanguage || null,
      context: context || null,
    }),
  });
}

// Chat endpoint - uses get-hint endpoint
export async function chatWithAI(
  message: string,
  code: string,
  language: string,
  taskId: string,
  scaffold?: ScaffoldPackage,
  previousHints: string[] = [],
  helpCount: number = 0,
  knownLanguage?: string,
  experienceLevel?: string
): Promise<{ response: string }> {
  // Extract task description and concepts from scaffold if available
  const taskIndex = parseInt(taskId) || 0;
  const taskDescription = scaffold?.todo_list?.[taskIndex] || "Current task";
  // Extract concepts from the scaffold if available
  const concepts: string[] =
    scaffold?.task_concepts?.[`task_${taskIndex}`] || [];

  // Get hint using the backend endpoint
  const hintResult = await getHint(
    taskDescription,
    concepts,
    code,
    message,
    previousHints,
    helpCount + 1, // Increment help count
    knownLanguage,
    language, // target_language
    experienceLevel
  );

  return {
    response:
      hintResult.hint +
      (hintResult.example_code
        ? `\n\nExample:\n${hintResult.example_code}`
        : ""),
  };
}
