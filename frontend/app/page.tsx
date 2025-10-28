"use client";
import { useEffect, useRef, useState } from "react";

export default function Home() {
  const recognitionRef = useRef<any>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState("");


  useEffect(() => {
    return () => {
      if (recognitionRef.current) recognitionRef.current.stop();
    };
  }, []);

  const startRecognition = () => {
    setError("");
    setTranscript("");

    const SpeechRecognition =
      (typeof window !== "undefined" && (window as any).SpeechRecognition) ||
      (typeof window !== "undefined" && (window as any).webkitSpeechRecognition);

    if (!SpeechRecognition) {
      setError("Web Speech API not supported in this browser.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = navigator.language || "en-US";
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = (event: any) => {
      let finalText = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          finalText += result[0].transcript;
        }
      }
      if (finalText) setTranscript((prev) => (prev ? prev + " " + finalText : finalText));
    };

    recognition.onerror = (e: any) => {
      setError(e?.error || "Speech recognition error");
    };

    recognition.onend = () => {
      setIsRecording(false);
    };

    recognition.start();
    recognitionRef.current = recognition;
    setIsRecording(true);
  };

  const stopRecognition = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsRecording(false);
    }
  };


  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black p-10">
      <main className="flex w-full max-w-2xl flex-col gap-6 rounded-xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-950">
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">Speech to Text</h1>
        <div className="flex items-center gap-4">
          {!isRecording ? (
            <button onClick={startRecognition} className="rounded-md bg-zinc-900 px-4 py-2 text-white dark:bg-zinc-100 dark:text-zinc-900">
              Start Listening
            </button>
          ) : (
            <button onClick={stopRecognition} className="rounded-md bg-red-600 px-4 py-2 text-white">
              Stop Listening
            </button>
          )}

        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
        {transcript && (
          <div className="rounded-md border border-zinc-200 p-4 text-sm dark:border-zinc-800 dark:text-zinc-100">
            {transcript}
          </div>
        )}
      </main>
    </div>
  );
}
