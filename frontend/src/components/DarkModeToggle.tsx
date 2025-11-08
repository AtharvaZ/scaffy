import { Moon, Sun } from 'lucide-react';
import { Button } from './ui/button';
import { useAppStore } from '../store/useAppStore';

export function DarkModeToggle() {
  const { isDarkMode, toggleDarkMode } = useAppStore();

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={toggleDarkMode}
      className="relative"
      aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      {isDarkMode ? (
        <Sun className="h-4 w-4" />
      ) : (
        <Moon className="h-4 w-4" />
      )}
    </Button>
  );
}

