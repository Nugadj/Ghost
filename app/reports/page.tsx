"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  FileText,
  Download,
  Calendar,
  Clock,
  Target,
  Shield,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Activity,
  Users,
  Server,
  Eye,
} from "lucide-react"
import Link from "next/link"

interface ReportData {
  id: string
  name: string
  type: "executive" | "technical" | "compliance"
  status: "completed" | "generating" | "failed"
  createdAt: string
  duration: string
  findings: number
  severity: "low" | "medium" | "high" | "critical"
}

export default function ReportsPage() {
  const [selectedTimeRange, setSelectedTimeRange] = useState("7d")
  const [selectedReportType, setSelectedReportType] = useState("all")

  const reports: ReportData[] = [
    {
      id: "1",
      name: "Q4 2024 Red Team Assessment",
      type: "executive",
      status: "completed",
      createdAt: "2024-12-15",
      duration: "2h 34m",
      findings: 23,
      severity: "high",
    },
    {
      id: "2",
      name: "Network Penetration Test - Technical",
      type: "technical",
      status: "completed",
      createdAt: "2024-12-14",
      duration: "4h 12m",
      findings: 45,
      severity: "critical",
    },
    {
      id: "3",
      name: "Compliance Assessment Report",
      type: "compliance",
      status: "generating",
      createdAt: "2024-12-16",
      duration: "1h 23m",
      findings: 12,
      severity: "medium",
    },
  ]

  const operationStats = {
    totalOperations: 15,
    successfulCompromises: 12,
    averageDwellTime: "4.2 days",
    detectionRate: "23%",
    criticalFindings: 8,
    highFindings: 15,
    mediumFindings: 32,
    lowFindings: 18,
  }

  const mitreStats = [
    { tactic: "Initial Access", techniques: 5, success: 4 },
    { tactic: "Execution", techniques: 8, success: 7 },
    { tactic: "Persistence", techniques: 6, success: 3 },
    { tactic: "Privilege Escalation", techniques: 4, success: 4 },
    { tactic: "Defense Evasion", techniques: 12, success: 9 },
    { tactic: "Credential Access", techniques: 7, success: 5 },
    { tactic: "Discovery", techniques: 9, success: 8 },
    { tactic: "Lateral Movement", techniques: 5, success: 4 },
    { tactic: "Collection", techniques: 6, success: 3 },
    { tactic: "Exfiltration", techniques: 3, success: 2 },
  ]

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="flex h-16 items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Shield className="h-8 w-8 text-primary" />
              <h1 className="text-2xl font-bold">Ghost Protocol</h1>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export All
            </Button>
            <Button size="sm">
              <FileText className="h-4 w-4 mr-2" />
              Generate Report
            </Button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 border-r border-border bg-sidebar min-h-[calc(100vh-4rem)]">
          <nav className="p-4 space-y-2">
            <Link href="/">
              <Button variant="ghost" className="w-full justify-start text-sidebar-foreground hover:bg-sidebar-accent">
                <Activity className="h-4 w-4 mr-2" />
                Dashboard
              </Button>
            </Link>
            <Link href="/beacons">
              <Button variant="ghost" className="w-full justify-start text-sidebar-foreground hover:bg-sidebar-accent">
                <Target className="h-4 w-4 mr-2" />
                Beacons
              </Button>
            </Link>
            <Button variant="ghost" className="w-full justify-start text-sidebar-foreground hover:bg-sidebar-accent">
              <Server className="h-4 w-4 mr-2" />
              Listeners
            </Button>
            <Button variant="ghost" className="w-full justify-start text-sidebar-foreground hover:bg-sidebar-accent">
              <Users className="h-4 w-4 mr-2" />
              Targets
            </Button>
            <Link href="/modules">
              <Button variant="ghost" className="w-full justify-start text-sidebar-foreground hover:bg-sidebar-accent">
                <Shield className="h-4 w-4 mr-2" />
                Modules
              </Button>
            </Link>
            <Button variant="default" className="w-full justify-start">
              <Eye className="h-4 w-4 mr-2" />
              Reports
            </Button>
            <Link href="/console">
              <Button variant="ghost" className="w-full justify-start text-sidebar-foreground hover:bg-sidebar-accent">
                <FileText className="h-4 w-4 mr-2" />
                Console
              </Button>
            </Link>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6">
          <div className="mb-6">
            <h2 className="text-3xl font-bold mb-2">Operation Reports</h2>
            <p className="text-muted-foreground">Comprehensive analysis and documentation of red team operations</p>
          </div>

          <Tabs defaultValue="overview" className="space-y-6">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="reports">Reports</TabsTrigger>
              <TabsTrigger value="mitre">MITRE ATT&CK</TabsTrigger>
              <TabsTrigger value="timeline">Timeline</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6">
              {/* Operation Statistics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Operations</CardTitle>
                    <Activity className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{operationStats.totalOperations}</div>
                    <p className="text-xs text-muted-foreground">Last 30 days</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
                    <TrendingUp className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {Math.round((operationStats.successfulCompromises / operationStats.totalOperations) * 100)}%
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {operationStats.successfulCompromises}/{operationStats.totalOperations} successful
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Avg. Dwell Time</CardTitle>
                    <Clock className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{operationStats.averageDwellTime}</div>
                    <p className="text-xs text-muted-foreground">Before detection</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Detection Rate</CardTitle>
                    <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{operationStats.detectionRate}</div>
                    <p className="text-xs text-muted-foreground">Operations detected</p>
                  </CardContent>
                </Card>
              </div>

              {/* Findings Summary */}
              <Card>
                <CardHeader>
                  <CardTitle>Findings Summary</CardTitle>
                  <CardDescription>Security findings categorized by severity</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-500">{operationStats.criticalFindings}</div>
                      <div className="text-sm text-muted-foreground">Critical</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-orange-500">{operationStats.highFindings}</div>
                      <div className="text-sm text-muted-foreground">High</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-yellow-500">{operationStats.mediumFindings}</div>
                      <div className="text-sm text-muted-foreground">Medium</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-500">{operationStats.lowFindings}</div>
                      <div className="text-sm text-muted-foreground">Low</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="reports" className="space-y-6">
              {/* Report Filters */}
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <Label htmlFor="search">Search Reports</Label>
                  <Input id="search" placeholder="Search by name or type..." />
                </div>
                <div>
                  <Label htmlFor="type">Report Type</Label>
                  <Select value={selectedReportType} onValueChange={setSelectedReportType}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Types</SelectItem>
                      <SelectItem value="executive">Executive</SelectItem>
                      <SelectItem value="technical">Technical</SelectItem>
                      <SelectItem value="compliance">Compliance</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="timerange">Time Range</Label>
                  <Select value={selectedTimeRange} onValueChange={setSelectedTimeRange}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="7d">Last 7 days</SelectItem>
                      <SelectItem value="30d">Last 30 days</SelectItem>
                      <SelectItem value="90d">Last 90 days</SelectItem>
                      <SelectItem value="1y">Last year</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Reports List */}
              <div className="space-y-4">
                {reports.map((report) => (
                  <Card key={report.id}>
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div className="space-y-2">
                          <div className="flex items-center gap-3">
                            <h3 className="text-lg font-semibold">{report.name}</h3>
                            <Badge variant="outline" className="capitalize">
                              {report.type}
                            </Badge>
                            <Badge
                              variant={
                                report.status === "completed"
                                  ? "default"
                                  : report.status === "generating"
                                    ? "secondary"
                                    : "destructive"
                              }
                            >
                              {report.status === "completed" && <CheckCircle className="h-3 w-3 mr-1" />}
                              {report.status === "generating" && <Clock className="h-3 w-3 mr-1" />}
                              {report.status === "failed" && <XCircle className="h-3 w-3 mr-1" />}
                              {report.status}
                            </Badge>
                          </div>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <Calendar className="h-4 w-4" />
                              {report.createdAt}
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock className="h-4 w-4" />
                              {report.duration}
                            </span>
                            <span className="flex items-center gap-1">
                              <Target className="h-4 w-4" />
                              {report.findings} findings
                            </span>
                            <Badge
                              variant={
                                report.severity === "critical"
                                  ? "destructive"
                                  : report.severity === "high"
                                    ? "destructive"
                                    : report.severity === "medium"
                                      ? "default"
                                      : "secondary"
                              }
                              className="text-xs"
                            >
                              {report.severity}
                            </Badge>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button variant="outline" size="sm">
                            <Eye className="h-4 w-4 mr-2" />
                            View
                          </Button>
                          <Button variant="outline" size="sm">
                            <Download className="h-4 w-4 mr-2" />
                            Download
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="mitre" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>MITRE ATT&CK Framework Coverage</CardTitle>
                  <CardDescription>Techniques tested and success rates across MITRE ATT&CK tactics</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {mitreStats.map((tactic) => (
                      <div key={tactic.tactic} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">{tactic.tactic}</span>
                          <span className="text-sm text-muted-foreground">
                            {tactic.success}/{tactic.techniques} successful
                          </span>
                        </div>
                        <div className="w-full bg-muted rounded-full h-2">
                          <div
                            className="bg-primary h-2 rounded-full transition-all duration-300"
                            style={{ width: `${(tactic.success / tactic.techniques) * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="timeline" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Operation Timeline</CardTitle>
                  <CardDescription>Chronological view of red team activities and milestones</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {[
                      {
                        time: "14:32:15",
                        phase: "Reconnaissance",
                        event: "Network discovery initiated",
                        details: "Scanning 192.168.1.0/24 subnet for active hosts",
                        severity: "low",
                      },
                      {
                        time: "14:35:22",
                        phase: "Initial Access",
                        event: "Phishing email delivered",
                        details: "Malicious document sent to 25 targets",
                        severity: "medium",
                      },
                      {
                        time: "14:38:45",
                        phase: "Execution",
                        event: "Payload executed successfully",
                        details: "PowerShell script executed on DESKTOP-ABC123",
                        severity: "high",
                      },
                      {
                        time: "14:42:10",
                        phase: "Persistence",
                        event: "Beacon established",
                        details: "Persistent connection established with C2 server",
                        severity: "high",
                      },
                    ].map((event, index) => (
                      <div key={index} className="flex gap-4">
                        <div className="flex flex-col items-center">
                          <div
                            className={`w-3 h-3 rounded-full ${
                              event.severity === "high"
                                ? "bg-red-500"
                                : event.severity === "medium"
                                  ? "bg-yellow-500"
                                  : "bg-blue-500"
                            }`}
                          />
                          {index < 3 && <div className="w-px h-8 bg-border mt-2" />}
                        </div>
                        <div className="flex-1 space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-muted-foreground">{event.time}</span>
                            <Badge variant="outline" className="text-xs">
                              {event.phase}
                            </Badge>
                          </div>
                          <h4 className="font-medium">{event.event}</h4>
                          <p className="text-sm text-muted-foreground">{event.details}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </main>
      </div>
    </div>
  )
}
