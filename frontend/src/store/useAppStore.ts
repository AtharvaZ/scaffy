import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { AppState, ParserOutput, ScaffoldPackage, RunnerResult, FeedbackResponse } from '../types';

interface AppStore extends AppState {
  // Actions
  setAssignmentText: (text: string) => void;
  setLanguage: (language: string) => void;
  setProficientLanguage: (language: string) => void;
  setParserOutput: (output: ParserOutput | null) => void;
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

export const useAppStore = create<AppStore>()(
  persist(
    (set) => ({
      ...initialState,
      isDarkMode: false,
      
      setAssignmentText: (text) => set({ assignmentText: text }),
      setLanguage: (language) => set({ language }),
      setProficientLanguage: (language) => set({ proficientLanguage: language }),
      setParserOutput: (output) => set({ parserOutput: output }),
      setScaffold: (scaffold) => set({ scaffold }),
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
      reset: () => set({ ...initialState, studentId: generateStudentId() }),
    }),
    {
      name: 'scaffy-app-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        studentCode: state.studentCode,
        studentId: state.studentId,
        assignmentId: state.assignmentId,
        language: state.language,
        proficientLanguage: state.proficientLanguage,
        // Removed completedTasks from persistence - tasks won't be saved between sessions
        isDarkMode: state.isDarkMode,
      }),
      onRehydrateStorage: () => (state) => {
        if (state && Array.isArray(state.completedTasks)) {
          state.completedTasks = new Set(state.completedTasks);
        } else if (state) {
          state.completedTasks = new Set();
        }
        // Apply dark mode on rehydration
        if (state?.isDarkMode) {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
      },
    }
  )
);

