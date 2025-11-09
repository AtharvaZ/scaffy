// API Types matching backend schemas

// Task Schema (from backend)
export interface TaskSchema {
  id: number;
  title: string;
  description: string;
  dependencies: number[];
  estimated_time: string;
  concepts: string[];
}

// Task Breakdown Schema (from backend)
export interface TaskBreakdownSchema {
  tasks: TaskSchema[];
  overview: string;
  total_estimated_time: string;
}

// Legacy ParserOutput for compatibility
export interface ParserOutput {
  tasks: TaskSchema[];
  overview: string;
  total_estimated_time: string;
}

// Starter Code Schema (from backend)
export interface StarterCode {
  code_snippet: string;
  instructions: string;
  todos: string[];
  concept_examples?: Record<string, string>;
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

export interface FailedTest {
  test_name: string;
  error_message: string;
  line_number: number;
}

export interface RunnerResult {
  exit_code: number;
  tests_passed: number;
  tests_failed: number;
  failed_tests: FailedTest[];
  runtime_ms: number;
  stdout: string;
  stderr: string;
  timeout?: boolean;
  security_violation?: boolean;
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
  onAssignmentSubmit: (text: string, language: string, proficientLanguage: string) => void;
  loading: boolean;
}

export interface TodoListProps {
  todos: string[];
  currentTask: number;
  onTaskSelect: (index: number) => void;
  completedTasks?: Set<number>;
}

export interface CodeEditorProps {
  initialCode: string;
  language: string;
  onChange: (code: string) => void;
  readOnly?: boolean;
}

export interface RunButtonProps {
  onClick: () => void;
  loading: boolean;
  disabled: boolean;
}

export interface TestResultsProps {
  results: RunnerResult;
  onRequestFeedback: () => void;
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

