import { useState, useRef, useEffect } from 'react';
import { Button } from './ui/button';
import { X, Send, Bot, User } from 'lucide-react';
import { Textarea } from './ui/textarea';
import { chatWithAI } from '../api/endpoints';
import { safeApiCall } from '../api/client';
import type { ScaffoldPackage } from '../types';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatBotProps {
  code: string;
  language: string;
  currentTask: number;
  scaffold?: ScaffoldPackage;
  currentTodoIndex?: number;
  onTodoIndexChange?: (index: number) => void;
  onClose: () => void;
}

export function ChatBot({ code, language, currentTask, scaffold, currentTodoIndex = 0, onTodoIndexChange, onClose }: ChatBotProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: `Hi! I'm here to help you with your code. I can see you're working on task ${currentTask + 1} in ${language}. Ask me anything about your code!`,
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [previousHints, setPreviousHints] = useState<string[]>([]);
  const [helpCount, setHelpCount] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    // Get current TODO if available
    const todos = scaffold?.task_todos?.[`task_${currentTask}`] || scaffold?.todos || [];
    const currentTodo = todos[currentTodoIndex] || null;
    
    // Always include current TODO in the question if available (as per spec)
    let questionText = input.trim();
    if (currentTodo) {
      questionText = `I'm stuck on: ${currentTodo}. ${questionText}`;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const userInput = input.trim();
    setInput('');
    setIsLoading(true);

    try {
      // Try to use the chat API endpoint (which uses get-hint backend endpoint)
      // Pass the question with current TODO included
      const result = await safeApiCall(
        () => chatWithAI(questionText, code, language, currentTask.toString(), scaffold, previousHints, helpCount),
        'Failed to get AI response'
      );

      if (result && result.response) {
        const aiResponse: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: result.response,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, aiResponse]);
        // Track this hint for future requests
        setPreviousHints((prev) => [...prev, result.response]);
        setHelpCount((prev) => prev + 1);
      } else {
        // Fallback to rule-based responses if API is not available
        const fallbackResponse = generateFallbackResponse(userInput, code, language, currentTask);
        const aiResponse: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: fallbackResponse,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, aiResponse]);
      }
    } catch (error) {
      // Fallback to rule-based responses on error
      const fallbackResponse = generateFallbackResponse(userInput, code, language, currentTask);
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: fallbackResponse,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const generateFallbackResponse = (userQuery: string, currentCode: string, lang: string, task: number): string => {
    const query = userQuery.toLowerCase();
    
    // Analyze code context
    const hasFunctions = currentCode.includes('def ') || currentCode.includes('function ') || currentCode.includes('public ');
    
    // Rule-based responses with code context
    if (query.includes('error') || query.includes('bug') || query.includes('wrong') || query.includes('not working')) {
      let suggestions = `Looking at your code for task ${task + 1}, here are some things to check:\n\n`;
      if (lang === 'python') {
        suggestions += `• Check indentation (Python is strict about this)\n`;
        suggestions += `• Ensure all colons (:) are present after if/for/while/def statements\n`;
        suggestions += `• Verify variable names are spelled correctly\n`;
        suggestions += `• Make sure you're returning values if needed\n`;
      } else if (lang === 'javascript') {
        suggestions += `• Check for missing semicolons or brackets\n`;
        suggestions += `• Ensure proper function syntax\n`;
        suggestions += `• Verify variable declarations (let/const/var)\n`;
      }
      return suggestions;
    }
    
    if (query.includes('syntax') || query.includes('how to') || query.includes('how do')) {
      if (lang === 'python') {
        return `Here's Python syntax help for task ${task + 1}:\n\n` +
               `• Functions: def function_name(param):\n` +
               `• Conditionals: if condition:\n` +
               `• Loops: for item in items: or while condition:\n` +
               `• Returns: return value\n\n` +
               `Would you like help with a specific syntax element?`;
      } else if (lang === 'javascript') {
        return `Here's JavaScript syntax help for task ${task + 1}:\n\n` +
               `• Functions: function name(param) { } or const name = (param) => { }\n` +
               `• Conditionals: if (condition) { }\n` +
               `• Loops: for (let i = 0; i < n; i++) { } or while (condition) { }\n` +
               `• Returns: return value;\n\n` +
               `Would you like help with a specific syntax element?`;
      }
    }
    
    if (query.includes('task') || query.includes('todo') || query.includes('what should')) {
      return `You're working on task ${task + 1}. ` +
             `Focus on implementing the specific requirements for this task. ` +
             `Make sure your code matches the expected structure and handles edge cases. ` +
             `${hasFunctions ? 'I can see you have functions defined - make sure they return the correct values.' : 'Consider what functions or logic you need to implement.'}`;
    }
    
    if (query.includes('test') || query.includes('run') || query.includes('execute')) {
      return `To test your code, click the "Run Tests" button below the editor. ` +
             `This will execute your code against the test cases and show you which tests pass or fail. ` +
             `I can help you fix any issues that come up in the test results.`;
    }
    
    if (query.includes('help') || query.includes('stuck') || query.includes('hint')) {
      return `I'm here to help! I can see your code for task ${task + 1} in ${lang}. ` +
             `I can help you with:\n\n` +
             `• Debugging errors\n` +
             `• Syntax questions\n` +
             `• Logic and algorithm help\n` +
             `• Best practices\n\n` +
             `What specific part would you like help with?`;
    }
    
    // Default response with code context
    return `I understand you're asking about "${userQuery}". ` +
           `Based on your code for task ${task + 1} in ${lang}, I can help you with syntax, logic, debugging, or best practices. ` +
           `${hasFunctions ? 'I can see you have functions in your code - would you like help with any of them?' : 'What specific part would you like help with?'}`;
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="h-full w-full bg-white dark:bg-background border-l border-black/10 dark:border-border flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-black/5 dark:border-border flex-shrink-0">
        <div className="flex items-center gap-2">
          <Bot className="h-4 w-4 text-black dark:text-foreground" />
          <h3 className="text-sm font-semibold tracking-tight text-black dark:text-foreground">AI Assistant</h3>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose} className="h-7 w-7">
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {message.role === 'assistant' && (
                <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-black dark:bg-primary">
                  <Bot className="h-4 w-4 text-white" />
                </div>
              )}
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  message.role === 'user'
                    ? 'bg-black dark:bg-primary text-white dark:text-primary-foreground'
                    : 'bg-gray-50 dark:bg-muted text-gray-900 dark:text-foreground border border-black/5 dark:border-border'
                }`}
              >
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
              </div>
              {message.role === 'user' && (
                <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-gray-200 dark:bg-muted">
                  <User className="h-4 w-4 text-gray-700 dark:text-foreground" />
                </div>
              )}
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-black dark:bg-primary">
                <Bot className="h-4 w-4 text-white" />
              </div>
              <div className="bg-gray-50 dark:bg-muted border border-black/5 dark:border-border rounded-lg p-3">
                <div className="flex gap-1">
                  <div className="h-2 w-2 bg-gray-400 dark:bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="h-2 w-2 bg-gray-400 dark:bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="h-2 w-2 bg-gray-400 dark:bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

      {/* Input */}
      <div className="px-4 py-3 border-t border-black/5 dark:border-border flex-shrink-0 bg-white dark:bg-background">
        <div className="flex gap-2">
          <Textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Ask me anything about your code..."
            className="resize-none border-black/10 dark:border-border focus:border-black/20 dark:focus:border-border focus:ring-0 min-h-[60px] max-h-[120px] text-sm bg-white dark:bg-background text-black dark:text-foreground"
            rows={2}
            disabled={isLoading}
          />
          <Button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="bg-black text-white hover:bg-black/90 dark:bg-primary dark:text-primary-foreground dark:hover:bg-primary/90 h-[60px] px-4 flex-shrink-0"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <p className="text-xs text-gray-500 dark:text-muted-foreground mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}

