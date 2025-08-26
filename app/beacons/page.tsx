"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Target,
  Terminal,
  MoreHorizontal,
  Search,
  Filter,
  RefreshCw,
  Download,
  Upload,
  Trash2,
  Play,
  Pause,
  Info,
  Activity,
  Clock,
  Monitor,
} from "lucide-react"

import { BeaconDetails } from "@/components/beacons/beacon-details"
import { BeaconConsole } from "@/components/beacons/beacon-console"

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

export default function BeaconsPage() {
  const [beacons, setBeacons] = useState<BeaconData[]>([])
  const [selectedBeacon, setSelectedBeacon] = useState<BeaconData | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [isLoading, setIsLoading] = useState(false)

  // Mock beacon data
  useEffect(() => {
    const mockBeacons: BeaconData[] = [
      {
        id: "beacon_001",
        hostname: "DESKTOP-ABC123",
        ip: "192.168.1.100",
        username: "john.doe",
        os: "Windows 11 Pro",
        architecture: "x64",
        pid: 4532,
        status: "active",
        firstSeen: "2024-01-15 14:32:15",
        lastSeen: new Date().toLocaleString(),
        listener: "HTTPS Listener",
        jitter: 10,
        sleep: 60,
        systemInfo: {
          processor: "Intel Core i7-12700K",
          memory: "16 GB",
          domain: "CORP.LOCAL",
          privileges: "User",
        },
      },
      {
        id: "beacon_002",
        hostname: "LAPTOP-XYZ789",
        ip: "192.168.1.101",
        username: "jane.smith",
        os: "Windows 10 Enterprise",
        architecture: "x64",
        pid: 2156,
        status: "inactive",
        firstSeen: "2024-01-15 13:45:22",
        lastSeen: "2024-01-15 15:12:33",
        listener: "HTTP Listener",
        jitter: 20,
        sleep: 120,
        systemInfo: {
          processor: "AMD Ryzen 5 5600X",
          memory: "8 GB",
          domain: "CORP.LOCAL",
          privileges: "Admin",
        },
      },
      {
        id: "beacon_003",
        hostname: "SERVER-DC01",
        ip: "192.168.1.10",
        username: "administrator",
        os: "Windows Server 2019",
        architecture: "x64",
        pid: 1892,
        status: "lost",
        firstSeen: "2024-01-15 12:15:45",
        lastSeen: "2024-01-15 14:22:11",
        listener: "DNS Listener",
        jitter: 5,
        sleep: 30,
        systemInfo: {
          processor: "Intel Xeon E5-2690",
          memory: "32 GB",
          domain: "CORP.LOCAL",
          privileges: "System",
        },
      },
    ]

    setBeacons(mockBeacons)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-500"
      case "inactive":
        return "bg-yellow-500"
      case "lost":
        return "bg-red-500"
      default:
        return "bg-gray-500"
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return <Badge className="bg-green-500 hover:bg-green-600">Active</Badge>
      case "inactive":
        return <Badge variant="secondary">Inactive</Badge>
      case "lost":
        return <Badge variant="destructive">Lost</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  const filteredBeacons = beacons.filter((beacon) => {
    const matchesSearch =
      beacon.hostname.toLowerCase().includes(searchTerm.toLowerCase()) ||
      beacon.ip.includes(searchTerm) ||
      beacon.username.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesStatus = statusFilter === "all" || beacon.status === statusFilter

    return matchesSearch && matchesStatus
  })

  const handleRefresh = async () => {
    setIsLoading(true)
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000))
    setIsLoading(false)
  }

  const handleBeaconAction = (action: string, beaconId: string) => {
    console.log(`[v0] Beacon action: ${action} on ${beaconId}`)
    // Handle beacon actions like kill, sleep, etc.
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="flex h-16 items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <Target className="h-8 w-8 text-primary" />
            <h1 className="text-2xl font-bold">Beacon Management</h1>
            <Badge variant="outline">{filteredBeacons.length} beacons</Badge>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleRefresh} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export
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
              placeholder="Search beacons..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Status: {statusFilter === "all" ? "All" : statusFilter}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuLabel>Filter by Status</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => setStatusFilter("all")}>All</DropdownMenuItem>
              <DropdownMenuItem onClick={() => setStatusFilter("active")}>Active</DropdownMenuItem>
              <DropdownMenuItem onClick={() => setStatusFilter("inactive")}>Inactive</DropdownMenuItem>
              <DropdownMenuItem onClick={() => setStatusFilter("lost")}>Lost</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Beacons Table */}
        <Card>
          <CardHeader>
            <CardTitle>Active Beacons</CardTitle>
            <CardDescription>Manage and interact with compromised hosts</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Status</TableHead>
                  <TableHead>Hostname</TableHead>
                  <TableHead>IP Address</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>OS</TableHead>
                  <TableHead>Last Seen</TableHead>
                  <TableHead>Listener</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredBeacons.map((beacon) => (
                  <TableRow key={beacon.id} className="cursor-pointer hover:bg-muted/50">
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <div className={`w-3 h-3 rounded-full ${getStatusColor(beacon.status)}`} />
                        {getStatusBadge(beacon.status)}
                      </div>
                    </TableCell>
                    <TableCell className="font-medium">{beacon.hostname}</TableCell>
                    <TableCell>{beacon.ip}</TableCell>
                    <TableCell>{beacon.username}</TableCell>
                    <TableCell>{beacon.os}</TableCell>
                    <TableCell>{beacon.lastSeen}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{beacon.listener}</Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button variant="outline" size="sm" onClick={() => setSelectedBeacon(beacon)}>
                              <Terminal className="h-4 w-4" />
                            </Button>
                          </DialogTrigger>
                          <DialogContent className="max-w-4xl max-h-[80vh]">
                            <DialogHeader>
                              <DialogTitle>Beacon Console - {beacon.hostname}</DialogTitle>
                              <DialogDescription>Interactive command console for {beacon.ip}</DialogDescription>
                            </DialogHeader>
                            {selectedBeacon && <BeaconConsole beacon={selectedBeacon} />}
                          </DialogContent>
                        </Dialog>

                        <Dialog>
                          <DialogTrigger asChild>
                            <Button variant="outline" size="sm">
                              <Info className="h-4 w-4" />
                            </Button>
                          </DialogTrigger>
                          <DialogContent className="max-w-2xl">
                            <DialogHeader>
                              <DialogTitle>Beacon Details - {beacon.hostname}</DialogTitle>
                              <DialogDescription>Detailed information about this beacon</DialogDescription>
                            </DialogHeader>
                            <BeaconDetails beacon={beacon} />
                          </DialogContent>
                        </Dialog>

                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="outline" size="sm">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent>
                            <DropdownMenuLabel>Beacon Actions</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem onClick={() => handleBeaconAction("sleep", beacon.id)}>
                              <Pause className="h-4 w-4 mr-2" />
                              Sleep
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleBeaconAction("wake", beacon.id)}>
                              <Play className="h-4 w-4 mr-2" />
                              Wake
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleBeaconAction("upload", beacon.id)}>
                              <Upload className="h-4 w-4 mr-2" />
                              Upload File
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleBeaconAction("download", beacon.id)}>
                              <Download className="h-4 w-4 mr-2" />
                              Download File
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                              onClick={() => handleBeaconAction("kill", beacon.id)}
                              className="text-destructive"
                            >
                              <Trash2 className="h-4 w-4 mr-2" />
                              Kill Beacon
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Beacons</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-500">
                {beacons.filter((b) => b.status === "active").length}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Inactive Beacons</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-500">
                {beacons.filter((b) => b.status === "inactive").length}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Lost Beacons</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-500">{beacons.filter((b) => b.status === "lost").length}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Beacons</CardTitle>
              <Monitor className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{beacons.length}</div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
