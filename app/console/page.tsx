"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Terminal, Send, History, Download, Upload, Trash2, Settings, Target, Server, Users, Zap } from "lucide-react"

interface ConsoleEntry {
  id: string
  type: "command" | "output" | "error" | "system" | "info"
  content: string
  timestamp: string
  source?: string
}

interface BeaconSession {
  id: string
  hostname: string
  ip: string
  status: "active" | "inactive"
}

export default function ConsolePage() {
  const [command, setCommand] = useState("")
  const [history, setHistory] = useState<ConsoleEntry[]>([])
  const [commandHistory, setCommandHistory] = useState<string[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const [isExecuting, setIsExecuting] = useState(false)
  const [activeSession, setActiveSession] = useState<string>("global")
  const [beaconSessions] = useState<BeaconSession[]>([
    { id: "beacon_001", hostname: "DESKTOP-ABC123", ip: "192.168.1.100", status: "active" },
    { id: "beacon_002", hostname: "LAPTOP-XYZ789", ip: "192.168.1.101", status: "inactive" },
  ])

  const scrollAreaRef = useRef<HTMLDivElement>(null)

  // Initialize with welcome message
  useEffect(() => {
    const welcomeEntries: ConsoleEntry[] = [
      {
        id: "welcome",
        type: "system",
        content: "Ghost Protocol Interactive Console v1.0",
        timestamp: new Date().toLocaleTimeString(),
      },
      {
        id: "help_hint",
        type: "info",
        content: "Type 'help' for available commands or 'beacon <id>' to interact with a specific beacon",
        timestamp: new Date().toLocaleTimeString(),
      },
    ]
    setHistory(welcomeEntries)
  }, [])

  // Auto-scroll to bottom when new entries are added
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [history])

  const executeCommand = async (cmd: string) => {
    if (!cmd.trim()) return

    setIsExecuting(true)

    // Add command to history
    const commandEntry: ConsoleEntry = {
      id: `cmd_${Date.now()}`,
      type: "command",
      content: `ghost> ${cmd}`,
      timestamp: new Date().toLocaleTimeString(),
      source: activeSession,
    }

    setHistory((prev) => [...prev, commandEntry])
    setCommandHistory((prev) => [cmd, ...prev.slice(0, 49)]) // Keep last 50 commands
    setCommand("")

    // Simulate command execution
    await new Promise((resolve) => setTimeout(resolve, 800))

    // Process command
    const result = await processCommand(cmd.trim())

    const outputEntry: ConsoleEntry = {
      id: `out_${Date.now()}`,
      type: result.type,
      content: result.content,
      timestamp: new Date().toLocaleTimeString(),
      source: activeSession,
    }

    setHistory((prev) => [...prev, outputEntry])
    setIsExecuting(false)
  }

  const processCommand = async (cmd: string): Promise<{ type: "output" | "error" | "info"; content: string }> => {
    const parts = cmd.toLowerCase().split(" ")
    const command = parts[0]
    const args = parts.slice(1)

    switch (command) {
      case "help":
        return {
          type: "info",
          content: `Available Commands:

GLOBAL COMMANDS:
  help                    - Show this help message
  status                  - Show system status
  beacons                 - List all beacons
  listeners               - List all listeners
  modules                 - List loaded modules
  beacon <id>             - Switch to beacon session
  global                  - Switch to global session
  clear                   - Clear console
  history                 - Show command history
  
BEACON COMMANDS (when connected to a beacon):
  whoami                  - Show current user
  pwd                     - Show current directory
  ls / dir                - List directory contents
  cd <path>               - Change directory
  ps                      - List processes
  sysinfo                 - Show system information
  download <file>         - Download file
  upload <file>           - Upload file
  shell <command>         - Execute shell command
  
MODULE COMMANDS:
  recon <target>          - Run reconnaissance
  exploit <target>        - Run exploitation module
  lateral <method>        - Attempt lateral movement
  
LISTENER COMMANDS:
  listener start <name>   - Start a listener
  listener stop <name>    - Stop a listener
  listener list           - List all listeners`,
        }

      case "status":
        return {
          type: "output",
          content: `Ghost Protocol Status:
  Active Beacons: ${beaconSessions.filter((b) => b.status === "active").length}
  Total Beacons: ${beaconSessions.length}
  Active Listeners: 2
  Loaded Modules: 6
  Current Session: ${activeSession === "global" ? "Global Console" : `Beacon ${activeSession}`}
  Uptime: 02:34:15`,
        }

      case "beacons":
        const beaconList = beaconSessions
          .map(
            (beacon) =>
              `  ${beacon.id.padEnd(15)} ${beacon.hostname.padEnd(20)} ${beacon.ip.padEnd(15)} ${beacon.status}`,
          )
          .join("\n")
        return {
          type: "output",
          content: `Active Beacons:
  ID              Hostname             IP              Status
  ============================================================
${beaconList}`,
        }

      case "listeners":
        return {
          type: "output",
          content: `Active Listeners:
  Name              Protocol    Host         Port    Status
  ========================================================
  HTTP Listener     HTTP        0.0.0.0      8080    Running
  HTTPS Listener    HTTPS       0.0.0.0      8443    Running
  DNS Listener      DNS         0.0.0.0      53      Stopped`,
        }

      case "modules":
        return {
          type: "output",
          content: `Loaded Modules:
  reconnaissance    - Network and host discovery
  weaponization     - Payload generation and delivery
  delivery          - Phishing and social engineering
  lateral_movement  - Network propagation techniques
  user_exploitation - User activity monitoring
  reporting         - Operation reporting and analysis`,
        }

      case "beacon":
        if (args.length === 0) {
          return { type: "error", content: "Usage: beacon <beacon_id>" }
        }
        const beaconId = args[0]
        const beacon = beaconSessions.find((b) => b.id === beaconId)
        if (!beacon) {
          return { type: "error", content: `Beacon '${beaconId}' not found` }
        }
        setActiveSession(beaconId)
        return {
          type: "info",
          content: `Switched to beacon session: ${beacon.hostname} (${beacon.ip})`,
        }

      case "global":
        setActiveSession("global")
        return { type: "info", content: "Switched to global console session" }

      case "clear":
        setHistory([])
        return { type: "info", content: "Console cleared" }

      case "history":
        const historyList = commandHistory
          .slice(0, 10)
          .map((cmd, index) => `  ${(index + 1).toString().padStart(2)}: ${cmd}`)
          .join("\n")
        return {
          type: "output",
          content: `Recent Command History:\n${historyList}`,
        }

      case "recon":
        if (args.length === 0) {
          return { type: "error", content: "Usage: recon <target>" }
        }
        return {
          type: "output",
          content: `Starting reconnaissance on ${args[0]}...
  [+] Port scan initiated
  [+] Service enumeration started
  [+] OS fingerprinting in progress
  [+] Scan completed - 5 open ports found`,
        }

      case "listener":
        if (args.length < 2) {
          return { type: "error", content: "Usage: listener <start|stop|list> [name]" }
        }
        const action = args[0]
        const listenerName = args[1]

        switch (action) {
          case "start":
            return { type: "output", content: `Starting listener: ${listenerName}` }
          case "stop":
            return { type: "output", content: `Stopping listener: ${listenerName}` }
          case "list":
            return { type: "output", content: "Use 'listeners' command to list all listeners" }
          default:
            return { type: "error", content: "Invalid listener action. Use start, stop, or list" }
        }

      // Beacon-specific commands (when connected to a beacon)
      case "whoami":
        if (activeSession === "global") {
          return { type: "error", content: "This command requires an active beacon session. Use 'beacon <id>' first." }
        }
        const currentBeacon = beaconSessions.find((b) => b.id === activeSession)
        return { type: "output", content: `CORP\\john.doe` }

      case "pwd":
        if (activeSession === "global") {
          return { type: "error", content: "This command requires an active beacon session. Use 'beacon <id>' first." }
        }
        return { type: "output", content: "C:\\Users\\john.doe" }

      case "ls":
      case "dir":
        if (activeSession === "global") {
          return { type: "error", content: "This command requires an active beacon session. Use 'beacon <id>' first." }
        }
        return {
          type: "output",
          content: `Directory of C:\\Users\\john.doe

01/15/2024  02:30 PM    <DIR>          .
01/15/2024  02:30 PM    <DIR>          ..
01/15/2024  02:30 PM    <DIR>          Desktop
01/15/2024  02:30 PM    <DIR>          Documents
01/15/2024  02:30 PM    <DIR>          Downloads
               0 File(s)              0 bytes
               3 Dir(s)  125,234,567,890 bytes free`,
        }

      case "sysinfo":
        if (activeSession === "global") {
          return { type: "error", content: "This command requires an active beacon session. Use 'beacon <id>' first." }
        }
        return {
          type: "output",
          content: `Computer Name: DESKTOP-ABC123
OS Name: Microsoft Windows 11 Pro
OS Version: 10.0.22000 Build 22000
System Type: x64-based PC
Total Physical Memory: 16,384 MB
Available Physical Memory: 8,192 MB
Processor: Intel(R) Core(TM) i7-12700K CPU @ 3.60GHz`,
        }

      default:
        return { type: "error", content: `Unknown command: '${command}'. Type 'help' for available commands.` }
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      executeCommand(command)
    } else if (e.key === "ArrowUp") {
      e.preventDefault()
      if (historyIndex < commandHistory.length - 1) {
        const newIndex = historyIndex + 1
        setHistoryIndex(newIndex)
        setCommand(commandHistory[newIndex])
      }
    } else if (e.key === "ArrowDown") {
      e.preventDefault()
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1
        setHistoryIndex(newIndex)
        setCommand(commandHistory[newIndex])
      } else if (historyIndex === 0) {
        setHistoryIndex(-1)
        setCommand("")
      }
    } else if (e.key === "Tab") {
      e.preventDefault()
      // Basic command completion
      const suggestions = ["help", "status", "beacons", "listeners", "modules", "beacon", "global", "clear", "history"]
      const matches = suggestions.filter((s) => s.startsWith(command.toLowerCase()))
      if (matches.length === 1) {
        setCommand(matches[0])
      }
    }
  }

  const clearConsole = () => {
    setHistory([])
  }

  const getEntryColor = (type: string) => {
    switch (type) {
      case "command":
        return "text-primary"
      case "error":
        return "text-red-500"
      case "system":
        return "text-yellow-500"
      case "info":
        return "text-blue-500"
      default:
        return "text-foreground"
    }
  }

  const getSessionBadge = () => {
    if (activeSession === "global") {
      return <Badge variant="outline">Global</Badge>
    }
    const beacon = beaconSessions.find((b) => b.id === activeSession)
    return beacon ? (
      <Badge variant={beacon.status === "active" ? "default" : "secondary"}>{beacon.hostname}</Badge>
    ) : (
      <Badge variant="outline">Unknown</Badge>
    )
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="flex h-16 items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <Terminal className="h-8 w-8 text-primary" />
            <h1 className="text-2xl font-bold">Interactive Console</h1>
            {getSessionBadge()}
          </div>

          <div className="flex items-center gap-2">
            <Select value={activeSession} onValueChange={setActiveSession}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Select session" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="global">Global Console</SelectItem>
                {beaconSessions.map((beacon) => (
                  <SelectItem key={beacon.id} value={beacon.id}>
                    {beacon.hostname} ({beacon.ip})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Button variant="outline" size="sm" onClick={clearConsole}>
              <Trash2 className="h-4 w-4 mr-2" />
              Clear
            </Button>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  <Settings className="h-4 w-4 mr-2" />
                  Options
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuLabel>Console Options</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <Download className="h-4 w-4 mr-2" />
                  Export History
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Upload className="h-4 w-4 mr-2" />
                  Import Script
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <History className="h-4 w-4 mr-2" />
                  Command History
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      <div className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Console */}
          <div className="lg:col-span-3">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Console Output</span>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <span>Session: {activeSession === "global" ? "Global" : activeSession}</span>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <ScrollArea className="h-[500px] p-4 font-mono text-sm" ref={scrollAreaRef}>
                  <div className="space-y-1">
                    {history.map((entry) => (
                      <div key={entry.id} className={`${getEntryColor(entry.type)} whitespace-pre-wrap`}>
                        <span className="text-muted-foreground text-xs mr-2">[{entry.timestamp}]</span>
                        {entry.content}
                      </div>
                    ))}
                    {isExecuting && (
                      <div className="text-muted-foreground">
                        <span className="text-xs mr-2">[{new Date().toLocaleTimeString()}]</span>
                        Executing command...
                      </div>
                    )}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Command Input */}
            <div className="flex items-center gap-2 mt-4">
              <div className="flex-1 relative">
                <Input
                  value={command}
                  onChange={(e) => setCommand(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Enter command... (Tab for completion, ↑↓ for history)"
                  disabled={isExecuting}
                  className="font-mono"
                />
              </div>
              <Button onClick={() => executeCommand(command)} disabled={isExecuting || !command.trim()}>
                <Send className="h-4 w-4" />
              </Button>
            </div>

            {/* Quick Commands */}
            <div className="flex flex-wrap gap-2 mt-4">
              <Button variant="outline" size="sm" onClick={() => setCommand("help")} disabled={isExecuting}>
                help
              </Button>
              <Button variant="outline" size="sm" onClick={() => setCommand("status")} disabled={isExecuting}>
                status
              </Button>
              <Button variant="outline" size="sm" onClick={() => setCommand("beacons")} disabled={isExecuting}>
                beacons
              </Button>
              <Button variant="outline" size="sm" onClick={() => setCommand("listeners")} disabled={isExecuting}>
                listeners
              </Button>
              <Button variant="outline" size="sm" onClick={() => setCommand("modules")} disabled={isExecuting}>
                modules
              </Button>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Active Sessions */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Active Sessions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div
                  className={`p-2 rounded cursor-pointer ${
                    activeSession === "global" ? "bg-primary/20" : "hover:bg-muted"
                  }`}
                  onClick={() => setActiveSession("global")}
                >
                  <div className="flex items-center gap-2">
                    <Terminal className="h-4 w-4" />
                    <span className="text-sm">Global Console</span>
                  </div>
                </div>
                {beaconSessions.map((beacon) => (
                  <div
                    key={beacon.id}
                    className={`p-2 rounded cursor-pointer ${
                      activeSession === beacon.id ? "bg-primary/20" : "hover:bg-muted"
                    }`}
                    onClick={() => setActiveSession(beacon.id)}
                  >
                    <div className="flex items-center gap-2">
                      <Target className="h-4 w-4" />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium truncate">{beacon.hostname}</div>
                        <div className="text-xs text-muted-foreground">{beacon.ip}</div>
                      </div>
                      <div
                        className={`w-2 h-2 rounded-full ${
                          beacon.status === "active" ? "bg-green-500" : "bg-gray-500"
                        }`}
                      />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button variant="outline" size="sm" className="w-full justify-start bg-transparent">
                  <Target className="h-4 w-4 mr-2" />
                  New Beacon
                </Button>
                <Button variant="outline" size="sm" className="w-full justify-start bg-transparent">
                  <Server className="h-4 w-4 mr-2" />
                  Start Listener
                </Button>
                <Button variant="outline" size="sm" className="w-full justify-start bg-transparent">
                  <Zap className="h-4 w-4 mr-2" />
                  Load Module
                </Button>
                <Button variant="outline" size="sm" className="w-full justify-start bg-transparent">
                  <Users className="h-4 w-4 mr-2" />
                  Scan Network
                </Button>
              </CardContent>
            </Card>

            {/* Command History */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Recent Commands</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-1">
                  {commandHistory.slice(0, 5).map((cmd, index) => (
                    <div
                      key={index}
                      className="text-xs font-mono text-muted-foreground cursor-pointer hover:text-foreground"
                      onClick={() => setCommand(cmd)}
                    >
                      {cmd}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
