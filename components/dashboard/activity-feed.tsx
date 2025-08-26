"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Activity, Terminal, AlertTriangle, Shield, Target, CheckCircle, XCircle, Clock } from "lucide-react"

interface ActivityEvent {
  id: string
  type: "beacon" | "command" | "alert" | "system" | "success" | "error"
  title: string
  description: string
  timestamp: string
  severity: "low" | "medium" | "high"
}

interface ActivityFeedProps {
  events: ActivityEvent[]
}

export function ActivityFeed({ events }: ActivityFeedProps) {
  const getEventIcon = (type: string) => {
    switch (type) {
      case "beacon":
        return <Target className="h-4 w-4" />
      case "command":
        return <Terminal className="h-4 w-4" />
      case "alert":
        return <AlertTriangle className="h-4 w-4" />
      case "system":
        return <Shield className="h-4 w-4" />
      case "success":
        return <CheckCircle className="h-4 w-4" />
      case "error":
        return <XCircle className="h-4 w-4" />
      default:
        return <Activity className="h-4 w-4" />
    }
  }

  const getEventColor = (type: string, severity: string) => {
    if (type === "success") return "text-green-500 border-l-green-500"
    if (type === "error") return "text-red-500 border-l-red-500"
    if (type === "alert") {
      switch (severity) {
        case "high":
          return "text-red-500 border-l-red-500"
        case "medium":
          return "text-yellow-500 border-l-yellow-500"
        default:
          return "text-blue-500 border-l-blue-500"
      }
    }
    return "text-blue-500 border-l-blue-500"
  }

  return (
    <Card className="col-span-1 lg:col-span-2">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Real-time Activity Feed
        </CardTitle>
        <CardDescription>Live operation events and system alerts</CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px] pr-4">
          <div className="space-y-4">
            {events.map((event) => (
              <div
                key={event.id}
                className={`flex items-start gap-4 p-3 border-l-4 bg-card/50 rounded-r-lg ${getEventColor(
                  event.type,
                  event.severity,
                )}`}
              >
                <div className={getEventColor(event.type, event.severity)}>{getEventIcon(event.type)}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <div className="font-medium truncate">{event.title}</div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-xs">
                        {event.type}
                      </Badge>
                      <Clock className="h-3 w-3 text-muted-foreground" />
                      <span className="text-xs text-muted-foreground">{event.timestamp}</span>
                    </div>
                  </div>
                  <div className="text-sm text-muted-foreground mt-1">{event.description}</div>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
