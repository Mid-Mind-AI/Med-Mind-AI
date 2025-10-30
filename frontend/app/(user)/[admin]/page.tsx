"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Checkbox } from "@/components/ui/checkbox";
import { 
  Calendar, 
  Clock, 
  CheckCircle2, 
  Plus, 
  ChevronLeft, 
  ChevronRight,
  Zap,
  ListTodo,
  Calendar as CalendarIcon
} from "lucide-react";

export default function Admin() {
  const recommendedActions = [
    {
      id: 1,
      title: "Syed Just had a dental appointment",
      description: "He had a tooth extraction and a filling",
      source: "Dental Clinic",
      timeAgo: "1 hour ago",
      checked: false
    },
    {
      id: 2,
      title: "Syed Just had a dental appointment",
      description: "He had a tooth extraction and a filling",
      source: "Dental Clinic",
      timeAgo: "1 hour ago",
      checked: false
    },
    {
      id: 3,
      title: "Syed Just had a dental appointment",
      description: "He had a tooth extraction and a filling",
      source: "Dental Clinic",
      timeAgo: "1 hour ago",
      checked: false
    },
    {
      id: 4,
      title: "Syed Just had a dental appointment",
      description: "He had a tooth extraction and a filling",
      source: "Dental Clinic",
      timeAgo: "1 hour ago",
      checked: false
    },
    {
      id: 5,
      title: "Syed Just had a dental appointment",
      description: "He had a tooth extraction and a filling",
      source: "Dental Clinic",
      timeAgo: "1 hour ago",
      checked: false
    },
  ];

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Card className="h-full">
              <CardHeader className="flex flex-row items-center justify-between">
                <div className="flex items-center gap-2">
                  <Zap className="h-5 w-5 text-primary" />
                  <CardTitle>Recommended Actions (5)</CardTitle>
                </div>
                <div className="flex items-center gap-4">
                  <Button variant="outline" size="sm" className="gap-2">
                    <Clock className="h-4 w-4" />
                    Last 7 days
                  </Button>
                  <div className="flex items-center gap-2">
                    <Switch id="show-read" />
                    <label htmlFor="show-read" className="text-sm text-muted-foreground">
                      Show Read
                    </label>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {recommendedActions.map((action) => (
                  <div key={action.id} className="flex items-start gap-3 p-3 rounded-lg hover:bg-accent/50 transition-colors">
                    <Checkbox 
                      id={`action-${action.id}`}
                      className="mt-1"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center">
                          <div className="w-3 h-3 rounded bg-primary"></div>
                        </div>
                        <span className="text-sm text-muted-foreground">{action.source}</span>
                      </div>
                      <h3 className="font-semibold text-sm mb-1">{action.title}</h3>
                      <p className="text-sm text-muted-foreground mb-2">{action.description}</p>
                    </div>
                    <span className="text-xs text-muted-foreground whitespace-nowrap">
                      {action.timeAgo}
                    </span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <Button variant="outline" size="sm" className="gap-2">
                  <CalendarIcon className="h-4 w-4" />
                  Today
                </Button>
                <div className="flex items-center gap-1">
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="text-center py-8">
                <Calendar className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                <h3 className="font-semibold mb-2">Calendar not connected</h3>
                <p className="text-sm text-muted-foreground mb-6">
                  Connect your calendar to track meetings
                </p>
                <div className="space-y-2">
                  <Button className="w-full gap-2">
                    <Calendar className="h-4 w-4" />
                    Google Calendar
                  </Button>
                  <Button variant="outline" className="w-full gap-2">
                    <Calendar className="h-4 w-4" />
                    Outlook Calendar
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div className="flex items-center gap-2">
                  <ListTodo className="h-5 w-5 text-primary" />
                  <CardTitle>Tasks (0)</CardTitle>
                </div>
                <div className="flex items-center gap-2">
                  <Switch id="show-completed" />
                  <label htmlFor="show-completed" className="text-sm text-muted-foreground">
                    Show Completed
                  </label>
                </div>
              </CardHeader>
              <CardContent className="text-center py-8">
                <CheckCircle2 className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                <h3 className="font-semibold mb-2">All tasks completed</h3>
                <p className="text-sm text-muted-foreground mb-6">
                  Add any tasks you want to track here
                </p>
                <Button className="gap-2">
                  <Plus className="h-4 w-4" />
                  Add Task
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
