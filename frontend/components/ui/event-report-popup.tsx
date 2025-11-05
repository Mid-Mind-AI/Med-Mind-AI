import React, { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { format } from "date-fns";

interface Medication {
  name: string;
  dosage: string;
  frequency: string;
}

interface Report {
  patient_name: string;
  doctor_name: string;
  primary_concern?: string;
  current_medications?: Medication[];
  medical_history?: string;
  ai_insights?: string;
  suggested_questions?: string[];
  notes?: string;
}

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

  useEffect(() => {
    if (isOpen && event?.eventId) {
      fetchReport(event.eventId);
    } else {
      setReport(null);
      setError(null);
    }
  }, [isOpen, event?.eventId]);

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

  if (!isOpen || !event) return null;

  // Parse the datetime to get a formatted date
  const eventDate = new Date(event.datetime);
  const formattedDate = format(eventDate, "EEEE, MMMM d, yyyy");

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
      <Card className="bg-white rounded-2xl shadow-lg w-[420px] max-h-[90vh] overflow-y-auto p-6 relative animate-fadeIn">
        <Button
          onClick={onClose}
          className="absolute top-3 right-3 text-gray-500 hover:text-gray-800"
          variant="ghost"
        >
          ✖
        </Button>

        <h2 className="text-xl font-semibold mb-4">Appointment Details</h2>

        {/* User Provided Information */}
        <div className="text-sm text-gray-600 space-y-3 mb-6 pb-6 border-b">
          <div>
            <p className="font-medium text-gray-700 mb-1">Doctor:</p>
            <p className="text-gray-900">{event.doctor_name}</p>
          </div>

          <div>
            <p className="font-medium text-gray-700 mb-1">Patient Name:</p>
            <p className="text-gray-900">{event.patient_name}</p>
          </div>

          <div>
            <p className="font-medium text-gray-700 mb-1">Phone Number:</p>
            <p className="text-gray-900">{event.phone_number}</p>
          </div>

          <div>
            <p className="font-medium text-gray-700 mb-1">Date:</p>
            <p className="text-gray-900">{formattedDate}</p>
          </div>

          <div>
            <p className="font-medium text-gray-700 mb-1">Time:</p>
            <p className="text-gray-900">{event.time}</p>
          </div>
        </div>

        {/* Report Section */}
        <div className="mt-6">
          <h3 className="font-semibold text-gray-800 mb-3">Pre-Visit Report</h3>
          {loading && (
            <div className="bg-gray-50 rounded-lg p-4 border text-center text-gray-500">
              <p className="text-sm">Loading report...</p>
            </div>
          )}
          {error && (
            <div className="bg-red-50 rounded-lg p-4 border border-red-200 text-red-700">
              <p className="text-sm">{error}</p>
            </div>
          )}
          {!loading && !error && report && (
            <div className="bg-gray-50 rounded-lg p-4 border space-y-4">
              {report.primary_concern && (
                <div>
                  <p className="font-medium text-gray-700 mb-1 text-sm">Primary Concern:</p>
                  <p className="text-gray-900 text-sm">{report.primary_concern}</p>
                </div>
              )}

              {report.current_medications && report.current_medications.length > 0 && (
                <div>
                  <p className="font-medium text-gray-700 mb-1 text-sm">Current Medications:</p>
                  <ul className="list-disc list-inside space-y-1 text-sm text-gray-900">
                    {report.current_medications.map((med, idx) => (
                      <li key={idx}>
                        {med.name} {med.dosage && `- ${med.dosage}`} {med.frequency && `(${med.frequency})`}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {report.medical_history && (
                <div>
                  <p className="font-medium text-gray-700 mb-1 text-sm">Medical History:</p>
                  <p className="text-gray-900 text-sm">{report.medical_history}</p>
                </div>
              )}

              {report.ai_insights && (
                <div>
                  <p className="font-medium text-gray-700 mb-1 text-sm">AI Insights:</p>
                  <p className="text-gray-900 text-sm">{report.ai_insights}</p>
                </div>
              )}

              {report.suggested_questions && report.suggested_questions.length > 0 && (
                <div>
                  <p className="font-medium text-gray-700 mb-2 text-sm">Suggested Questions for Doctor:</p>
                  <ol className="list-decimal list-inside space-y-1.5 text-sm text-gray-900">
                    {report.suggested_questions.map((question, idx) => (
                      <li key={idx} className="pl-2">{question}</li>
                    ))}
                  </ol>
                </div>
              )}

              {report.notes && (
                <div>
                  <p className="font-medium text-gray-700 mb-1 text-sm">Notes:</p>
                  <p className="text-gray-900 text-sm">{report.notes}</p>
                </div>
              )}

              {!report.primary_concern && !report.medical_history && !report.ai_insights && !report.notes && (!report.current_medications || report.current_medications.length === 0) && (!report.suggested_questions || report.suggested_questions.length === 0) && (
                <p className="text-sm text-gray-500 text-center">No report data available yet.</p>
              )}
            </div>
          )}
          {!loading && !error && !report && (
            <div className="bg-gray-50 rounded-lg p-4 border-2 border-dashed border-gray-300 text-center text-gray-500">
              <p className="text-sm">Pre-visit report not yet generated.</p>
              <p className="text-xs mt-2 text-gray-400">Complete pre-visit questions to generate report.</p>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default EventReportPopup;
