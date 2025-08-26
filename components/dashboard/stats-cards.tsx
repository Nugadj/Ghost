"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Activity, Target, Users, Server, TrendingUp } from "lucide-react"

interface OperationStats {
  activeBeacons: number
  totalTargets: number
  activeListeners: number
  completedTasks: number
  successRate: number
  uptime: string
  threatLevel: "low" | "medium" | "high"
  networkCoverage: number
}

interface StatsCardsProps {
  stats: OperationStats
}

export function StatsCards({ stats }: StatsCardsProps) {
  const getThreatLevelColor = (level: string) => {
    switch (level) {
      case "low":
        return "bg-green-500"
      case "medium":
        return "bg-yellow-500"
      case "high":
        return "bg-red-500"
      default:
        return "bg-gray-500"
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <Card className="relative overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Active Beacons</CardTitle>
          <Target className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-primary">{stats.activeBeacons}</div>
          <div className="flex items-center gap-2 mt-2">
            <Progress value={(stats.activeBeacons / stats.totalTargets) * 100} className="flex-1" />
            <span className="text-xs text-muted-foreground">
              {Math.round((stats.activeBeacons / stats.totalTargets) * 100)}%
            </span>
          </div>
          <p className="text-xs text-muted-foreground mt-1">+2 from last hour</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Network Coverage</CardTitle>
          <Users className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.totalTargets}</div>
          <div className="flex items-center gap-2 mt-2">
            <Progress value={stats.networkCoverage} className="flex-1" />
            <span className="text-xs text-muted-foreground">{stats.networkCoverage}%</span>
          </div>
          <p className="text-xs text-muted-foreground mt-1">Across 3 subnets</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">C2 Infrastructure</CardTitle>
          <Server className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-green-500">{stats.activeListeners}</div>
          <div className="flex items-center gap-2 mt-2">
            <Badge variant="outline" className="text-xs">
              HTTP
            </Badge>
            <Badge variant="outline" className="text-xs">
              HTTPS
            </Badge>
            <Badge variant="outline" className="text-xs">
              DNS
            </Badge>
          </div>
          <p className="text-xs text-muted-foreground mt-1">All protocols active</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Operation Status</CardTitle>
          <Activity className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <div className="text-2xl font-bold">{stats.successRate}%</div>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </div>
          <div className="flex items-center gap-2 mt-2">
            <div className={`w-2 h-2 rounded-full ${getThreatLevelColor(stats.threatLevel)}`} />
            <span className="text-xs capitalize">{stats.threatLevel} threat level</span>
          </div>
          <p className="text-xs text-muted-foreground mt-1">Uptime: {stats.uptime}</p>
        </CardContent>
      </Card>
    </div>
  )
}
