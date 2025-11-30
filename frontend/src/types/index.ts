// API Types matching backend schemas

// Task Schema (from backend)
export interface TaskSchema {
  id: number;
  title: string;
  description: string;
  dependencies: number[];
  estimated_time: string;
  concepts: string[];
  template_variables?: string[];  // Variable names from template to preserve
}

// Class Schema for multi-class files
export interface ClassSchema {
  class_name: string;
  purpose: string;
  tasks: TaskSchema[];
  method_signatures?: string[];  // Method names/signatures to preserve from template
}

// NEW: File Schema for multi-file support (updated for multi-class and per-file tests)
export interface FileSchema {
  filename: string;
  purpose: string;
  tasks?: TaskSchema[] | null;  // For simple files
  classes?: ClassSchema[] | null;  // For multi-class files
  tests?: TestCase[] | null;  // Per-file test cases
}

// Test Case Schema (from backend)
export interface TestCase {
  test_name: string;
  function_name: string;
  input_data: string;
  expected_output: string;
  description: string;
  test_type: "normal" | "edge" | "error";
}

// Template Structure Schema (from backend)
export interface TemplateStructure {
  has_template: boolean;
  variable_names: string[];
  class_names: string[];
  method_signatures?: string[];
}

// Task Breakdown Schema (from backend) - UPDATED FOR MULTI-FILE
export interface TaskBreakdownSchema {
  overview: string;
  total_estimated_time: string;
  template_structure?: TemplateStructure;  // Global template info
  files: FileSchema[];  // Changed from: tasks: TaskSchema[]
  // tests are now per-file (in FileSchema.tests), not at top level
}

// Legacy ParserOutput for compatibility - keeping both formats
export interface ParserOutput {
  tasks?: TaskSchema[];  // Legacy format
  files?: FileSchema[];  // New format
  overview: string;
  total_estimated_time: string;
  template_structure?: TemplateStructure;  // Template info
  tests?: TestCase[];
}

// Starter Code Schema (from backend) - UPDATED FOR MULTI-FILE
export interface StarterCode {
  code_snippet: string;
  instructions: string;
  todos: string[];
  concept_examples?: Record<string, string>;
  filename: string;  // NEW: which file this task belongs to
}

// Scaffold Package (adapted from StarterCode for compatibility)
export interface ScaffoldPackage {
  todo_list: string[];
  starter_files: Record<string, string>;
  unit_tests: Record<string, string>;
  per_task_hints: Record<string, string[]>;
  code_snippet?: string;
  instructions?: string;
  todos?: string[]; // TODOs from starter code for current task
  concept_examples?: Record<string, string>;
  task_concepts?: Record<string, string[]>; // Task concepts indexed by task ID
  task_concept_examples?: Record<string, Record<string, string>>; // Concept examples per task
  task_todos?: Record<string, string[]>; // TODOs per task indexed by task ID
}

// Hint Schema (from backend)
export interface HintSchema {
  hint: string;
  hint_type: string;
  example_code?: string;
}

// Test Result (from backend)
export interface TestResult {
  test_name: string;
  function_name?: string;  // Function being tested
  passed: boolean;
  input_data: string;
  expected_output: string;
  actual_output: string;
  error?: string;
}

export interface FailedTest {
  test_name: string;
  error_message: string;
  line_number: number;
}

export interface RunnerResult {
  success: boolean;
  output: string;
  error: string;
  exit_code: number;
  execution_time: string;
  test_results?: TestResult[];
  tests_passed?: number;
  tests_failed?: number;
}

export interface FeedbackResponse {
  diagnosis: string;
  explanation: string;
  small_fix: string;
  next_hint: string;
  confidence: number;
  line_numbers?: number[];
}

// Component Props Types

export interface AssignmentInputProps {
  onAssignmentSubmit: (text: string, language: string, proficientLanguage: string, experienceLevel: string) => void;
  loading: boolean;
}

export interface TodoListProps {
  todos: string[];
  currentTask: number;
  onTaskSelect: (index: number) => void;
  completedTasks?: Set<number>;
  selectedTaskForExamples?: number;
  onTaskSelectForExamples?: (index: number) => void;
}

export interface CodeEditorProps {
  initialCode: string;
  language: string;
  onChange: (code: string) => void;
  readOnly?: boolean;
  scrollToTaskIndex?: number;
  todos?: string[];
}

export interface RunButtonProps {
  onClick: () => void;
  loading: boolean;
  disabled: boolean;
}

export interface FeedbackCardProps {
  feedback: FeedbackResponse;
  attemptNumber: number;
  onDismiss: () => void;
}

export interface ProgressProps {
  totalTasks: number;
  completedTasks: number;
  currentTask: number;
}

export interface SuccessProps {
  onContinue: () => void;
  stats: {
    totalAttempts: number;
    timeSpent: number;
    testsRun: number;
  };
}

// App State Type
export interface AppState {
  // Assignment
  assignmentText: string;
  language: string;
  proficientLanguage: string;
  experienceLevel: string;
  parserOutput: ParserOutput | null;
  
  // Scaffold
  scaffold: ScaffoldPackage | null;
  currentTask: number;
  completedTasks: Set<number>;
  
  // Code
  studentCode: string;
  hasUnsavedChanges: boolean;
  
  // Execution
  runnerResult: RunnerResult | null;
  isRunning: boolean;
  
  // Feedback
  feedback: FeedbackResponse | null;
  showFeedback: boolean;
  attemptCount: number;
  
  // Session
  studentId: string;
  assignmentId: string;
  startTime: Date;
  
  // UI
  isLoading: boolean;
  error: string | null;
}

