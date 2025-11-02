"use client";

import { Mic } from "lucide-react";
import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";

interface AIVoiceInputProps {
  onStart?: () => void;
  onStop?: (duration: number) => void;
  visualizerBars?: number;
  demoMode?: boolean;
  demoInterval?: number;
  className?: string;
}

export function AIVoiceInput({
  onStart,
  onStop,
  visualizerBars = 48,
  demoMode = false,
  demoInterval = 3000,
  className
}: AIVoiceInputProps) {
  const [submitted, setSubmitted] = useState(false);
  const [time, setTime] = useState(0);
  const [isClient, setIsClient] = useState(false);
  const [isDemo, setIsDemo] = useState(demoMode);

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    if (submitted) {
      onStart?.();
      intervalId = setInterval(() => {
        setTime((t) => t + 1);
      }, 1000);
    } else {
      onStop?.(time);
      setTime(0);
    }

    return () => clearInterval(intervalId);
  }, [submitted, time, onStart, onStop]);

  useEffect(() => {
    if (!isDemo) return;

    let timeoutId: NodeJS.Timeout;
    const runAnimation = () => {
      setSubmitted(true);
      timeoutId = setTimeout(() => {
        setSubmitted(false);
        timeoutId = setTimeout(runAnimation, 1000);
      }, demoInterval);
    };

    const initialTimeout = setTimeout(runAnimation, 100);
    return () => {
      clearTimeout(timeoutId);
      clearTimeout(initialTimeout);
    };
  }, [isDemo, demoInterval]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const handleClick = () => {
    if (isDemo) {
      setIsDemo(false);
      setSubmitted(false);
    } else {
      setSubmitted((prev) => !prev);
    }
  };

  return (
    <div className={cn("w-full py-8", className)}>
      <div className="relative max-w-xl w-full mx-auto flex items-center flex-col gap-4">
        <button
          className={cn(
            "group relative w-20 h-20 rounded-full flex items-center justify-center transition-all duration-300 hover:scale-105",
            submitted
              ? "bg-none"
              : "bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 border border-gray-200 dark:border-gray-700 hover:shadow-lg hover:border-gray-300 dark:hover:border-gray-600"
          )}
          type="button"
          onClick={handleClick}
        >
          {submitted ? (
            <div className="relative">
              <div
                className="w-8 h-8 rounded-sm animate-spin bg-black dark:bg-white cursor-pointer pointer-events-auto"
                style={{ animationDuration: "3s" }}
              />
              {/* Subtle glow effect when active */}
              <div className="absolute inset-0 rounded-sm bg-black/20 dark:bg-white/20 blur-sm animate-pulse" style={{ animationDuration: "2s" }} />
            </div>
          ) : (
            <Mic className="w-8 h-8 text-gray-700 dark:text-gray-300 group-hover:text-gray-900 dark:group-hover:text-gray-100 transition-colors" strokeWidth={1.5} />
          )}
        </button>

        <span
          className={cn(
            "font-mono text-xl font-light tracking-wider transition-all duration-300",
            submitted
              ? "text-gray-900 dark:text-gray-100"
              : "text-gray-400 dark:text-gray-600"
          )}
        >
          {formatTime(time)}
        </span>

        <div className="h-8 w-72 flex items-end justify-center gap-0.5">
          {[...Array(visualizerBars)].map((_, i) => (
            <div
              key={i}
              className={cn(
                "w-0.5 rounded-full transition-all duration-200 ease-out",
                submitted
                  ? "bg-gradient-to-t from-gray-900 via-gray-700 to-gray-900 dark:from-white dark:via-gray-300 dark:to-white"
                  : "bg-gray-200 dark:bg-gray-800 h-2"
              )}
              style={
                submitted && isClient
                  ? {
                      height: `${20 + Math.random() * 80}%`,
                      animationDelay: `${i * 0.05}s`,
                    }
                  : undefined
              }
            />
          ))}
        </div>

        <p className={cn(
          "text-xs font-medium tracking-wide transition-all duration-300",
          submitted
            ? "text-gray-700 dark:text-gray-300"
            : "text-gray-500 dark:text-gray-500"
        )}>
          {submitted ? "Listening..." : "Click to speak"}
        </p>
      </div>
    </div>
  );
}
