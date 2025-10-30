import Image from "next/image";
import { AIVoiceInput } from "@/components/ui/ai-voice-input";
export default function Call() {
  return (
    <div className="flex flex-col items-center justify-center bg-background rounded-lg h-full m-4  border border-accent gap-16">
            <h1 className="text-4xl font-bold max-w-lg md:max-w-xl text-center">Start a call to get started booking your appointment</h1>
            <div className="flex justify-center">
                <AIVoiceInput className="bg-secondary rounded-lg p-4 w-fit" />
            </div>
    </div>
  );
}
