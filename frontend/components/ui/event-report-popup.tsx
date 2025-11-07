import React, { useState, useEffect } from "react";
import { format } from "date-fns";
import { Button } from "@/components/ui/button";
import { X } from "lucide-react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";

interface EventData {
  id: number;
  name: string;
  patient_name: string;
  phone_number: string;
  doctor_name: string;
  time: string;
  datetime: string;
  eventId?: string; // Backend event ID
}

interface Report {
  primary_concern?: string | null;
  medications?: Array<{
    name: string;
    dosage: string;
    frequency: string;
    duration?: string;
  }>;
  current_medications?: Array<{
    name: string;
    dosage: string;
    frequency: string;
    duration?: string;
  }>;
  medical_history?: string | null;
  ai_insights?: string | null;
  suggested_questions?: string[];
  notes?: string | null;
}

interface EventReportPopupProps {
  isOpen: boolean;
  onClose: () => void;
  event: EventData | null;
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

const EventReportPopup: React.FC<EventReportPopupProps> = ({
  isOpen,
  onClose,
  event,
}) => {
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchReport = async (eventId: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/report/${eventId}`);
      if (!response.ok) {
        throw new Error("Failed to fetch report");
      }
      const data = await response.json();
      setReport(data.report);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load report");
      console.error("Error fetching report:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen && event?.eventId) {
      fetchReport(event.eventId);
    } else {
      setReport(null);
      setError(null);
    }
  }, [isOpen, event?.eventId]);

  if (!isOpen || !event) return null;

  const eventDate = new Date(event.datetime);
  const formattedDate = format(eventDate, "MMMM d, yyyy");
  const formattedDateTime = format(eventDate, "MMMM d, yyyy 'at' h:mm a");

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/40 z-50">
      <Card className="relative py-2 max-w-6xl h-full max-h-[90vh] flex flex-col rounded-3xl animate-fadeIn ">
        {/* Header */}
        <CardHeader className=" border-b pb-0 ">
          <div className="flex items-center justify-between px-4">
          <CardTitle className="text-lg font-semibold text-foreground  ">
            Appointment Report
          </CardTitle>
          <Button
            onClick={onClose}
            variant="ghost"
            size="icon"
            className=" hover:bg-accent"
          >
            <X className="h-4 w-4" />
          </Button>
          
          </div>
        </CardHeader>

        {/* Content - Two Column Layout */}
        <div className="flex-1 overflow-auto">
          <CardContent className="relative  z-10">
          <div className="grid grid-cols-3 gap-4">
            {/* Left Column - 1/3 width */}
            <div className="col-span-1 space-y-4">
              {/* Doctor Patient Info Section */}
              <div className="border-2 rounded-2xl p-4 bg-white">
                <h3 className="font-bold text-foreground text-base ">
                  Doctor Patient Info
                </h3>
                <div className=" text-sm space-y-2">
                  <div>
                    <p className="font-medium text-foreground ">Doctor Name</p>
                    <p className="text-muted-foreground">{event.doctor_name || event.name || "N/A"}</p>
                  </div>
                  <div>
                    <p className="font-medium text-foreground ">Patient Name</p>
                    <p className="text-muted-foreground">{event.patient_name}</p>
                  </div>
                  <div>
                    <p className="font-medium text-foreground ">Date of call:</p>
                    <p className="text-muted-foreground">{formattedDateTime}</p>
                  </div>
                </div>
              </div>

              {/* Recommended Actions Section */}
              <div className="border-2 rounded-2xl p-4 bg-white ">
                <h3 className="font-bold text-foreground  ">
                  Recommended Actions
                </h3>
                <ul className="text-sm text-muted-foreground list-disc list-inside">
                  <li>Follow up Call</li>
                  <li>Prepare blood test for appointment</li>
                </ul>
              </div>
            </div>

            {/* Right Column - 2/3 width */}
            <div className="col-span-2">
              {/* Pre-Visit Report Section (fetched from backend/LLM) */}
              <div className="border-2 rounded-2xl p-4 bg-white h-full min-h-[400px]">
                <h3 className="font-bold text-foreground ">Pre-Visit Report</h3>

                {loading && (
                  <div className="border bg-muted/40 rounded-lg p-4 text-center text-foreground-muted">
                    <p className="text-sm">Loading report...</p>
                  </div>
                )}

                {error && (
                  <div className="rounded-lg p-4 border border-red-200 bg-red-50 text-red-700">
                    <p className="text-sm">{error}</p>
                  </div>
                )}

                {!loading && !error && report && (
                  <div className=" space-y-2">
                    {report.primary_concern && (
                      <div>
                        <p className="font-medium text-foreground text-sm">Primary Concern:</p>
                        <p className="text-muted-foreground text-sm">{report.primary_concern}</p>
                      </div>
                    )}

                    {(report.current_medications?.length || report.medications?.length) ? (
                      <div>
                        <p className="font-medium text-foreground text-sm">Current Medications:</p>
                        <ul className="list-disc list-inside text-sm text-muted-foreground">
                          {(report.current_medications ?? report.medications ?? []).map((med, idx) => (
                            <li key={idx}>
                              {med.name} {med.dosage ? `- ${med.dosage}` : ""} {med.frequency ? `(${med.frequency})` : ""}
                            </li>
                          ))}
                        </ul>
                      </div>
                    ) : null}

                    {report.medical_history && (
                      <div>
                        <p className="font-medium text-foreground text-sm">Medical History:</p>
                        <p className="text-muted-foreground text-sm">{report.medical_history}</p>
                      </div>
                    )}

                    {report.ai_insights && (
                      <div>
                        <p className="font-medium text-foreground text-sm">AI Insights:</p>
                        <p className="text-muted-foreground text-sm whitespace-pre-line">{report.ai_insights}</p>
                      </div>
                    )}

                    {(report.suggested_questions && report.suggested_questions.length > 0) && (
                      <div>
                        <p className="font-medium text-foreground text-sm">Suggested Questions for Doctor:</p>
                        <ol className="list-decimal list-inside text-sm text-foreground/90">
                          {report.suggested_questions.map((q, idx) => (
                            <li key={idx} className="pl-2">{q}</li>
                          ))}
                        </ol>
                      </div>
                    )}

                    {report.notes && (
                      <div>
                        <p className="font-medium text-foreground text-sm">Notes:</p>
                        <p className="text-muted-foreground text-sm">{report.notes}</p>
                      </div>
                    )}

                    {(!report.primary_concern && !report.medical_history && !report.ai_insights && !report.notes && !(report.current_medications?.length || report.medications?.length) && !(report.suggested_questions?.length)) && (
                      <p className="text-sm text-foreground/90 text-center">No report data available yet.</p>
                    )}
                  </div>
                )}

                {!loading && !error && !report && (
                  <div className="rounded-lg p-4 border-2 border-dashed border-gray-300 text-center text-muted-foreground">
                    <p className="text-sm">Pre-visit report not yet generated.</p>
                    <p className="text-xs mt-2">Complete pre-visit questions to generate report.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
          </CardContent>
        </div>
      </Card>
    </div>
  );
};

export default EventReportPopup;