import { useEffect, useState } from 'react';
import { Check, Cloud } from 'lucide-react';

export function SaveIndicator() {
  const [showSaved, setShowSaved] = useState(false);

  useEffect(() => {
    // Listen for storage changes
    const handleStorageChange = () => {
      setShowSaved(true);
      setTimeout(() => setShowSaved(false), 2000);
    };

    // Trigger on any state change (Zustand persist saves automatically)
    const interval = setInterval(() => {
      const storage = localStorage.getItem('scaffy-app-storage');
      if (storage) {
        handleStorageChange();
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  if (!showSaved) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 animate-fade-in">
      <div className="flex items-center gap-2 px-4 py-2 bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800 rounded-lg shadow-lg">
        <Check className="h-4 w-4 text-green-600 dark:text-green-400" />
        <span className="text-sm font-medium text-green-700 dark:text-green-300">
          Progress saved
        </span>
      </div>
    </div>
  );
}

export function AutoSaveIndicator({ hasUnsavedChanges }: { hasUnsavedChanges: boolean }) {
  return (
    <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
      <Cloud className="h-3.5 w-3.5" />
      <span>{hasUnsavedChanges ? 'Saving...' : 'All changes saved'}</span>
    </div>
  );
}
