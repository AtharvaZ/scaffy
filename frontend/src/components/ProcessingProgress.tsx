import { Loader2, CheckCircle2, Circle } from 'lucide-react';

interface ProcessingProgressProps {
  stage: 'parsing' | 'generating' | 'complete';
  tasksTotal?: number;
  tasksCompleted?: number;
}

export function ProcessingProgress({ stage, tasksTotal = 0, tasksCompleted = 0 }: ProcessingProgressProps) {
  const stages = [
    { id: 'parsing', label: 'Parsing Assignment', description: 'Breaking down your assignment into tasks...' },
    { id: 'generating', label: 'Generating Code', description: tasksTotal > 0 ? `Creating starter code (${tasksCompleted}/${tasksTotal} tasks)` : 'Creating starter code for each task...' },
    { id: 'complete', label: 'Ready!', description: 'Your scaffold is ready to use' },
  ];

  const currentStageIndex = stages.findIndex(s => s.id === stage);

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="rounded-lg border border-black/5 dark:border-border bg-white dark:bg-card p-8">
        <div className="space-y-6">
          <div className="text-center mb-8">
            <Loader2 className="h-12 w-12 animate-spin text-black dark:text-primary mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-black dark:text-foreground mb-2">
              Processing Your Assignment
            </h3>
            <p className="text-sm text-gray-600 dark:text-muted-foreground">
              This may take 20-40 seconds depending on assignment complexity
            </p>
          </div>

          {/* Progress Steps */}
          <div className="space-y-4">
            {stages.map((stageItem, index) => {
              const isComplete = index < currentStageIndex;
              const isCurrent = index === currentStageIndex;
              const isPending = index > currentStageIndex;

              return (
                <div
                  key={stageItem.id}
                  className={`flex items-start gap-4 p-4 rounded-lg transition-all ${
                    isCurrent
                      ? 'bg-blue-50 dark:bg-blue-950/20 border-2 border-blue-200 dark:border-blue-800'
                      : isComplete
                      ? 'bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-800'
                      : 'bg-gray-50 dark:bg-gray-900/20 border border-gray-200 dark:border-gray-800'
                  }`}
                >
                  {/* Icon */}
                  <div className="flex-shrink-0 mt-0.5">
                    {isComplete ? (
                      <CheckCircle2 className="h-6 w-6 text-green-600 dark:text-green-400" />
                    ) : isCurrent ? (
                      <Loader2 className="h-6 w-6 text-blue-600 dark:text-blue-400 animate-spin" />
                    ) : (
                      <Circle className="h-6 w-6 text-gray-400 dark:text-gray-600" />
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <p
                      className={`text-sm font-semibold ${
                        isCurrent
                          ? 'text-blue-900 dark:text-blue-100'
                          : isComplete
                          ? 'text-green-900 dark:text-green-100'
                          : 'text-gray-500 dark:text-gray-500'
                      }`}
                    >
                      {stageItem.label}
                    </p>
                    <p
                      className={`text-xs mt-1 ${
                        isCurrent
                          ? 'text-blue-700 dark:text-blue-300'
                          : isComplete
                          ? 'text-green-700 dark:text-green-300'
                          : 'text-gray-400 dark:text-gray-600'
                      }`}
                    >
                      {stageItem.description}
                    </p>

                    {/* Progress bar for generating stage */}
                    {isCurrent && stageItem.id === 'generating' && tasksTotal > 0 && (
                      <div className="mt-3">
                        <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-600 dark:bg-blue-400 transition-all duration-500 ease-out"
                            style={{ width: `${(tasksCompleted / tasksTotal) * 100}%` }}
                          />
                        </div>
                        <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                          {Math.round((tasksCompleted / tasksTotal) * 100)}% complete
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Tip */}
          <div className="mt-6 p-4 bg-yellow-50 dark:bg-yellow-950/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
            <p className="text-xs text-yellow-800 dark:text-yellow-200">
              <strong>💡 Tip:</strong> We're using AI to create personalized starter code for each task. 
              This ensures you get the best learning experience tailored to your background!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

