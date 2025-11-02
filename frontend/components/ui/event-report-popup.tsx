import React from "react";
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
  notes?: string;
}

interface EventData {
  id: number;
  name: string;
  patient_name: string;
  phone_number: string;
  time: string;
  datetime: string;
}

interface EventReportPopupProps {
  isOpen: boolean;
  onClose: () => void;
  event: EventData | null;
}

const EventReportPopup: React.FC<EventReportPopupProps> = ({
  isOpen,
  onClose,
  event,
}) => {
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

        {/* Report Placeholder Section */}
        <div className="mt-6">
          <h3 className="font-semibold text-gray-800 mb-3">Report</h3>
          <div className="bg-gray-50 rounded-lg p-4 border-2 border-dashed border-gray-300 text-center text-gray-500 min-h-[200px] flex items-center justify-center">
            <p className="text-sm">Report content will be displayed here</p>
            <p className="text-xs mt-2 text-gray-400">(Placeholder for create_event_summary API)</p>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default EventReportPopup;
