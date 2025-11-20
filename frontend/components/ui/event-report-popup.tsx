import React, { useState, useEffect, useRef } from "react";
import { format } from "date-fns";
import { Button } from "@/components/ui/button";
import { X, Calendar, User, Phone, Stethoscope, Copy, Check } from "lucide-react";

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
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const modalRef = useRef<HTMLDivElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);

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

  // Keyboard support
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener("keydown", handleEscape);
      // Focus the close button when modal opens
      setTimeout(() => closeButtonRef.current?.focus(), 100);
    }

    return () => {
      document.removeEventListener("keydown", handleEscape);
    };
  }, [isOpen, onClose]);

  // Copy to clipboard helper
  const copyToClipboard = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  if (!isOpen || !event) return null;

  const eventDate = new Date(event.datetime);
  const formattedDate = format(eventDate, "MMM d, yyyy");
  const formattedTime = format(eventDate, "h:mm a");

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-in fade-in-0 duration-200"
      onClick={onClose}
    >
      <div
        ref={modalRef}
        className="relative flex h-[85vh] w-full max-w-5xl flex-col overflow-hidden rounded-2xl bg-background shadow-2xl animate-in fade-in-0 zoom-in-95 slide-in-from-bottom-4 duration-300"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="report-title"
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border px-6 sm:px-8 py-4 sm:py-5">
          <div className="flex flex-col gap-1">
            <h2 id="report-title" className="text-xl font-bold tracking-tight text-foreground">
              Appointment Report
            </h2>
            <p className="text-sm text-muted-foreground">
              {formattedDate}
            </p>
          </div>
          <Button
            ref={closeButtonRef}
            onClick={onClose}
            variant="ghost"
            size="icon"
            className="h-8 w-8 rounded-lg text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
            aria-label="Close dialog"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Content */}
        <div className="flex min-h-0 flex-1 overflow-hidden flex-col lg:flex-row">
          {/* Left Sidebar - Overview */}
          <div className="flex w-full lg:w-80 flex-col border-r border-border bg-muted/30 overflow-y-auto">
            <div className="px-4 sm:px-6 py-6 space-y-6">
              {/* Patient Info */}
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="mt-0.5 rounded-lg bg-muted p-2">
                    <User className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Patient
                    </p>
                    <p className="mt-1 text-sm font-medium text-foreground truncate">
                      {event.patient_name}
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="mt-0.5 rounded-lg bg-muted p-2">
                    <Stethoscope className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Doctor
                    </p>
                    <p className="mt-1 text-sm font-medium text-foreground truncate">
                      {event.doctor_name || event.name || "N/A"}
                    </p>
                  </div>
                </div>

                {event.phone_number && (
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5 rounded-lg bg-muted p-2">
                      <Phone className="h-4 w-4 text-muted-foreground" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                        Phone
                      </p>
                      <p className="mt-1 text-sm font-medium text-foreground">
                        {event.phone_number}
                      </p>
                    </div>
                  </div>
                )}

                <div className="flex items-start gap-3">
                  <div className="mt-0.5 rounded-lg bg-muted p-2">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Time
                    </p>
                    <p className="mt-1 text-sm font-medium text-foreground">
                      {formattedTime}
                    </p>
                  </div>
                </div>
              </div>

              {/* Status Badge */}
              <div className="pt-4 border-t border-border">
                <div className="rounded-xl bg-card border border-border px-4 py-3">
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">
                    Status
                  </p>
                  <div className="flex items-center gap-2">
                    <div className={`h-2 w-2 rounded-full ${report ? 'bg-green-500' : 'bg-muted-foreground/50'}`} />
                    <p className="text-sm font-medium text-foreground">
                      {report ? "Report Generated" : "Pending"}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Content - Report */}
          <div className="flex min-w-0 flex-1 flex-col bg-background">
            <div className="border-b border-border px-6 sm:px-8 py-4">
              <h3 className="text-sm font-medium text-foreground">
                Pre-Visit Report
              </h3>
            </div>

            <div className="flex-1 overflow-y-auto px-4 sm:px-6 lg:px-8 py-6">
              {loading && (
                <div className="flex items-center justify-center py-12">
                  <div className="text-center">
                    <div className="inline-block h-8 w-8 animate-spin rounded-full border-2 border-muted border-t-foreground mb-3" />
                    <p className="text-sm text-muted-foreground">Loading report...</p>
                  </div>
                </div>
              )}

              {error && (
                <div className="rounded-xl border border-destructive/50 bg-destructive/10 px-4 py-3">
                  <p className="text-sm font-medium text-destructive">{error}</p>
                </div>
              )}

              {!loading && !error && report && (
                <div className="space-y-5">
                  {report.primary_concern && (
                    <div className="group relative rounded-xl border border-border bg-muted/30 px-5 py-4 hover:bg-muted/50 transition-colors">
                      <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7"
                          onClick={() => copyToClipboard(report.primary_concern || "", "primary_concern")}
                          aria-label="Copy primary concern"
                        >
                          {copiedId === "primary_concern" ? (
                            <Check className="h-3.5 w-3.5 text-green-600" />
                          ) : (
                            <Copy className="h-3.5 w-3.5 text-muted-foreground" />
                          )}
                        </Button>
                      </div>
                      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">
                        Primary Concern
                      </p>
                      <p className="text-sm font-normal leading-relaxed text-foreground pr-8">
                        {report.primary_concern}
                      </p>
                    </div>
                  )}

                  {(report.current_medications?.length ||
                    report.medications?.length) && (
                    <div className="group relative rounded-xl border border-border bg-muted/30 px-5 py-4 hover:bg-muted/50 transition-colors">
                      <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7"
                          onClick={() => {
                            const medsText = (report.current_medications ?? report.medications ?? [])
                              .map(m => `${m.name}${m.dosage ? ` - ${m.dosage}` : ""}${m.frequency ? ` (${m.frequency})` : ""}`)
                              .join("\n");
                            copyToClipboard(medsText, "medications");
                          }}
                          aria-label="Copy medications"
                        >
                          {copiedId === "medications" ? (
                            <Check className="h-3.5 w-3.5 text-green-600" />
                          ) : (
                            <Copy className="h-3.5 w-3.5 text-muted-foreground" />
                          )}
                        </Button>
                      </div>
                      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3">
                        Current Medications
                      </p>
                      <ul className="space-y-2 pr-8">
                        {(report.current_medications ??
                          report.medications ??
                          []
                        ).map((m, idx) => (
                          <li key={idx} className="flex items-start gap-2 text-sm text-foreground">
                            <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-muted-foreground/60 shrink-0" />
                            <span className="flex-1">
                              <span className="font-medium">{m.name}</span>
                              {m.dosage && <span className="text-muted-foreground"> • {m.dosage}</span>}
                              {m.frequency && <span className="text-muted-foreground"> • {m.frequency}</span>}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {report.medical_history && (
                    <div className="group relative rounded-xl border border-border bg-muted/30 px-5 py-4 hover:bg-muted/50 transition-colors">
                      <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7"
                          onClick={() => copyToClipboard(report.medical_history || "", "medical_history")}
                          aria-label="Copy medical history"
                        >
                          {copiedId === "medical_history" ? (
                            <Check className="h-3.5 w-3.5 text-green-600" />
                          ) : (
                            <Copy className="h-3.5 w-3.5 text-muted-foreground" />
                          )}
                        </Button>
                      </div>
                      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">
                        Medical History
                      </p>
                      <p className="text-sm font-normal leading-relaxed text-foreground whitespace-pre-line pr-8">
                        {report.medical_history}
                      </p>
                    </div>
                  )}

                  {report.ai_insights && (
                    <div className="group relative rounded-xl border border-primary/20 bg-primary/5 px-5 py-4 hover:bg-primary/10 transition-colors">
                      <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7"
                          onClick={() => copyToClipboard(report.ai_insights || "", "ai_insights")}
                          aria-label="Copy AI insights"
                        >
                          {copiedId === "ai_insights" ? (
                            <Check className="h-3.5 w-3.5 text-green-600" />
                          ) : (
                            <Copy className="h-3.5 w-3.5 text-primary" />
                          )}
                        </Button>
                      </div>
                      <p className="text-xs font-medium text-primary uppercase tracking-wider mb-2">
                        AI Insights
                      </p>
                      <p className="text-sm font-normal leading-relaxed text-foreground whitespace-pre-line pr-8">
                        {report.ai_insights}
                      </p>
                    </div>
                  )}

                  {report.suggested_questions &&
                    report.suggested_questions.length > 0 && (
                      <div className="group relative rounded-xl border border-border bg-muted/30 px-5 py-4 hover:bg-muted/50 transition-colors">
                        <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-7 w-7"
                            onClick={() => copyToClipboard(report.suggested_questions?.join("\n") || "", "suggested_questions")}
                            aria-label="Copy suggested questions"
                          >
                            {copiedId === "suggested_questions" ? (
                              <Check className="h-3.5 w-3.5 text-green-600" />
                            ) : (
                              <Copy className="h-3.5 w-3.5 text-muted-foreground" />
                            )}
                          </Button>
                        </div>
                        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3">
                          Suggested Questions
                        </p>
                        <ol className="space-y-2 pr-8">
                          {report.suggested_questions.map((q, i) => (
                            <li key={i} className="flex gap-3 text-sm text-foreground">
                              <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-muted text-xs font-medium text-muted-foreground">
                                {i + 1}
                              </span>
                              <span className="flex-1 leading-relaxed">{q}</span>
                            </li>
                          ))}
                        </ol>
                      </div>
                    )}

                  {report.notes && (
                    <div className="group relative rounded-xl border border-border bg-muted/30 px-5 py-4 hover:bg-muted/50 transition-colors">
                      <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7"
                          onClick={() => copyToClipboard(report.notes || "", "notes")}
                          aria-label="Copy notes"
                        >
                          {copiedId === "notes" ? (
                            <Check className="h-3.5 w-3.5 text-green-600" />
                          ) : (
                            <Copy className="h-3.5 w-3.5 text-muted-foreground" />
                          )}
                        </Button>
                      </div>
                      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">
                        Notes
                      </p>
                      <p className="text-sm font-normal leading-relaxed text-foreground whitespace-pre-line pr-8">
                        {report.notes}
                      </p>
                    </div>
                  )}

                  {!report.primary_concern &&
                    !report.medical_history &&
                    !report.ai_insights &&
                    !report.notes &&
                    !(report.current_medications?.length ||
                      report.medications?.length) &&
                    !(report.suggested_questions?.length) && (
                      <div className="py-12 text-center">
                        <p className="text-sm text-muted-foreground">
                          No report data available yet.
                        </p>
                      </div>
                    )}
                </div>
              )}

              {!loading && !error && !report && (
                <div className="flex items-center justify-center py-16">
                  <div className="text-center max-w-sm">
                    <div className="mx-auto mb-4 h-12 w-12 rounded-full bg-muted flex items-center justify-center">
                      <Calendar className="h-6 w-6 text-muted-foreground" />
                    </div>
                    <p className="text-sm font-medium text-foreground mb-1">
                      Report Not Generated
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Complete pre-visit questions to generate a report.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EventReportPopup;
