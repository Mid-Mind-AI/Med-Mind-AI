import React from "react";
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

  const eventDate = new Date(event.datetime);
  const formattedDate = format(eventDate, "MMMM d, yyyy");
  const formattedDateTime = format(eventDate, "MMMM d, yyyy 'at' h:mm a");

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/40 z-50">
      <Card className="relative w-[90vw] max-w-[1200px] max-h-[90vh] overflow-y-auto animate-fadeIn border-2 shadow-2xl rounded-2xl bg-gradient-to-br from-white to-neutral-50">
        {/* Header */}
        <CardHeader className="relative border-b pb-4">
          <Button
            onClick={onClose}
            variant="ghost"
            size="icon"
            className="absolute top-3 right-3 hover:bg-accent"
          >
            <X className="h-4 w-4" />
          </Button>
          <CardTitle className="text-lg font-semibold text-foreground">
            Appointment Report
          </CardTitle>
        </CardHeader>

        {/* Content - Two Column Layout */}
        <CardContent className="relative p-6 z-10">
          <div className="grid grid-cols-3 gap-6">
            {/* Left Column - 1/3 width */}
            <div className="col-span-1 space-y-6">
              {/* Doctor Patient Info Section */}
              <div className="border-2 rounded-2xl p-4 bg-white">
                <h3 className="font-semibold text-foreground text-base mb-6">
                  Doctor Patient Info
                </h3>
                <div className="space-y-3 text-sm">
                  <div>
                    <p className="font-bold text-gray-600 mb-1">Doctor Name</p>
                    <p className="text-muted-foreground">{event.name || "N/A"}</p>
                  </div>
                  <div>
                    <p className="font-bold text-gray-600 mb-1">Patient Name</p>
                    <p className="text-muted-foreground">{event.patient_name}</p>
                  </div>
                  <div>
                    <p className="font-bold text-gray-600 mb-1">Date of call:</p>
                    <p className="text-muted-foreground">{formattedDateTime}</p>
                  </div>
                </div>
              </div>

              {/* Recommended Actions Section */}
              <div className="border-2 rounded-2xl p-4 bg-white">
                <h3 className="font-semibold text-foreground text-base mb-4">
                  Recommended Actions
                </h3>
                <ul className="space-y-2 text-sm text-muted-foreground list-disc list-inside">
                  <li>Follow up Call</li>
                  <li>Prepare blood test for appointment</li>
                </ul>
              </div>
            </div>

            {/* Right Column - 2/3 width */}
            <div className="col-span-2">
              {/* AI Insights Section */}
              <div className="border-2 rounded-2xl p-6 bg-white h-full min-h-[400px]">
                <h3 className="font-semibold text-foreground text-base mb-4">
                  AI Insights
                </h3>
                <div className="border border-dashed border-gray-300 bg-muted/40 rounded-xl p-6 text-center text-muted-foreground min-h-[350px] flex flex-col items-center justify-center hover:border-gray-400 transition">
                  <p className="text-sm font-medium">
                    AI insights will be displayed here
                  </p>
                  <p className="text-xs mt-1 text-gray-500">
                    (Placeholder for AI-generated insights)
                  </p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>

        {/* Footer */}
        <CardFooter className="justify-end border-t bg-muted/40 py-4 px-6">
          <Button 
            onClick={onClose} 
            className="rounded-md bg-green-600 hover:bg-green-700 text-white"
          >
            Close
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
};

export default EventReportPopup;