import { Button } from './ui/button';
import { Loader2, Play } from 'lucide-react';
import type { RunButtonProps } from '../types';

export function RunButton({ onClick, loading, disabled }: RunButtonProps) {
  return (
    <Button
      onClick={onClick}
      disabled={disabled || loading}
      size="lg"
      className="bg-black text-white hover:bg-black/90 transition-all duration-150"
    >
      {loading ? (
        <>
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          Running Tests...
        </>
      ) : (
        <>
          <Play className="mr-2 h-4 w-4" />
          Run Tests
        </>
      )}
    </Button>
  );
}

