"use client";

import Image from "next/image";
import { AIVoiceInput } from "@/components/ui/ai-voice-input";
import { useState } from "react";

export default function Call() {
  const [transcript, setTranscript] = useState<string>("");

  const handleTranscript = (duration: number, text?: string) => {
    if (text) {
      setTranscript(text);
      console.log("Transcript received:", text);
      // Here you could process the transcript for booking purposes
    }
  };

  return (
    <div className="flex flex-col items-center justify-center bg-background rounded-lg h-full m-4 border border-accent gap-16">
      <h1 className="text-4xl font-bold max-w-lg md:max-w-xl text-center">Start a call to get started booking your appointment</h1>
      <div className="flex justify-center">
        <AIVoiceInput
          className="bg-secondary rounded-lg p-4 w-fit"
          onStop={handleTranscript}
        />
      </div>
      {transcript && (
        <div className="max-w-2xl w-full p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">You said:</p>
          <p className="text-base text-gray-900 dark:text-gray-100">{transcript}</p>
        </div>
      )}
    </div>
  );
}
