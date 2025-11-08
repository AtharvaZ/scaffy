import { useEffect } from 'react';
import confetti from 'canvas-confetti';
import { Button } from './ui/button';
import { Trophy } from 'lucide-react';
import type { SuccessProps } from '../types';

export function SuccessCelebration({ onContinue, stats }: SuccessProps) {
  useEffect(() => {
    // Trigger confetti animation
    const duration = 3000;
    const animationEnd = Date.now() + duration;
    const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };

    function randomInRange(min: number, max: number) {
      return Math.random() * (max - min) + min;
    }

    const interval = setInterval(() => {
      const timeLeft = animationEnd - Date.now();

      if (timeLeft <= 0) {
        return clearInterval(interval);
      }

      const particleCount = 50 * (timeLeft / duration);
      confetti({
        ...defaults,
        particleCount,
        origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
      });
      confetti({
        ...defaults,
        particleCount,
        origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
      });
    }, 250);
  }, []);

  const formatTime = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    return `${minutes}m ${seconds % 60}s`;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/80 backdrop-blur-sm">
      <div className="w-full max-w-md animate-slideIn rounded-lg border border-black/5 bg-white p-8 vercel-shadow-lg">
        <div className="text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-black">
            <Trophy className="h-8 w-8 text-white" />
          </div>
          <h2 className="mb-2 text-2xl font-semibold tracking-tight text-black">Congratulations! 🎉</h2>
          <p className="mb-6 text-sm text-gray-600">
            All tests passed! You've successfully completed the assignment
          </p>
        </div>
        <div className="mb-6 space-y-3 rounded-lg border border-black/5 bg-gray-50 p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Total Attempts</span>
            <span className="font-semibold text-black">{stats.totalAttempts}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Time Spent</span>
            <span className="font-semibold text-black">{formatTime(stats.timeSpent)}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Tests Run</span>
            <span className="font-semibold text-black">{stats.testsRun}</span>
          </div>
        </div>
        <Button onClick={onContinue} className="w-full bg-black text-white hover:bg-black/90" size="lg">
          Continue
        </Button>
      </div>
    </div>
  );
}

