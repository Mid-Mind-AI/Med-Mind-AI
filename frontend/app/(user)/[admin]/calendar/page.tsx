"use client";
import Image from "next/image";
import { useEffect, useState } from "react";
import { AIVoiceInput } from "@/components/ui/ai-voice-input";
import { FullScreenCalendar } from "@/components/ui/fullscreen-calendar";
import { format } from "date-fns";

type BackendEvent = {
  id: string;
  patient_name: string;
  phone_number: string;
  doctor_name: string;
  start: string; // ISO 8601
  end: string;   // ISO 8601
  timezone: string;
  notes: string;
};

type CalendarEvent = {
  id: number;
  name: string;
  patient_name: string;
  phone_number: string;
  doctor_name: string;
  time: string;
  datetime: string;
  eventId: string; // Backend event ID
};

type CalendarDay = {
  day: Date;
  events: CalendarEvent[];
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function Admin() {
  const [data, setData] = useState<CalendarDay[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const today = new Date();
    const monthParam = format(today, "yyyy-MM");
    const url = `${API_BASE}/calendar?month=${monthParam}`;

    setLoading(true);
    setError(null);

    fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then(async (r) => {
        if (!r.ok) {
          const errorText = await r.text().catch(() => r.statusText);
          throw new Error(
            `HTTP error! status: ${r.status}, message: ${errorText}`
          );
        }
        return r.json();
      })
      .then((json) => {
        const events: BackendEvent[] = json.events || [];

        // Group backend events by calendar day
        const groups = new Map<string, CalendarEvent[]>();

        for (const ev of events) {
          const startDate = new Date(ev.start);
          const dayKey = format(startDate, "yyyy-MM-dd");
          const arr = groups.get(dayKey) || [];

          arr.push({
            // Store the actual event ID as a string, but convert to number for calendar component
            id: new Date(ev.start).getTime(),
            name: `${ev.doctor_name} - ${ev.patient_name}`,
            patient_name: ev.patient_name,
            phone_number: ev.phone_number,
            doctor_name: ev.doctor_name,
            time: format(startDate, "h:mm a"),
            datetime: ev.start,
            eventId: ev.id, // Store the actual backend event ID
          });
          groups.set(dayKey, arr);
        }

        const mapped: CalendarDay[] = Array.from(groups.entries()).map(
          ([dayKey, evs]) => ({
            day: new Date(dayKey),
            events: evs,
          })
        );

        setData(mapped);
        setLoading(false);
      })
      .catch((e) => {
        console.error("Failed to load events from", url, e);
        const errorMessage =
          e instanceof Error
            ? e.message
            : "Failed to connect to backend server";
        setError(
          `Unable to load calendar events. Please ensure the backend server is running at ${API_BASE}`
        );
        setData([]);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center bg-background rounded-lg h-screen">
        <div className="text-lg">Loading calendar events...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center bg-background rounded-lg h-screen p-8">
        <div className="text-lg text-destructive mb-4">Error</div>
        <div className="text-sm text-muted-foreground text-center max-w-md">
          {error}
        </div>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center bg-background rounded-lg ">
      <div className="flex h-screen w-full p-8">
        <FullScreenCalendar data={data} />
      </div>
    </div>
  );
}
