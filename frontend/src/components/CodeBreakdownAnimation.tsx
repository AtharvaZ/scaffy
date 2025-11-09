import { useEffect, useState } from 'react';
import { Loader2, CheckCircle2, Circle, FileText, Type, Lightbulb, Code2, Play } from 'lucide-react';

type Phase = 'input' | 'processing' | 'tasks' | 'editor';

interface Task {
  id: number;
  text: string;
  concepts: string[];
}

export function CodeBreakdownAnimation() {
  const [phase, setPhase] = useState<Phase>('input');
  const [processingStage, setProcessingStage] = useState<'parsing' | 'generating' | 'complete'>('parsing');
  const [tasksCompleted, setTasksCompleted] = useState(0);
  const [tasksTotal, setTasksTotal] = useState(3);
  const [selectedTask, setSelectedTask] = useState(0);
  const [showHint, setShowHint] = useState(false);
  const [hintText, setHintText] = useState('');
  const [hintButtonPressed, setHintButtonPressed] = useState(false);

  const assignmentText = `Create a REST API endpoint that:
- Accepts user input
- Validates the data
- Stores it in a database
- Returns a success response`;

  const tasks: Task[] = [
    { 
      id: 1, 
      text: 'Set up Express router and route handler', 
      concepts: ['Express.js', 'Route Handlers']
    },
    { 
      id: 2, 
      text: 'Implement input validation middleware', 
      concepts: ['Validation', 'Middleware']
    },
    { 
      id: 3, 
      text: 'Create database save operation', 
      concepts: ['Database', 'Async Operations']
    },
  ];

  const codeForTask = `// Task 2: Implement input validation middleware
import { body, validationResult } from 'express-validator';

export const validateUserInput = [
  body('name')
    .trim()
    .isLength({ min: 1, max: 100 })
    .withMessage('Name is required'),
  body('email')
    .isEmail()
    .normalizeEmail()
    .withMessage('Valid email is required'),
  (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }
    next();
  }
];`;

  const hintExample = `Consider what fields require validation. 
What data structure are you expecting in the request body? 
Think about validation rules: email format requirements, 
name length constraints.`;

  useEffect(() => {
    const sequence = async () => {
      // Phase 1: Show assignment input (Create Assignment)
      setPhase('input');
      setProcessingStage('parsing');
      setTasksCompleted(0);
      setShowHint(false);
      setHintButtonPressed(false);
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Phase 2: Show processing progress
      setPhase('processing');
      setProcessingStage('parsing');
      await new Promise(resolve => setTimeout(resolve, 1500));

      setProcessingStage('generating');
      setTasksTotal(3);
      // Simulate progress with slower, more graceful increments
      for (let i = 0; i <= 3; i++) {
        setTasksCompleted(i);
        await new Promise(resolve => setTimeout(resolve, 1500));
      }
      
      setProcessingStage('complete');
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Phase 3: Show task breakdown
      setPhase('tasks');
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Phase 4: Show editor with hints (Code Editor)
      setPhase('editor');
      setSelectedTask(1);
      setShowHint(false);
      setHintButtonPressed(false);
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Highlight Get Hint button as if pressed
      setHintButtonPressed(true);
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Show hint after button press
      setShowHint(true);
      setHintText(hintExample);
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Reset all states before next iteration
      setShowHint(false);
      setHintButtonPressed(false);
      setSelectedTask(0);
      setPhase('input');
      setProcessingStage('parsing');
      setTasksCompleted(0);
      
      // Delay before next iteration
      await new Promise(resolve => setTimeout(resolve, 5000));
      
      // Loop to start again
      sequence();
    };

    const timer = setTimeout(() => sequence(), 1500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="relative w-full h-[600px] bg-white dark:bg-black rounded-xl border border-gray-200/60 dark:border-gray-800/60 overflow-hidden">
      {/* Input Phase */}
      {phase === 'input' && (
        <div className="h-full flex items-center justify-center p-8 animate-fade-in">
          <div className="max-w-2xl w-full">
            <div className="rounded-2xl border border-gray-200/60 dark:border-gray-800/60 bg-white dark:bg-black p-6 shadow-sm">
              <div className="mb-4">
                <h3 className="text-lg font-semibold tracking-tight text-black dark:text-white mb-1">
                  Create Assignment
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Enter your assignment details to get started
                </p>
              </div>
              <div className="space-y-4">
                <div className="flex items-center gap-2 p-1 rounded-lg bg-gray-100 dark:bg-gray-900 border border-gray-200 dark:border-gray-800">
                  <button
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-md text-sm font-medium bg-white dark:bg-gray-800 text-black dark:text-white shadow-sm"
                  >
                    <Type className="h-4 w-4" />
                    Enter Text
                  </button>
                  <button
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-md text-sm font-medium text-gray-600 dark:text-gray-400"
                  >
                    <FileText className="h-4 w-4" />
                    Upload PDF
                  </button>
            </div>
                <div className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg p-4 min-h-[120px]">
              <pre className="text-sm font-mono text-gray-800 dark:text-gray-200 leading-relaxed whitespace-pre-wrap">
                    {assignmentText}
              </pre>
                </div>
                <div className="flex gap-3">
                  <select className="flex-1 px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-black text-sm text-gray-900 dark:text-gray-100">
                    <option>JavaScript</option>
                  </select>
                  <select className="flex-1 px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-black text-sm text-gray-900 dark:text-gray-100">
                    <option>Python</option>
                  </select>
                </div>
                <button className="w-full px-4 py-2.5 rounded-lg bg-gradient-to-r from-blue-600 to-blue-500 text-white text-sm font-medium shadow-md shadow-blue-500/20">
                  Submit Assignment
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Processing Phase */}
      {phase === 'processing' && (
        <div className="h-full flex items-center justify-center p-8 animate-fade-in">
          <div className="max-w-2xl w-full">
            <div className="rounded-lg border border-black/5 dark:border-gray-800/60 bg-white dark:bg-black p-6">
              <div className="space-y-4">
                <div className="text-center mb-6">
                  <Loader2 className="h-10 w-10 animate-spin text-blue-600 dark:text-blue-400 mx-auto mb-3" />
                  <h3 className="text-base font-semibold text-black dark:text-white mb-1">
                    Processing Your Assignment
                  </h3>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    This may take 20-40 seconds depending on assignment complexity
                  </p>
                </div>

                <div className="space-y-3">
                  {/* Parsing Stage */}
                  <div
                    className={`flex items-start gap-3 p-3 rounded-lg transition-all ${
                      processingStage === 'parsing'
                        ? 'bg-blue-50 dark:bg-blue-950/20 border-2 border-blue-200 dark:border-blue-800'
                        : processingStage === 'generating' || processingStage === 'complete'
                        ? 'bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-800'
                        : 'bg-gray-50 dark:bg-gray-900/20 border border-gray-200 dark:border-gray-800'
                    }`}
                  >
                    <div className="flex-shrink-0 mt-0.5">
                      {processingStage === 'parsing' ? (
                        <Loader2 className="h-5 w-5 text-blue-600 dark:text-blue-400 animate-spin" />
                      ) : processingStage === 'generating' || processingStage === 'complete' ? (
                        <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
                      ) : (
                        <Circle className="h-5 w-5 text-gray-400 dark:text-gray-600" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-semibold ${
                        processingStage === 'parsing'
                          ? 'text-blue-900 dark:text-blue-100'
                          : processingStage === 'generating' || processingStage === 'complete'
                          ? 'text-green-900 dark:text-green-100'
                          : 'text-gray-500 dark:text-gray-500'
                      }`}>
                        Parsing Assignment
                      </p>
                      <p className={`text-xs mt-0.5 ${
                        processingStage === 'parsing'
                          ? 'text-blue-700 dark:text-blue-300'
                          : processingStage === 'generating' || processingStage === 'complete'
                          ? 'text-green-700 dark:text-green-300'
                          : 'text-gray-400 dark:text-gray-600'
                      }`}>
                        Breaking down your assignment into tasks...
                      </p>
                    </div>
                  </div>

                  {/* Generating Stage */}
                  <div
                    className={`flex items-start gap-3 p-3 rounded-lg transition-all ${
                      processingStage === 'generating'
                        ? 'bg-blue-50 dark:bg-blue-950/20 border-2 border-blue-200 dark:border-blue-800'
                        : processingStage === 'complete'
                        ? 'bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-800'
                        : 'bg-gray-50 dark:bg-gray-900/20 border border-gray-200 dark:border-gray-800'
                    }`}
                  >
                    <div className="flex-shrink-0 mt-0.5">
                      {processingStage === 'generating' ? (
                        <Loader2 className="h-5 w-5 text-blue-600 dark:text-blue-400 animate-spin" />
                      ) : processingStage === 'complete' ? (
                        <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
                      ) : (
                        <Circle className="h-5 w-5 text-gray-400 dark:text-gray-600" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-semibold ${
                        processingStage === 'generating'
                          ? 'text-blue-900 dark:text-blue-100'
                          : processingStage === 'complete'
                          ? 'text-green-900 dark:text-green-100'
                          : 'text-gray-500 dark:text-gray-500'
                      }`}>
                        Generating Code
                      </p>
                      <p className={`text-xs mt-0.5 ${
                        processingStage === 'generating'
                          ? 'text-blue-700 dark:text-blue-300'
                          : processingStage === 'complete'
                          ? 'text-green-700 dark:text-green-300'
                          : 'text-gray-400 dark:text-gray-600'
                      }`}>
                        Creating starter code ({tasksCompleted}/{tasksTotal} tasks)
                      </p>
                      {processingStage === 'generating' && tasksTotal > 0 && (
                        <div className="mt-2">
                          <div className="h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-blue-600 dark:bg-blue-400 transition-all duration-500 ease-out"
                              style={{ width: `${(tasksCompleted / tasksTotal) * 100}%` }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Complete Stage */}
                  {processingStage === 'complete' && (
                    <div className="flex items-start gap-3 p-3 rounded-lg bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-800">
                      <div className="flex-shrink-0 mt-0.5">
                        <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-green-900 dark:text-green-100">
                          Ready!
                        </p>
                        <p className="text-xs mt-0.5 text-green-700 dark:text-green-300">
                          Your scaffold is ready to use
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tasks Phase */}
      {phase === 'tasks' && (
        <div className="h-full flex items-center justify-center p-8 animate-fade-in">
          <div className="max-w-2xl w-full">
            <div className="rounded-2xl border border-gray-200/60 dark:border-gray-800/60 bg-white dark:bg-black p-6 shadow-sm">
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-black dark:text-white mb-1">
                  Task Breakdown
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Your assignment has been broken down into manageable tasks
                </p>
              </div>
              <div className="space-y-3">
              {tasks.map((task) => (
                <div
                  key={task.id}
                    className="rounded-xl border border-gray-200/60 dark:border-gray-800/60 bg-white dark:bg-black p-4 hover:border-blue-500/50 dark:hover:border-blue-400/50 transition-colors"
                >
                    <div className="flex items-start gap-3">
                  <div className="w-5 h-5 rounded border-2 border-gray-300 dark:border-gray-700 mt-0.5 flex-shrink-0"></div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
                          {task.text}
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {task.concepts.map((concept, idx) => (
                            <span
                              key={idx}
                              className="text-xs px-2 py-1 rounded bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-800"
                            >
                              {concept}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                </div>
              ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Editor Phase */}
      {phase === 'editor' && (
        <div className="h-full grid grid-cols-3 divide-x divide-gray-200/60 dark:divide-gray-800/60 animate-fade-in relative">
          {/* Code Editor */}
          <div className="col-span-2 flex flex-col h-full bg-white dark:bg-black">
            <div className="flex-1 overflow-auto p-4">
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-2">
                <div className="flex gap-1.5">
                    <div className="w-2.5 h-2.5 rounded-full bg-red-500/80"></div>
                    <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/80"></div>
                    <div className="w-2.5 h-2.5 rounded-full bg-green-500/80"></div>
                  </div>
                  <span className="text-xs font-mono text-gray-500 dark:text-gray-400 ml-2">
                    validateUserInput.js
                  </span>
                </div>
              </div>
              <div className="bg-gray-950 dark:bg-black rounded-lg border border-gray-800 dark:border-gray-800 p-4">
                <pre className="text-xs font-mono leading-relaxed">
                <code>
                  {codeForTask.split('\n').map((line, index) => {
                    const isComment = line.trim().startsWith('//');
                      const isKeyword = ['import', 'export', 'const', 'body', 'trim', 'isLength', 'isEmail', 'return', 'if', 'next'].some(k => line.includes(k));
                    
                    return (
                        <div key={index} className="flex items-start gap-3">
                          <span className="text-gray-600 dark:text-gray-700 select-none w-6 text-right font-mono text-xs">
                          {index + 1}
                        </span>
                        <span className={`flex-1 font-mono ${
                          isComment ? 'text-gray-500 dark:text-gray-500' :
                          isKeyword ? 'text-blue-400 dark:text-blue-400' :
                          'text-gray-300 dark:text-gray-300'
                        }`}>
                          {line === '' ? '\u00A0' : line}
                        </span>
                      </div>
                    );
                  })}
                </code>
              </pre>
              </div>
              <div className="flex items-center gap-2 mt-4 relative">
                <button
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-medium transition-all duration-300 ease-out ${
                    hintButtonPressed
                      ? 'bg-blue-100 dark:bg-blue-900 border-blue-300 dark:border-blue-700 text-blue-700 dark:text-blue-300 scale-[0.95] shadow-md'
                      : 'bg-gray-100 dark:bg-gray-900 border-gray-200 dark:border-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-800'
                  }`}
                >
                  <Lightbulb className="h-3 w-3" />
                  Get Hint
                </button>
                <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-100 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 text-xs font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-800">
                  <Code2 className="h-3 w-3" />
                  Examples
                </button>
                <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gradient-to-r from-blue-600 to-blue-500 text-white text-xs font-medium shadow-sm ml-auto">
                  <Play className="h-3 w-3" />
                  Run Tests
                </button>
              </div>
            </div>
          </div>

          {/* Hints Sidebar */}
          <div className="col-span-1 flex flex-col h-full bg-white dark:bg-black border-l border-gray-200/60 dark:border-gray-800/60">
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200/60 dark:border-gray-800/60 flex-shrink-0">
              <div className="flex items-center gap-2">
                <Lightbulb className="h-4 w-4 text-black dark:text-white" />
                <h3 className="text-sm font-semibold tracking-tight text-black dark:text-white">
                  Hints
                </h3>
              </div>
            </div>
            <div className="flex-1 overflow-y-auto px-4 py-4">
              {showHint ? (
                <div className="space-y-3 animate-fade-in" style={{ animationDuration: '0.8s' }}>
                  <div className="rounded-lg p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 animate-slide-in" style={{ animationDuration: '0.6s', animationDelay: '0.2s', animationFillMode: 'both' }}>
                    <p className="text-xs leading-relaxed text-gray-900 dark:text-gray-100">
                      {hintText}
                    </p>
                  </div>
                  <button className="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 text-xs font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-all duration-300">
                    Get Another Hint
                  </button>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-center">
                  <Lightbulb className="h-8 w-8 text-gray-400 dark:text-gray-600 mb-3" />
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    Click "Get Hint" to receive guidance
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
