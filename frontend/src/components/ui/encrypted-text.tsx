import { useEffect, useState, useRef } from "react";
import { cn } from "@/lib/utils";

interface EncryptedTextProps {
  text: string;
  encryptedClassName?: string;
  revealedClassName?: string;
  revealDelayMs?: number;
  className?: string;
  autoStart?: boolean;
  triggerOnHover?: boolean;
}

export function EncryptedText({
  text,
  encryptedClassName = "text-neutral-500",
  revealedClassName = "dark:text-white text-black",
  revealDelayMs = 80,
  className,
  autoStart = true,
  triggerOnHover = false,
}: EncryptedTextProps) {
  const [displayText, setDisplayText] = useState("");
  const [currentIndex, setCurrentIndex] = useState(-1);
  const [isComplete, setIsComplete] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const ref = useRef<HTMLSpanElement>(null);

  const chars = "!@#$%^&*()_+-=[]{}|;:,.<>?";

  const startAnimation = () => {
    setHasStarted(true);
    setCurrentIndex(0);
    setIsComplete(false);
  };

  const handleHover = () => {
    if (triggerOnHover) {
      startAnimation();
    }
  };

  // Intersection Observer to auto-start animation when in view
  useEffect(() => {
    if (!autoStart || hasStarted) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !hasStarted) {
            setHasStarted(true);
            setCurrentIndex(0);
          }
        });
      },
      { threshold: 0.1 }
    );

    const currentRef = ref.current;
    if (currentRef) {
      observer.observe(currentRef);
    }

    return () => {
      if (currentRef) {
        observer.unobserve(currentRef);
      }
    };
  }, [autoStart, hasStarted]);

  useEffect(() => {
    if (!hasStarted || currentIndex < 0) return;

    if (currentIndex >= text.length) {
      setIsComplete(true);
      return;
    }

    const interval = setInterval(() => {
      setDisplayText(() => {
        const revealed = text.slice(0, currentIndex + 1);
        const encrypted = text
          .slice(currentIndex + 1)
          .split("")
          .map(() => chars[Math.floor(Math.random() * chars.length)])
          .join("");
        return revealed + encrypted;
      });
    }, 50);

    const revealTimeout = setTimeout(() => {
      setCurrentIndex((prev) => prev + 1);
    }, revealDelayMs);

    return () => {
      clearInterval(interval);
      clearTimeout(revealTimeout);
    };
  }, [currentIndex, text, revealDelayMs, chars, hasStarted]);

  return (
    <span
      ref={ref}
      onMouseEnter={handleHover}
      className={cn(
        "transition-colors duration-200",
        triggerOnHover && "cursor-pointer",
        isComplete ? revealedClassName : encryptedClassName,
        className
      )}
    >
      {isComplete ? text : displayText}
    </span>
  );
}

