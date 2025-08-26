"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Clock, AlertTriangle, Shield, Target } from "lucide-react"

interface ThreatEvent {
  id: string
  timestamp: string
  phase: string
  technique: string
  description: string
  severity: "low" | "medium" | "high"
  mitre_id: string
}

interface ThreatTimelineProps {
  events: ThreatEvent[]
}

export function ThreatTimeline({ events }: ThreatTimelineProps) {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high":
        return "bg-red-500"
      case "medium":
        return "bg-yellow-500"
      case "low":
        return "bg-green-500"
      default:
        return "bg-gray-500"
    }
  }

  const getPhaseIcon = (phase: string) => {
    switch (phase.toLowerCase()) {
      case "reconnaissance":
        return <Target className="h-4 w-4" />
      case "initial access":
        return <Shield className="h-4 w-4" />
      case "execution":
        return <AlertTriangle className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5" />
          MITRE ATT&CK Timeline
        </CardTitle>
        <CardDescription>Attack progression mapped to MITRE framework</CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px] pr-4">
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-border" />

            <div className="space-y-6">
              {events.map((event, index) => (
                <div key={event.id} className="relative flex items-start gap-4">
                  {/* Timeline dot */}
                  <div className={`relative z-10 w-3 h-3 rounded-full ${getSeverityColor(event.severity)} mt-2`} />

                  <div className="flex-1 min-w-0 pb-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {getPhaseIcon(event.phase)}
                        <span className="font-medium">{event.technique}</span>
                        <Badge variant="outline" className="text-xs">
                          {event.mitre_id}
                        </Badge>
                      </div>
                      <span className="text-xs text-muted-foreground">{event.timestamp}</span>
                    </div>

                    <div className="text-sm text-muted-foreground mb-2">{event.description}</div>

                    <div className="flex items-center gap-2">
                      <Badge variant="secondary" className="text-xs">
                        {event.phase}
                      </Badge>
                      <Badge variant={event.severity === "high" ? "destructive" : "outline"} className="text-xs">
                        {event.severity}
                      </Badge>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
