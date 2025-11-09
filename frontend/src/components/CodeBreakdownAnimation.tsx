import { useEffect, useState, useRef } from 'react';

type Phase = 'assignment' | 'scaffolded' | 'split';

interface Task {
  id: number;
  text: string;
  completed: boolean;
}

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'ai';
}

export function CodeBreakdownAnimation() {
  const [phase, setPhase] = useState<Phase>('assignment');
  const [tasks, setTasks] = useState<Task[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [showTyping, setShowTyping] = useState(false);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  const assignment = `Create a REST API endpoint that:
- Accepts user input
- Validates the data
- Stores it in a database
- Returns a success response`;

  const scaffoldedTasks: Task[] = [
    { id: 1, text: 'Set up Express router and route handler', completed: false },
    { id: 2, text: 'Implement input validation middleware', completed: false },
    { id: 3, text: 'Create database save operation', completed: false },
    { id: 4, text: 'Add error handling and response formatting', completed: false },
  ];

  const codeForTask = `// Task 2: Implement input validation middleware
import { body, validationResult } from 'express-validator';

export const validateUserInput = [
  body('name')
    .trim()
    .isLength({ min: 1, max: 100 })
    .withMessage('Name is required and must be 1-100 characters'),
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

  useEffect(() => {
    const sequence = async () => {
      // Phase 1: Show assignment
      setPhase('assignment');
      setTasks([]);
      setMessages([]);
      setShowTyping(false);
      await new Promise(resolve => setTimeout(resolve, 4000));

      // Phase 2: Show scaffolded tasks
      setPhase('scaffolded');
      setTasks(scaffoldedTasks);
      await new Promise(resolve => setTimeout(resolve, 5000));

      // Phase 3: Show split screen with editor and chat
      setPhase('split');
      await new Promise(resolve => setTimeout(resolve, 2000));

      // User asks question
      setMessages([{
        id: 1,
        text: 'I need help with the validation logic.',
        sender: 'user'
      }]);
      setShowTyping(true);
      await new Promise(resolve => setTimeout(resolve, 2000));

      // AI responds
      setShowTyping(false);
      setMessages(prev => [...prev, {
        id: 2,
        text: 'Consider what fields require validation. What data structure are you expecting in the request body?',
        sender: 'ai'
      }]);
      await new Promise(resolve => setTimeout(resolve, 5000));

      // User responds
      setMessages(prev => [...prev, {
        id: 3,
        text: 'I need to validate name and email fields.',
        sender: 'user'
      }]);
      setShowTyping(true);
      await new Promise(resolve => setTimeout(resolve, 2000));

      // AI responds
      setShowTyping(false);
      setMessages(prev => [...prev, {
        id: 4,
        text: 'Good. Think about validation rules: email format requirements, name length constraints. What validation approach would be most maintainable?',
        sender: 'ai'
      }]);
      await new Promise(resolve => setTimeout(resolve, 5500));

      // User responds
      setMessages(prev => [...prev, {
        id: 5,
        text: 'I could use a validation library like Joi or Zod for this.',
        sender: 'user'
      }]);
      setShowTyping(true);
      await new Promise(resolve => setTimeout(resolve, 2000));

      // AI responds
      setShowTyping(false);
      setMessages(prev => [...prev, {
        id: 6,
        text: 'Excellent approach. Validation libraries provide type safety and clear error messages. Consider where to place the validation middleware in your route handler.',
        sender: 'ai'
      }]);
      await new Promise(resolve => setTimeout(resolve, 6000));

      // Reset and loop
      setMessages([]);
      setShowTyping(false);
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      sequence();
    };

    const timer = setTimeout(() => sequence(), 1500);
    return () => clearTimeout(timer);
  }, []);

  // Auto-scroll chat
  useEffect(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  }, [messages, showTyping]);

  return (
    <div className="relative w-full h-[600px] bg-white dark:bg-black rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
      {/* Assignment Phase */}
      {phase === 'assignment' && (
        <div className="h-full flex items-center justify-center p-12 animate-fade-in">
          <div className="max-w-2xl w-full">
            <div className="mb-6">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
                <span className="text-xs font-medium text-blue-700 dark:text-blue-300">Assignment</span>
              </div>
            </div>
            <div className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg p-8">
              <pre className="text-sm font-mono text-gray-800 dark:text-gray-200 leading-relaxed whitespace-pre-wrap">
                {assignment}
              </pre>
            </div>
          </div>
        </div>
      )}

      {/* Scaffolded Phase */}
      {phase === 'scaffolded' && (
        <div className="h-full flex items-center justify-center p-12 animate-fade-in">
          <div className="max-w-2xl w-full">
            <div className="mb-6">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
                <span className="text-xs font-medium text-green-700 dark:text-green-300">Scaffolded Tasks</span>
              </div>
            </div>
            <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg p-6 space-y-3">
              {tasks.map((task) => (
                <div
                  key={task.id}
                  className="flex items-start gap-3 p-3 rounded-md border border-gray-200 dark:border-gray-800 hover:border-gray-300 dark:hover:border-gray-700 transition-colors"
                >
                  <div className="w-5 h-5 rounded border-2 border-gray-300 dark:border-gray-700 mt-0.5 flex-shrink-0"></div>
                  <span className="text-sm text-gray-900 dark:text-gray-100 flex-1">{task.text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Split Screen Phase */}
      {phase === 'split' && (
        <div className="h-full grid grid-cols-2 divide-x divide-gray-200 dark:divide-gray-800 animate-fade-in">
          {/* Code Editor Side */}
          <div className="flex flex-col h-full bg-gray-950 dark:bg-black">
            <div className="flex items-center justify-between px-4 py-2.5 border-b border-gray-800 dark:border-gray-800 bg-gray-900 dark:bg-gray-950">
              <div className="flex items-center gap-2">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
                  <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
                </div>
                <span className="text-xs font-mono text-gray-400 ml-3">validateUserInput.js</span>
              </div>
              <div className="text-xs text-gray-500 font-mono">JavaScript</div>
            </div>
            
            <div className="flex-1 overflow-auto p-6">
              <pre className="text-sm font-mono leading-relaxed">
                <code>
                  {codeForTask.split('\n').map((line, index) => {
                    const isComment = line.trim().startsWith('//');
                    const isKeyword = ['import', 'export', 'const', 'body', 'trim', 'isLength', 'isEmail', 'normalizeEmail', 'withMessage', 'return', 'if', 'next'].some(k => line.includes(k));
                    
                    return (
                      <div key={index} className="flex items-start gap-4">
                        <span className="text-gray-600 dark:text-gray-700 select-none w-8 text-right font-mono text-xs">
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
          </div>

          {/* Chat Bot Side */}
          <div className="flex flex-col h-full bg-white dark:bg-gray-950">
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-green-500"></div>
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">AI Assistant</span>
              </div>
              <span className="text-xs text-gray-500 dark:text-gray-400">Online</span>
            </div>

            <div ref={messagesContainerRef} className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0 scroll-smooth">
              {messages.length === 0 && (
                <div className="flex items-center justify-center h-full">
                  <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
                    Ask questions about your code...
                  </p>
                </div>
              )}

              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
                >
                  <div
                    className={`max-w-[85%] rounded-lg px-4 py-2.5 ${
                      message.sender === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-700'
                    }`}
                  >
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
                  </div>
                </div>
              ))}

              {showTyping && (
                <div className="flex justify-start animate-fade-in">
                  <div className="bg-gray-100 dark:bg-gray-800 rounded-lg px-4 py-2.5 border border-gray-200 dark:border-gray-700">
                    <div className="flex gap-1.5">
                      <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div className="h-1" />
            </div>

            <div className="border-t border-gray-200 dark:border-gray-800 p-4 bg-gray-50 dark:bg-gray-900">
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  placeholder="Ask about your code..."
                  className="flex-1 px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  disabled
                />
                <button
                  className="px-4 py-2.5 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled
                >
                  Send
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
