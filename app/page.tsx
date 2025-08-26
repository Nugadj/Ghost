"use client"

import { useState, useEffect } from "react"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { Header } from "@/components/layout/header"
import { Sidebar } from "@/components/layout/sidebar"

// Import dashboard components
import { StatsCards } from "@/components/dashboard/stats-cards"
import { ActivityFeed } from "@/components/dashboard/activity-feed"
import { NetworkMap } from "@/components/dashboard/network-map"
import { ThreatTimeline } from "@/components/dashboard/threat-timeline"

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

export default function GhostProtocolDashboard() {
  const [operationStats, setOperationStats] = useState<OperationStats>({
    activeBeacons: 0,
    totalTargets: 0,
    activeListeners: 0,
    completedTasks: 0,
    successRate: 0,
    uptime: "00:00:00",
    threatLevel: "low",
    networkCoverage: 0,
  })

  const [isConnected, setIsConnected] = useState(false)

  // Mock data for dashboard components
  const [activityEvents] = useState([
    {
      id: "1",
      type: "beacon" as const,
      title: "New beacon connected",
      description: "DESKTOP-ABC123 • 192.168.1.100 • Windows 11",
      timestamp: "2 minutes ago",
      severity: "low" as const,
    },
    {
      id: "2",
      type: "command" as const,
      title: "Command executed successfully",
      description: "whoami executed on DESKTOP-ABC123",
      timestamp: "5 minutes ago",
      severity: "low" as const,
    },
    {
      id: "3",
      type: "alert" as const,
      title: "Beacon lost connection",
      description: "LAPTOP-XYZ789 • Last seen 10 minutes ago",
      timestamp: "10 minutes ago",
      severity: "medium" as const,
    },
    {
      id: "4",
      type: "success" as const,
      title: "Lateral movement successful",
      description: "Pivoted to DC01 via SMB",
      timestamp: "15 minutes ago",
      severity: "high" as const,
    },
  ])

  const [networkNodes] = useState([
    {
      id: "1",
      hostname: "DESKTOP-ABC123",
      ip: "192.168.1.100",
      status: "compromised" as const,
      os: "Windows 11",
      connections: ["2"],
    },
    {
      id: "2",
      hostname: "LAPTOP-XYZ789",
      ip: "192.168.1.101",
      status: "inactive" as const,
      os: "Windows 10",
      connections: ["1", "3"],
    },
    {
      id: "3",
      hostname: "DC01",
      ip: "192.168.1.10",
      status: "active" as const,
      os: "Windows Server 2019",
      connections: ["2"],
    },
  ])

  const [threatEvents] = useState([
    {
      id: "1",
      timestamp: "14:32:15",
      phase: "Reconnaissance",
      technique: "Network Service Scanning",
      description: "Performed port scan on 192.168.1.0/24 subnet",
      severity: "low" as const,
      mitre_id: "T1046",
    },
    {
      id: "2",
      timestamp: "14:35:22",
      phase: "Initial Access",
      technique: "Spearphishing Attachment",
      description: "Malicious document opened by user john.doe",
      severity: "high" as const,
      mitre_id: "T1566.001",
    },
    {
      id: "3",
      timestamp: "14:38:45",
      phase: "Execution",
      technique: "PowerShell",
      description: "Executed PowerShell script for system enumeration",
      severity: "medium" as const,
      mitre_id: "T1059.001",
    },
  ])

  // Simulate real-time data updates
  useEffect(() => {
    const interval = setInterval(() => {
      setOperationStats({
        activeBeacons: 3,
        totalTargets: 15,
        activeListeners: 2,
        completedTasks: 12,
        successRate: 87,
        uptime: "02:34:15",
        threatLevel: "medium",
        networkCoverage: 73,
      })

      setIsConnected(true)
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  return (
    <ProtectedRoute requiredPermission="read">
      <div className="min-h-screen bg-background text-foreground">
        <Header isConnected={isConnected} />

        <div className="flex">
          <Sidebar />

          {/* Main Content */}
          <main className="flex-1 p-6">
            <StatsCards stats={operationStats} />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
              <ActivityFeed events={activityEvents} />
              <NetworkMap nodes={networkNodes} />
            </div>

            <div className="mt-6">
              <ThreatTimeline events={threatEvents} />
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  )
}
