"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { Terminal, Send, Download, Upload, Trash2 } from "lucide-react"

interface BeaconData {
  id: string
  hostname: string
  ip: string
  username: string
  os: string
  status: "active" | "inactive" | "lost"
}

interface ConsoleEntry {
  id: string
  type: "command" | "output" | "error" | "system"
  content: string
  timestamp: string
}

interface BeaconConsoleProps {
  beacon: BeaconData
}

export function BeaconConsole({ beacon }: BeaconConsoleProps) {
  const [command, setCommand] = useState("")
  const [history, setHistory] = useState<ConsoleEntry[]>([])
  const [commandHistory, setCommandHistory] = useState<string[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const [isExecuting, setIsExecuting] = useState(false)
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  // Initialize with welcome message
  useEffect(() => {
    const welcomeEntry: ConsoleEntry = {
      id: "welcome",
      type: "system",
      content: `Connected to ${beacon.hostname} (${beacon.ip}) as ${beacon.username}`,
      timestamp: new Date().toLocaleTimeString(),
    }
    setHistory([welcomeEntry])
  }, [beacon])

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
      content: `${beacon.username}@${beacon.hostname}:~$ ${cmd}`,
      timestamp: new Date().toLocaleTimeString(),
    }

    setHistory((prev) => [...prev, commandEntry])
    setCommandHistory((prev) => [cmd, ...prev.slice(0, 49)]) // Keep last 50 commands
    setCommand("")

    // Simulate command execution
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // Mock command responses
    let output = ""
    let type: "output" | "error" = "output"

    switch (cmd.toLowerCase().trim()) {
      case "whoami":
        output = `${beacon.username}`
        break
      case "pwd":
        output = "C:\\Users\\john.doe"
        break
      case "ls":
      case "dir":
        output = `Directory of C:\\Users\\john.doe

01/15/2024  02:30 PM    <DIR>          .
01/15/2024  02:30 PM    <DIR>          ..
01/15/2024  02:30 PM    <DIR>          Desktop
01/15/2024  02:30 PM    <DIR>          Documents
01/15/2024  02:30 PM    <DIR>          Downloads
01/15/2024  02:30 PM    <DIR>          Pictures
               0 File(s)              0 bytes
               6 Dir(s)  125,234,567,890 bytes free`
        break
      case "sysinfo":
        output = `Computer Name: ${beacon.hostname}
OS Name: ${beacon.os}
OS Version: 10.0.22000 Build 22000
System Type: x64-based PC
Total Physical Memory: 16,384 MB
Available Physical Memory: 8,192 MB
Processor: Intel(R) Core(TM) i7-12700K CPU @ 3.60GHz`
        break
      case "ps":
      case "tasklist":
        output = `Image Name                     PID Session Name        Session#    Mem Usage
========================= ======== ================ =========== ============
System Idle Process              0 Services                   0          8 K
System                           4 Services                   0        140 K
smss.exe                       348 Services                   0      1,048 K
csrss.exe                      424 Services                   0      4,356 K
winlogon.exe                   448 Console                    1      5,792 K`
        break
      case "help":
        output = `Available commands:
  whoami     - Display current user
  pwd        - Show current directory
  ls/dir     - List directory contents
  sysinfo    - Display system information
  ps         - List running processes
  cd <path>  - Change directory
  cat <file> - Display file contents
  download <file> - Download file from target
  upload <file>   - Upload file to target
  shell <cmd>     - Execute shell command
  exit       - Close beacon session`
        break
      default:
        if (cmd.startsWith("cd ")) {
          output = `Changed directory to ${cmd.substring(3)}`
        } else if (cmd.startsWith("cat ")) {
          output = `File contents of ${cmd.substring(4)}:\n\nThis is a sample file content...`
        } else if (cmd.startsWith("shell ")) {
          output = `Executing: ${cmd.substring(6)}\n\nCommand executed successfully.`
        } else {
          output = `'${cmd}' is not recognized as an internal or external command.`
          type = "error"
        }
    }

    const outputEntry: ConsoleEntry = {
      id: `out_${Date.now()}`,
      type,
      content: output,
      timestamp: new Date().toLocaleTimeString(),
    }

    setHistory((prev) => [...prev, outputEntry])
    setIsExecuting(false)
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
      default:
        return "text-foreground"
    }
  }

  return (
    <div className="space-y-4">
      {/* Console Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Terminal className="h-5 w-5" />
          <span className="font-medium">Interactive Console</span>
          <Badge variant={beacon.status === "active" ? "default" : "secondary"}>{beacon.status}</Badge>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Upload className="h-4 w-4 mr-2" />
            Upload
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Download
          </Button>
          <Button variant="outline" size="sm" onClick={clearConsole}>
            <Trash2 className="h-4 w-4 mr-2" />
            Clear
          </Button>
        </div>
      </div>

      {/* Console Output */}
      <Card>
        <CardContent className="p-0">
          <ScrollArea className="h-[400px] p-4 font-mono text-sm" ref={scrollAreaRef}>
            <div className="space-y-2">
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
      <div className="flex items-center gap-2">
        <div className="flex-1 relative">
          <Input
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Enter command..."
            disabled={isExecuting || beacon.status !== "active"}
            className="font-mono"
          />
        </div>
        <Button
          onClick={() => executeCommand(command)}
          disabled={isExecuting || beacon.status !== "active" || !command.trim()}
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>

      {/* Quick Commands */}
      <div className="flex flex-wrap gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setCommand("whoami")}
          disabled={isExecuting || beacon.status !== "active"}
        >
          whoami
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setCommand("sysinfo")}
          disabled={isExecuting || beacon.status !== "active"}
        >
          sysinfo
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setCommand("ps")}
          disabled={isExecuting || beacon.status !== "active"}
        >
          ps
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setCommand("pwd")}
          disabled={isExecuting || beacon.status !== "active"}
        >
          pwd
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setCommand("help")}
          disabled={isExecuting || beacon.status !== "active"}
        >
          help
        </Button>
      </div>
    </div>
  )
}
