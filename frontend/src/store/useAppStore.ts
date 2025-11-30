import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { AppState, ParserOutput, ScaffoldPackage, RunnerResult, FeedbackResponse } from '../types';

// Per-file session data
export interface FileSession {
  filename: string;
  code: string;
  completedTodos: Set<number>;
  testResults: any[] | null;
  lastRunResult: RunnerResult | null;
}

interface AppStore extends AppState {
  // File session management
  currentFile: string;
  fileSessions: Map<string, FileSession>;

  // Actions
  setAssignmentText: (text: string) => void;
  setLanguage: (language: string) => void;
  setProficientLanguage: (language: string) => void;
  setExperienceLevel: (level: string) => void;
  setParserOutput: (output: ParserOutput | null) => void;
  updateTestCases: (testCases: any[]) => void;
  setScaffold: (scaffold: ScaffoldPackage | null) => void;
  setCurrentTask: (task: number) => void;
  addCompletedTask: (task: number) => void;
  toggleCompletedTask: (task: number) => void;
  setStudentCode: (code: string) => void;
  setHasUnsavedChanges: (hasChanges: boolean) => void;
  setRunnerResult: (result: RunnerResult | null) => void;
  setIsRunning: (isRunning: boolean) => void;
  setFeedback: (feedback: FeedbackResponse | null) => void;
  setShowFeedback: (show: boolean) => void;
  setAttemptCount: (count: number) => void;
  incrementAttemptCount: () => void;
  setAssignmentId: (id: string) => void;
  setIsLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setCompletedTasks: (tasks: Set<number>) => void;
  isDarkMode: boolean;
  toggleDarkMode: () => void;

  // File session actions
  setCurrentFile: (filename: string) => void;
  initializeFileSessions: (filenames: string[], initialCodes: Record<string, string>) => void;
  saveCurrentFileSession: () => void;
  loadFileSession: (filename: string) => void;
  updateFileSessionCode: (filename: string, code: string) => void;
  toggleFileSessionTodo: (filename: string, todoIndex: number) => void;
  updateFileSessionTestResults: (filename: string, testResults: any[], runResult: RunnerResult) => void;

  reset: () => void;
}

