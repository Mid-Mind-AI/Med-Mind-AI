import React from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

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
  notes?: string;
}

interface EventReportPopupProps {
  isOpen: boolean;
  onClose: () => void;
  report: Report | null;
}

const EventReportPopup: React.FC<EventReportPopupProps> = ({
  isOpen,
  onClose,
  report,
}) => {
  if (!isOpen || !report) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
      <Card className="bg-white rounded-2xl shadow-lg w-[420px] p-6 relative animate-fadeIn">
        <Button
          onClick={onClose}
          className="absolute top-3 right-3 text-gray-500 hover:text-gray-800"
          variant="ghost"
        >
          ✖
        </Button>

        <h2 className="text-xl font-semibold mb-3">MedGemma Report</h2>
        <div className="text-sm text-gray-600 space-y-2">
          <p><strong>Doctor:</strong> {report.doctor_name}</p>
          <p><strong>Patient:</strong> {report.patient_name}</p>

          <div>
            <h3 className="font-medium mt-3">Primary Concern:</h3>
            <p>{report.primary_concern || "Not specified"}</p>
          </div>

          <div>
            <h3 className="font-medium mt-3">Current Medications:</h3>
            <ul className="list-disc pl-5">
              {report.current_medications?.length ? (
                report.current_medications.map((m, i) => (
                  <li key={i}>
                    {m.name} — {m.dosage} ({m.frequency})
                  </li>
                ))
              ) : (
                <li>No current medications</li>
              )}
            </ul>
          </div>

          <div>
            <h3 className="font-medium mt-3">Medical History:</h3>
            <p>{report.medical_history || "Not available"}</p>
          </div>

          <div>
            <h3 className="font-medium mt-3">AI Insights:</h3>
            <p>{report.ai_insights || "No insights yet"}</p>
          </div>

          {report.notes && (
            <div>
              <h3 className="font-medium mt-3">Notes:</h3>
              <p>{report.notes}</p>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default EventReportPopup;