import { CheckCircle2, Circle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface TodoChecklistProps {
  todos: string[];
  currentTodoIndex: number;
  onTodoIndexChange: (index: number) => void;
  onTodoToggle?: (index: number) => void;
  completedTodos?: Set<number>;
}

export function TodoChecklist({ todos, currentTodoIndex, onTodoIndexChange, onTodoToggle, completedTodos = new Set() }: TodoChecklistProps) {
  if (!todos || todos.length === 0) {
    return null;
  }

  return (
    <div className="rounded-xl border border-gray-200/60 dark:border-gray-800/60 bg-gray-50/50 dark:bg-gray-900/50 p-4">
      <h4 className="text-sm font-semibold text-black dark:text-white mb-3">TODOs</h4>
      <ol className="space-y-2">
        {todos.map((todo, index) => {
          const isCompleted = completedTodos.has(index);
          const isCurrent = index === currentTodoIndex;
          
          return (
            <li
              key={index}
              className={cn(
                "flex items-start gap-3 rounded-md p-2 transition-all duration-150",
                isCurrent && "bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800",
                !isCurrent && "hover:bg-gray-100 dark:hover:bg-gray-800"
              )}
            >
              <div 
                className="mt-0.5 flex-shrink-0 cursor-pointer"
                onClick={(e) => {
                  e.stopPropagation();
                  if (onTodoToggle) {
                    onTodoToggle(index);
                  }
                }}
              >
                {isCompleted ? (
                  <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400" />
                ) : (
                  <Circle className="h-4 w-4 text-gray-400 dark:text-gray-600" />
                )}
              </div>
              <span 
                onClick={() => onTodoIndexChange(index)}
                className={cn(
                  "flex-1 text-xs leading-relaxed cursor-pointer",
                  isCompleted && "line-through text-gray-500 dark:text-gray-500",
                  isCurrent && "font-medium text-blue-600 dark:text-blue-400",
                  !isCurrent && !isCompleted && "text-gray-700 dark:text-gray-300"
                )}
              >
                {index + 1}. {todo}
              </span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
