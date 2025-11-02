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
  time: string;
  datetime: string;
};

type CalendarDay = {
  day: Date;
  events: CalendarEvent[];
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function Admin() {
  const [data, setData] = useState<CalendarDay[]>([]);

  useEffect(() => {
    const today = new Date();
    const monthParam = format(today, "yyyy-MM");

    fetch(`${API_BASE}/calendar?month=${monthParam}`)
      .then((r) => r.json())
      .then((json) => {
        const events: BackendEvent[] = json.events || [];

        // Group backend events by calendar day
        const groups = new Map<string, CalendarEvent[]>();

        for (const ev of events) {
          const startDate = new Date(ev.start);
          const dayKey = format(startDate, "yyyy-MM-dd");
          const arr = groups.get(dayKey) || [];

          arr.push({
            // Use timestamp as numeric id to satisfy the calendar's number type
            id: new Date(ev.start).getTime(),
            name: `${ev.patient_name} (${ev.phone_number})`,
            patient_name: ev.patient_name,
            phone_number: ev.phone_number,
            time: format(startDate, "h:mm a"),
            datetime: ev.start,
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
      })
      .catch((e) => {
        console.error("Failed to load events", e);
        setData([]);
      });
  }, []);

  return (
    <div className="flex flex-col items-center justify-center bg-background rounded-lg ">
      <div className="flex h-screen w-full p-8">
        <FullScreenCalendar data={data} />
      </div>
    </div>
  );
}