const generateStudentId = (): string => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  // Fallback for environments without crypto.randomUUID
  return `student-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

const initialState: AppState = {
  assignmentText: '',
  language: 'python',
  proficientLanguage: 'python',
  experienceLevel: 'intermediate',
  parserOutput: null,
  scaffold: null,
  currentTask: 0,
  completedTasks: new Set(),
  studentCode: '',
  hasUnsavedChanges: false,
  runnerResult: null,
  isRunning: false,
  feedback: null,
  showFeedback: false,
  attemptCount: 0,
  studentId: generateStudentId(),
  assignmentId: '',
  startTime: new Date(),
  isLoading: false,
  error: null,
};

const initialFileSessionState = {
  currentFile: '',
  fileSessions: new Map<string, FileSession>(),
};

export const useAppStore = create<AppStore>()(
  persist(
    (set, get) => ({
      ...initialState,
      ...initialFileSessionState,
      isDarkMode: false,

      setAssignmentText: (text) => set({ assignmentText: text }),
      setLanguage: (language) => set({ language }),
      setProficientLanguage: (language) => set({ proficientLanguage: language }),
      setExperienceLevel: (level) => set({ experienceLevel: level }),
      setParserOutput: (output) => set({ parserOutput: output }),
      updateTestCases: (testCases) => set((state) => {
        console.log("📝 updateTestCases called in store");
        console.log("  - Incoming testCases:", testCases);
        console.log("  - Current file:", state.currentFile);
        console.log("  - parserOutput exists:", !!state.parserOutput);

        if (!state.parserOutput) {
          console.error("❌ No parserOutput in state");
          return {};
        }

        // Handle multi-file structure (tests are per-file)
        if (state.parserOutput.files && state.parserOutput.files.length > 0) {
          console.log(`  - Multi-file mode: ${state.parserOutput.files.length} files`);
          console.log(`  - Files:`, state.parserOutput.files.map(f => f.filename));

          const updatedFiles = state.parserOutput.files.map(file => {
            // Update tests for current file
            if (file.filename === state.currentFile) {
              console.log(`  ✅ Matched current file: ${file.filename}`);
              console.log(`     Old tests: ${file.tests?.length || 0}, New tests: ${testCases.length}`);
              return { ...file, tests: testCases };
            }
            // For single-file assignments (only one file in array)
            if (state.parserOutput!.files!.length === 1) {
              console.log(`  ✅ Single file assignment, updating: ${file.filename}`);
              console.log(`     Old tests: ${file.tests?.length || 0}, New tests: ${testCases.length}`);
              return { ...file, tests: testCases };
            }
            console.log(`  ⏭️  Skipping file: ${file.filename}`);
            return file;
          });

          console.log("  - Updated files structure:", updatedFiles.map(f => ({ filename: f.filename, tests: f.tests?.length })));

          const newState = {
            parserOutput: {
              ...state.parserOutput,
              files: updatedFiles
            }
          };

          console.log("✅ State update complete");
          return newState;
        }

        // Fallback to old structure (legacy support)
        console.log("  - Using legacy test structure");
        return {
          parserOutput: { ...state.parserOutput, tests: testCases }
        };
      }),
      setScaffold: (scaffold) => set({
        scaffold,
        // Reset progress when new scaffold is loaded
        completedTasks: new Set(),
        fileSessions: new Map(),
        currentFile: '',
        studentCode: '',
        runnerResult: null,
        feedback: null,
        showFeedback: false,
        attemptCount: 0,
      }),
      setCurrentTask: (task) => set({ currentTask: task, attemptCount: 0 }),
      addCompletedTask: (task) =>
        set((state) => {
          const newCompleted = new Set(state.completedTasks);
          newCompleted.add(task);
          return { completedTasks: newCompleted };
        }),
      toggleCompletedTask: (task) =>
        set((state) => {
          const newCompleted = new Set(state.completedTasks);
          if (newCompleted.has(task)) {
            newCompleted.delete(task);
          } else {
            newCompleted.add(task);
          }
          return { completedTasks: newCompleted };
        }),
      setCompletedTasks: (tasks) => set({ completedTasks: tasks }),
      setStudentCode: (code) => set({ studentCode: code, hasUnsavedChanges: true }),
      setHasUnsavedChanges: (hasChanges) => set({ hasUnsavedChanges: hasChanges }),
      setRunnerResult: (result) => set({ runnerResult: result }),
      setIsRunning: (isRunning) => set({ isRunning }),
      setFeedback: (feedback) => set({ feedback }),
      setShowFeedback: (show) => set({ showFeedback: show }),
      setAttemptCount: (count) => set({ attemptCount: count }),
      incrementAttemptCount: () => set((state) => ({ attemptCount: state.attemptCount + 1 })),
      setAssignmentId: (id) => set({ assignmentId: id }),
      setIsLoading: (loading) => set({ isLoading: loading }),
      setError: (error) => set({ error }),
      toggleDarkMode: () => {
        set((state) => {
          const newDarkMode = !state.isDarkMode;
          // Apply dark class to document root
          if (newDarkMode) {
            document.documentElement.classList.add('dark');
          } else {
            document.documentElement.classList.remove('dark');
          }
          return { isDarkMode: newDarkMode };
        });
      },

      // File session management actions
      setCurrentFile: (filename) => set({ currentFile: filename }),

      initializeFileSessions: (filenames, initialCodes) => {
        const sessions = new Map<string, FileSession>();
        filenames.forEach((filename) => {
          sessions.set(filename, {
            filename,
            code: initialCodes[filename] || '',
            completedTodos: new Set<number>(),
            testResults: null,
            lastRunResult: null,
          });
        });
        const firstFile = filenames[0] || '';
        set({
          fileSessions: sessions,
          currentFile: firstFile,
          studentCode: initialCodes[firstFile] || '',
        });
      },

      saveCurrentFileSession: () => {
        const state = get();
        if (!state.currentFile) return;

        const sessions = new Map(state.fileSessions);
        const currentSession = sessions.get(state.currentFile);
        if (currentSession) {
          sessions.set(state.currentFile, {
            ...currentSession,
            code: state.studentCode,
            completedTodos: new Set(state.completedTasks),
            testResults: state.runnerResult?.test_results || null,
            lastRunResult: state.runnerResult,
          });
          set({ fileSessions: sessions });
        }
      },

      loadFileSession: (filename) => {
        const state = get();
        const session = state.fileSessions.get(filename);
        if (session) {
          set({
            currentFile: filename,
            studentCode: session.code,
            // Don't replace completedTasks - keep it global for progress bar
            runnerResult: session.lastRunResult,
          });
        }
      },

      updateFileSessionCode: (filename, code) => {
        const state = get();
        const sessions = new Map(state.fileSessions);
        const session = sessions.get(filename);
        if (session) {
          sessions.set(filename, { ...session, code });
          set({ fileSessions: sessions });
        }
      },

      toggleFileSessionTodo: (filename, todoIndex) => {
        const state = get();
        const sessions = new Map(state.fileSessions);
        const session = sessions.get(filename);
        if (session) {
          const newCompletedTodos = new Set(session.completedTodos);
          if (newCompletedTodos.has(todoIndex)) {
            newCompletedTodos.delete(todoIndex);
          } else {
            newCompletedTodos.add(todoIndex);
          }
          sessions.set(filename, { ...session, completedTodos: newCompletedTodos });
          set({ fileSessions: sessions });
        }
      },

      updateFileSessionTestResults: (filename, testResults, runResult) => {
        const state = get();
        const sessions = new Map(state.fileSessions);
        const session = sessions.get(filename);
        if (session) {
          sessions.set(filename, {
            ...session,
            testResults,
            lastRunResult: runResult,
          });
          set({ fileSessions: sessions });
        }
      },

      reset: () => set({ ...initialState, ...initialFileSessionState, studentId: generateStudentId() }),
    }),
    {
      name: 'scaffy-app-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        // User info
        studentCode: state.studentCode,
        studentId: state.studentId,
        assignmentId: state.assignmentId,

        // Assignment details
        assignmentText: state.assignmentText,
        language: state.language,
        proficientLanguage: state.proficientLanguage,
        experienceLevel: state.experienceLevel,

        // Generated content - save the full parser output and scaffold
        parserOutput: state.parserOutput,
        scaffold: state.scaffold,

        // Progress tracking
        currentTask: state.currentTask,
        completedTasks: Array.from(state.completedTasks), // Convert Set to Array for JSON

        // Test results
        runnerResult: state.runnerResult,

        // Multi-file support
        currentFile: state.currentFile,
        fileSessions: Array.from(state.fileSessions.entries()).map(([filename, session]) => ({
          filename,
          code: session.code,
          completedTodos: Array.from(session.completedTodos), // Convert Set to Array
          testResults: session.testResults,
          lastRunResult: session.lastRunResult,
        })),

        // UI preferences
        isDarkMode: state.isDarkMode,

        // Timestamp for data freshness
        lastSaved: Date.now(),
      }),
      onRehydrateStorage: () => (state) => {
        if (!state) return;

        // Convert completedTasks array back to Set
        if (Array.isArray(state.completedTasks)) {
          state.completedTasks = new Set(state.completedTasks);
        } else {
          state.completedTasks = new Set();
        }

        // Convert fileSessions array back to Map
        if (Array.isArray(state.fileSessions)) {
          const sessionsMap = new Map<string, FileSession>();
          state.fileSessions.forEach((session: any) => {
            sessionsMap.set(session.filename, {
              ...session,
              completedTodos: new Set(session.completedTodos || []),
            });
          });
          state.fileSessions = sessionsMap;
        } else {
          state.fileSessions = new Map();
        }

        // Apply dark mode on rehydration
        if (state.isDarkMode) {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }

        console.log('📦 Restored data from localStorage:', {
          assignmentId: state.assignmentId,
          language: state.language,
          tasksCount: state.scaffold?.todo_list?.length || 0,
          filesCount: state.fileSessions.size,
          completedTasks: state.completedTasks.size,
        });
      },
    }
  )
);

