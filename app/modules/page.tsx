"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import {
  Zap,
  Search,
  Settings,
  Play,
  Pause,
  Download,
  Upload,
  RefreshCw,
  Eye,
  Target,
  Shield,
  Users,
  FileText,
  Activity,
  CheckCircle,
  XCircle,
  Clock,
} from "lucide-react"

import { ModuleConfig } from "@/components/modules/module-config"
import { ModuleResults } from "@/components/modules/module-results"

interface ModuleData {
  id: string
  name: string
  category: "reconnaissance" | "weaponization" | "delivery" | "lateral_movement" | "user_exploitation" | "reporting"
  version: string
  description: string
  status: "loaded" | "unloaded" | "running" | "error"
  enabled: boolean
  lastRun: string
  capabilities: string[]
  config: Record<string, any>
  results?: {
    success: boolean
    output: string
    timestamp: string
  }
}

export default function ModulesPage() {
  const [modules, setModules] = useState<ModuleData[]>([])
  const [selectedModule, setSelectedModule] = useState<ModuleData | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [categoryFilter, setCategoryFilter] = useState<string>("all")
  const [isLoading, setIsLoading] = useState(false)

  // Mock module data
  useEffect(() => {
    const mockModules: ModuleData[] = [
      {
        id: "recon_001",
        name: "Network Scanner",
        category: "reconnaissance",
        version: "1.2.0",
        description: "Advanced network discovery and port scanning capabilities",
        status: "loaded",
        enabled: true,
        lastRun: "2024-01-15 14:32:15",
        capabilities: ["Port Scanning", "Service Detection", "OS Fingerprinting", "Vulnerability Assessment"],
        config: {
          target_range: "192.168.1.0/24",
          port_range: "1-1000",
          scan_type: "tcp",
          threads: 50,
          timeout: 5,
        },
        results: {
          success: true,
          output: "Scan completed: 15 hosts discovered, 45 open ports found",
          timestamp: "2024-01-15 14:35:22",
        },
      },
      {
        id: "weapon_001",
        name: "Payload Generator",
        category: "weaponization",
        version: "2.1.0",
        description: "Generate and customize various payload types for delivery",
        status: "loaded",
        enabled: true,
        lastRun: "2024-01-15 13:45:30",
        capabilities: ["Executable Generation", "Document Macros", "Script Payloads", "Obfuscation"],
        config: {
          payload_type: "windows_exe",
          architecture: "x64",
          encoder: "shikata_ga_nai",
          iterations: 3,
          template: "default",
        },
      },
      {
        id: "delivery_001",
        name: "Phishing Campaign",
        category: "delivery",
        version: "1.5.0",
        description: "Automated phishing email generation and campaign management",
        status: "running",
        enabled: true,
        lastRun: "2024-01-15 15:12:45",
        capabilities: ["Email Templates", "Target Management", "Tracking", "Analytics"],
        config: {
          smtp_server: "smtp.example.com",
          sender_email: "admin@company.com",
          template: "invoice_notification",
          target_list: "executives.csv",
        },
      },
      {
        id: "lateral_001",
        name: "SMB Pivot",
        category: "lateral_movement",
        version: "1.0.3",
        description: "Lateral movement through SMB shares and administrative access",
        status: "loaded",
        enabled: false,
        lastRun: "2024-01-15 12:22:10",
        capabilities: ["SMB Enumeration", "Share Access", "Credential Harvesting", "Remote Execution"],
        config: {
          target_hosts: ["192.168.1.10", "192.168.1.11"],
          credentials: "harvested_creds.txt",
          method: "psexec",
        },
      },
      {
        id: "exploit_001",
        name: "Keylogger",
        category: "user_exploitation",
        version: "1.3.0",
        description: "Capture user keystrokes and system activity",
        status: "loaded",
        enabled: true,
        lastRun: "2024-01-15 14:55:33",
        capabilities: ["Keystroke Logging", "Screenshot Capture", "Clipboard Monitoring", "Application Tracking"],
        config: {
          log_file: "keylog.txt",
          screenshot_interval: 300,
          filter_passwords: true,
          stealth_mode: true,
        },
      },
      {
        id: "report_001",
        name: "MITRE ATT&CK Reporter",
        category: "reporting",
        version: "2.0.0",
        description: "Generate comprehensive reports mapped to MITRE ATT&CK framework",
        status: "loaded",
        enabled: true,
        lastRun: "2024-01-15 16:00:00",
        capabilities: ["ATT&CK Mapping", "Timeline Generation", "Evidence Collection", "Executive Summary"],
        config: {
          output_format: "pdf",
          include_screenshots: true,
          classification: "confidential",
          template: "executive_summary",
        },
      },
    ]

    setModules(mockModules)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case "loaded":
        return "text-green-500"
      case "running":
        return "text-blue-500"
      case "error":
        return "text-red-500"
      case "unloaded":
        return "text-gray-500"
      default:
        return "text-gray-500"
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "loaded":
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case "running":
        return <Activity className="h-4 w-4 text-blue-500" />
      case "error":
        return <XCircle className="h-4 w-4 text-red-500" />
      case "unloaded":
        return <Clock className="h-4 w-4 text-gray-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "reconnaissance":
        return <Search className="h-5 w-5" />
      case "weaponization":
        return <Zap className="h-5 w-5" />
      case "delivery":
        return <Target className="h-5 w-5" />
      case "lateral_movement":
        return <Shield className="h-5 w-5" />
      case "user_exploitation":
        return <Users className="h-5 w-5" />
      case "reporting":
        return <FileText className="h-5 w-5" />
      default:
        return <Activity className="h-5 w-5" />
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "reconnaissance":
        return "bg-blue-500"
      case "weaponization":
        return "bg-purple-500"
      case "delivery":
        return "bg-orange-500"
      case "lateral_movement":
        return "bg-green-500"
      case "user_exploitation":
        return "bg-red-500"
      case "reporting":
        return "bg-gray-500"
      default:
        return "bg-gray-500"
    }
  }

  const filteredModules = modules.filter((module) => {
    const matchesSearch =
      module.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      module.description.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesCategory = categoryFilter === "all" || module.category === categoryFilter

    return matchesSearch && matchesCategory
  })

  const handleModuleToggle = (moduleId: string, enabled: boolean) => {
    setModules((prev) => prev.map((module) => (module.id === moduleId ? { ...module, enabled } : module)))
    console.log(`[v0] Module ${moduleId} ${enabled ? "enabled" : "disabled"}`)
  }

  const handleModuleAction = (action: string, moduleId: string) => {
    console.log(`[v0] Module action: ${action} on ${moduleId}`)

    setModules((prev) =>
      prev.map((module) => {
        if (module.id === moduleId) {
          switch (action) {
            case "run":
              return { ...module, status: "running" }
            case "stop":
              return { ...module, status: "loaded" }
            case "reload":
              return { ...module, status: "loaded", lastRun: new Date().toLocaleString() }
            default:
              return module
          }
        }
        return module
      }),
    )
  }

  const handleRefresh = async () => {
    setIsLoading(true)
    await new Promise((resolve) => setTimeout(resolve, 1000))
    setIsLoading(false)
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="flex h-16 items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <Zap className="h-8 w-8 text-primary" />
            <h1 className="text-2xl font-bold">Module Management</h1>
            <Badge variant="outline">{filteredModules.length} modules</Badge>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleRefresh} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
            <Button variant="outline" size="sm">
              <Upload className="h-4 w-4 mr-2" />
              Load Module
            </Button>
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export Config
            </Button>
          </div>
        </div>
      </header>

      <div className="p-6">
        {/* Filters and Search */}
        <div className="flex items-center gap-4 mb-6">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search modules..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>

          <Select value={categoryFilter} onValueChange={setCategoryFilter}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Filter by category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Categories</SelectItem>
              <SelectItem value="reconnaissance">Reconnaissance</SelectItem>
              <SelectItem value="weaponization">Weaponization</SelectItem>
              <SelectItem value="delivery">Delivery</SelectItem>
              <SelectItem value="lateral_movement">Lateral Movement</SelectItem>
              <SelectItem value="user_exploitation">User Exploitation</SelectItem>
              <SelectItem value="reporting">Reporting</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Module Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Modules</CardTitle>
              <Zap className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{modules.length}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Loaded</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-500">
                {modules.filter((m) => m.status === "loaded").length}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Running</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-500">
                {modules.filter((m) => m.status === "running").length}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Enabled</CardTitle>
              <Settings className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{modules.filter((m) => m.enabled).length}</div>
            </CardContent>
          </Card>
        </div>

        {/* Modules Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredModules.map((module) => (
            <Card key={module.id} className="relative">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${getCategoryColor(module.category)}`}>
                      {getCategoryIcon(module.category)}
                    </div>
                    <div>
                      <CardTitle className="text-lg">{module.name}</CardTitle>
                      <CardDescription>v{module.version}</CardDescription>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusIcon(module.status)}
                    <Switch
                      checked={module.enabled}
                      onCheckedChange={(enabled) => handleModuleToggle(module.id, enabled)}
                    />
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">{module.description}</p>

                <div className="flex items-center justify-between">
                  <Badge variant="outline" className="capitalize">
                    {module.category.replace("_", " ")}
                  </Badge>
                  <span className={`text-sm font-medium ${getStatusColor(module.status)}`}>
                    {module.status.toUpperCase()}
                  </span>
                </div>

                <div className="space-y-2">
                  <div className="text-xs text-muted-foreground">Capabilities:</div>
                  <div className="flex flex-wrap gap-1">
                    {module.capabilities.slice(0, 3).map((capability) => (
                      <Badge key={capability} variant="secondary" className="text-xs">
                        {capability}
                      </Badge>
                    ))}
                    {module.capabilities.length > 3 && (
                      <Badge variant="secondary" className="text-xs">
                        +{module.capabilities.length - 3} more
                      </Badge>
                    )}
                  </div>
                </div>

                <div className="text-xs text-muted-foreground">Last run: {module.lastRun}</div>

                <div className="flex items-center gap-2">
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1 bg-transparent"
                        onClick={() => setSelectedModule(module)}
                      >
                        <Settings className="h-4 w-4 mr-2" />
                        Configure
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-2xl">
                      <DialogHeader>
                        <DialogTitle>Configure {module.name}</DialogTitle>
                        <DialogDescription>Modify module settings and parameters</DialogDescription>
                      </DialogHeader>
                      {selectedModule && <ModuleConfig module={selectedModule} />}
                    </DialogContent>
                  </Dialog>

                  {module.status === "running" ? (
                    <Button variant="outline" size="sm" onClick={() => handleModuleAction("stop", module.id)}>
                      <Pause className="h-4 w-4" />
                    </Button>
                  ) : (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleModuleAction("run", module.id)}
                      disabled={!module.enabled}
                    >
                      <Play className="h-4 w-4" />
                    </Button>
                  )}

                  {module.results && (
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-3xl">
                        <DialogHeader>
                          <DialogTitle>{module.name} Results</DialogTitle>
                          <DialogDescription>Latest execution results and output</DialogDescription>
                        </DialogHeader>
                        <ModuleResults module={module} />
                      </DialogContent>
                    </Dialog>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
