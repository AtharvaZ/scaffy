import { CheckCircle2, Circle } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { TodoListProps } from '../types';

export function TodoList({ todos, currentTask, onTaskSelect, completedTasks = new Set() }: TodoListProps) {
  return (
    <div className="rounded-lg border border-black/5 dark:border-border bg-white dark:bg-card p-6 vercel-shadow">
      <h3 className="mb-4 text-sm font-semibold tracking-tight text-black dark:text-foreground">Tasks</h3>
      <ol className="space-y-1">
        {todos.map((todo, index) => {
          const isCompleted = completedTasks.has(index);
          const isCurrent = index === currentTask;
          
          return (
            <li
              key={index}
              onClick={() => onTaskSelect(index)}
              className={cn(
                "flex items-start gap-3 rounded-md p-3 cursor-pointer transition-all duration-150",
                isCurrent && "bg-black/5 dark:bg-muted border border-black/10 dark:border-border",
                !isCurrent && "hover:bg-black/2.5 dark:hover:bg-muted/50"
              )}
            >
              <div className="mt-0.5 flex-shrink-0">
                {isCompleted ? (
                  <CheckCircle2 className="h-4 w-4 text-black dark:text-foreground" />
                ) : (
                  <Circle className="h-4 w-4 text-gray-400 dark:text-muted-foreground" />
                )}
              </div>
              <span className={cn(
                "flex-1 text-sm leading-relaxed",
                isCompleted && "line-through text-gray-500 dark:text-muted-foreground",
                isCurrent && "font-medium text-black dark:text-foreground",
                !isCurrent && !isCompleted && "text-gray-700 dark:text-muted-foreground"
              )}>
                {index + 1}. {todo}
              </span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}

