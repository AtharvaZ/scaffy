import apiCall from './client';
import type { TaskBreakdownSchema, StarterCode, HintSchema, ParserOutput, ScaffoldPackage, RunnerResult, FeedbackResponse } from '../types';

// Health check
export async function checkHealth(): Promise<{ status: string; agents?: any; api_key_set?: boolean }> {
  return apiCall<{ status: string; agents?: any; api_key_set?: boolean }>('/health', { method: 'GET' });
}

// Parse assignment - matches backend /parse-assignment endpoint
export async function parseAssignment(
  assignmentText: string,
  targetLanguage: string,
  knownLanguage?: string,
  experienceLevel: string = 'intermediate'
): Promise<TaskBreakdownSchema> {
  return apiCall<TaskBreakdownSchema>('/parse-assignment', {
    method: 'POST',
    body: JSON.stringify({
      assignment_text: assignmentText,
      target_language: targetLanguage,
      known_language: knownLanguage || null,
      experience_level: experienceLevel,
    }),
  });
}

// Generate starter code - matches backend /generate-starter-code endpoint
export async function generateStarterCode(
  taskDescription: string,
  programmingLanguage: string,
  concepts: string[],
  knownLanguage?: string
): Promise<StarterCode> {
  return apiCall<StarterCode>('/generate-starter-code', {
    method: 'POST',
    body: JSON.stringify({
      task_description: taskDescription,
      programming_language: programmingLanguage,
      concepts: concepts,
      known_language: knownLanguage || null,
    }),
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
  targetLanguage?: string
): Promise<HintSchema> {
  return apiCall<HintSchema>('/get-hint', {
    method: 'POST',
    body: JSON.stringify({
      task_description: taskDescription,
      concepts: concepts,
      student_code: studentCode,
      question: question,
      previous_hints: previousHints,
      help_count: helpCount,
      known_language: knownLanguage || null,
      target_language: targetLanguage || null,
    }),
  });
}

// Run code execution
export async function runCode(
  code: string,
  language: string,
  stdin?: string
): Promise<{
  success: boolean;
  output: string;
  error: string;
  exit_code: number;
  execution_time: string;
}> {
  return apiCall('/run-code', {
    method: 'POST',
    body: JSON.stringify({
      code: code,
      language: language,
      stdin: stdin || null,
    }),
  });
}

export async function getFeedback(
  studentCode: string,
  runnerResult: RunnerResult,
  scaffold: ScaffoldPackage,
  studentId: string,
  assignmentId: string,
  taskId: string
): Promise<FeedbackResponse> {
  throw new Error('getFeedback endpoint not available in backend. This feature is not implemented.');
}

// Helper function to parse assignment and generate starter code for all tasks
export async function parseAndScaffold(
  assignmentText: string,
  targetLanguage: string,
  knownLanguage?: string,
  experienceLevel: string = 'intermediate',
  onProgress?: (stage: 'parsing' | 'generating', completed: number, total: number) => void
): Promise<{ parser_output: TaskBreakdownSchema; scaffold_package: ScaffoldPackage }> {
  // First, parse the assignment
  if (onProgress) onProgress('parsing', 0, 1);
  const taskBreakdown = await parseAssignment(assignmentText, targetLanguage, knownLanguage, experienceLevel);
  
  // Then, generate starter code for each task with progress tracking
  const starterCodes: StarterCode[] = [];
  const totalTasks = taskBreakdown.tasks.length;
  
  for (let i = 0; i < taskBreakdown.tasks.length; i++) {
    const task = taskBreakdown.tasks[i];
    if (onProgress) onProgress('generating', i, totalTasks);
    
    const code = await generateStarterCode(
      task.description,
      targetLanguage,
      task.concepts,
      knownLanguage
    );
    starterCodes.push(code);
  }
  
  // Final progress update
  if (onProgress) onProgress('generating', totalTasks, totalTasks);
  
  // Combine into scaffold package format
  const scaffoldPackage: ScaffoldPackage = {
    todo_list: taskBreakdown.tasks.map(task => task.description),
    starter_files: starterCodes.reduce((acc, code, index) => {
      acc[`task_${index + 1}.${targetLanguage === 'python' ? 'py' : 'js'}`] = code.code_snippet;
      return acc;
    }, {} as Record<string, string>),
    unit_tests: {}, // Not available from backend
    per_task_hints: {}, // Not available from backend
    code_snippet: starterCodes[0]?.code_snippet,
    instructions: starterCodes[0]?.instructions,
    todos: starterCodes[0]?.todos, // TODOs for first task
    concept_examples: starterCodes[0]?.concept_examples,
    // Store task concepts for easy access
    task_concepts: taskBreakdown.tasks.reduce((acc, task, index) => {
      acc[`task_${index}`] = task.concepts;
      return acc;
    }, {} as Record<string, string[]>),
    // Store concept examples per task
    task_concept_examples: starterCodes.reduce((acc, code, index) => {
      if (code.concept_examples) {
        acc[`task_${index}`] = code.concept_examples;
      }
      return acc;
    }, {} as Record<string, Record<string, string>>),
    // Store TODOs per task
    task_todos: starterCodes.reduce((acc, code, index) => {
      if (code.todos) {
        acc[`task_${index}`] = code.todos;
      }
      return acc;
    }, {} as Record<string, string[]>),
  };
  
  return {
    parser_output: taskBreakdown,
    scaffold_package: scaffoldPackage,
  };
}

// Extract text from PDF - matches backend /extract-pdf-text endpoint
export async function extractPdfText(file: File): Promise<{
  success: boolean;
  extracted_text: string;
  page_count: number;
  error: string | null;
}> {
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  const url = `${API_BASE_URL}/extract-pdf-text`;
  
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await fetch(url, {
      method: 'POST',
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
      throw new Error(`Network error: Cannot connect to ${url}. Check if backend is running and CORS is configured.`);
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
  example_type: 'basic_syntax' | 'intermediate_pattern' | 'advanced_pattern';
  code_example: string;
  explanation: string;
  comparison_to_known: string | null;
}> {
  return apiCall('/get-concept-example', {
    method: 'POST',
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
  knownLanguage?: string
): Promise<{ response: string }> {
  // Extract task description and concepts from scaffold if available
  const taskIndex = parseInt(taskId) || 0;
  const taskDescription = scaffold?.todo_list?.[taskIndex] || 'Current task';
  // Extract concepts from the scaffold if available
  const concepts: string[] = scaffold?.task_concepts?.[`task_${taskIndex}`] || [];
  
  // Get hint using the backend endpoint
  const hintResult = await getHint(
    taskDescription,
    concepts,
    code,
    message,
    previousHints,
    helpCount + 1, // Increment help count
    knownLanguage,
    language // target_language
  );
  
  return {
    response: hintResult.hint + (hintResult.example_code ? `\n\nExample:\n${hintResult.example_code}` : ''),
  };
}

