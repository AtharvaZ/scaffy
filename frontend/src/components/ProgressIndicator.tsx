import type { ProgressProps } from '../types';

export function ProgressIndicator({ totalTasks, completedTasks, currentTask }: ProgressProps) {
  const progress = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;

  return (
    <div className="rounded-lg border border-black/5 bg-white p-3 vercel-shadow max-w-md">
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-600 font-medium">Progress</span>
          <span className="font-semibold text-black">
            {completedTasks} / {totalTasks} tasks complete
          </span>
        </div>
        <div className="h-1.5 w-full overflow-hidden rounded-full bg-gray-100">
          <div
            className="h-full bg-black transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </div>
  );
}

