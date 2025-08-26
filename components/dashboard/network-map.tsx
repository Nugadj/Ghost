"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Network, Maximize2, RefreshCw } from "lucide-react"

interface NetworkNode {
  id: string
  hostname: string
  ip: string
  status: "active" | "inactive" | "compromised"
  os: string
  connections: string[]
}

interface NetworkMapProps {
  nodes: NetworkNode[]
}

export function NetworkMap({ nodes }: NetworkMapProps) {
  const getNodeColor = (status: string) => {
    switch (status) {
      case "compromised":
        return "bg-red-500"
      case "active":
        return "bg-green-500"
      case "inactive":
        return "bg-gray-500"
      default:
        return "bg-gray-500"
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Network className="h-5 w-5" />
              Network Topology
            </CardTitle>
            <CardDescription>Visual representation of compromised network</CardDescription>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm">
              <Maximize2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="relative h-[300px] bg-muted/20 rounded-lg p-4 overflow-hidden">
          {/* Network visualization placeholder */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="grid grid-cols-3 gap-8">
              {nodes.slice(0, 9).map((node, index) => (
                <div key={node.id} className="relative">
                  <div
                    className={`w-12 h-12 rounded-full ${getNodeColor(
                      node.status,
                    )} flex items-center justify-center text-white text-xs font-bold shadow-lg`}
                  >
                    {node.hostname.slice(0, 2).toUpperCase()}
                  </div>
                  <div className="absolute -bottom-6 left-1/2 transform -translate-x-1/2">
                    <Badge variant="outline" className="text-xs">
                      {node.ip}
                    </Badge>
                  </div>
                  {/* Connection lines would be drawn here in a real implementation */}
                  {index < 8 && <div className="absolute top-6 left-12 w-8 h-0.5 bg-border transform rotate-45" />}
                </div>
              ))}
            </div>
          </div>
        </div>
        <div className="flex items-center justify-between mt-4">
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <span>Compromised ({nodes.filter((n) => n.status === "compromised").length})</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span>Active ({nodes.filter((n) => n.status === "active").length})</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-gray-500" />
              <span>Inactive ({nodes.filter((n) => n.status === "inactive").length})</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
