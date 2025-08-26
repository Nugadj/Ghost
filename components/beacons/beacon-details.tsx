"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Monitor, User, Activity, Settings } from "lucide-react"

interface BeaconData {
  id: string
  hostname: string
  ip: string
  username: string
  os: string
  architecture: string
  pid: number
  status: "active" | "inactive" | "lost"
  firstSeen: string
  lastSeen: string
  listener: string
  jitter: number
  sleep: number
  systemInfo: {
    processor: string
    memory: string
    domain: string
    privileges: string
  }
}

interface BeaconDetailsProps {
  beacon: BeaconData
}

export function BeaconDetails({ beacon }: BeaconDetailsProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "text-green-500"
      case "inactive":
        return "text-yellow-500"
      case "lost":
        return "text-red-500"
      default:
        return "text-gray-500"
    }
  }

  const getPrivilegeColor = (privileges: string) => {
    switch (privileges.toLowerCase()) {
      case "system":
        return "text-red-500"
      case "admin":
      case "administrator":
        return "text-yellow-500"
      case "user":
        return "text-blue-500"
      default:
        return "text-gray-500"
    }
  }

  return (
    <div className="space-y-6">
      {/* Basic Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Monitor className="h-5 w-5" />
            System Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-muted-foreground">Hostname</label>
              <div className="text-lg font-mono">{beacon.hostname}</div>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">IP Address</label>
              <div className="text-lg font-mono">{beacon.ip}</div>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Operating System</label>
              <div className="text-lg">{beacon.os}</div>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Architecture</label>
              <div className="text-lg">{beacon.architecture}</div>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Process ID</label>
              <div className="text-lg font-mono">{beacon.pid}</div>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Status</label>
              <div className={`text-lg font-medium ${getStatusColor(beacon.status)}`}>
                {beacon.status.toUpperCase()}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* User Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            User Context
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-muted-foreground">Username</label>
              <div className="text-lg font-mono">{beacon.username}</div>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Domain</label>
              <div className="text-lg">{beacon.systemInfo.domain}</div>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Privileges</label>
              <div className={`text-lg font-medium ${getPrivilegeColor(beacon.systemInfo.privileges)}`}>
                {beacon.systemInfo.privileges}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Hardware Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Hardware Details
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 gap-4">
            <div>
              <label className="text-sm font-medium text-muted-foreground">Processor</label>
              <div className="text-lg">{beacon.systemInfo.processor}</div>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Memory</label>
              <div className="text-lg">{beacon.systemInfo.memory}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Connection Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Connection Details
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-muted-foreground">Listener</label>
              <div className="text-lg">
                <Badge variant="outline">{beacon.listener}</Badge>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Sleep Interval</label>
              <div className="text-lg">{beacon.sleep}s</div>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Jitter</label>
              <div className="text-lg">{beacon.jitter}%</div>
            </div>
          </div>

          <Separator />

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-muted-foreground">First Seen</label>
              <div className="text-lg font-mono">{beacon.firstSeen}</div>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Last Seen</label>
              <div className="text-lg font-mono">{beacon.lastSeen}</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
