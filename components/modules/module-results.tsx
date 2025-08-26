"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { CheckCircle, XCircle, Download, RefreshCw, Activity } from "lucide-react"

interface ModuleData {
  id: string
  name: string
  category: string
  results?: {
    success: boolean
    output: string
    timestamp: string
  }
}

interface ModuleResultsProps {
  module: ModuleData
}

export function ModuleResults({ module }: ModuleResultsProps) {
  if (!module.results) {
    return (
      <div className="text-center py-8">
        <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
        <p className="text-muted-foreground">No results available for this module</p>
      </div>
    )
  }

  const { results } = module

  // Mock detailed results based on module category
  const getDetailedResults = () => {
    switch (module.category) {
      case "reconnaissance":
        return {
          summary: "Network scan completed successfully",
          details: {
            "Hosts Discovered": 15,
            "Open Ports": 45,
            "Services Identified": 23,
            "Vulnerabilities Found": 3,
          },
          hosts: [
            { ip: "192.168.1.10", hostname: "DC01", ports: [53, 88, 135, 139, 445], os: "Windows Server 2019" },
            { ip: "192.168.1.100", hostname: "DESKTOP-ABC123", ports: [135, 139, 445], os: "Windows 11" },
            { ip: "192.168.1.101", hostname: "LAPTOP-XYZ789", ports: [135, 139], os: "Windows 10" },
          ],
        }

      case "weaponization":
        return {
          summary: "Payload generated successfully",
          details: {
            "Payload Size": "2.3 MB",
            Encoding: "shikata_ga_nai x3",
            Architecture: "x64",
            Format: "Windows PE",
          },
          artifacts: [
            { name: "payload.exe", size: "2.3 MB", hash: "a1b2c3d4e5f6..." },
            { name: "payload.ps1", size: "15 KB", hash: "f6e5d4c3b2a1..." },
          ],
        }

      case "delivery":
        return {
          summary: "Phishing campaign executed",
          details: {
            "Emails Sent": 25,
            Delivered: 23,
            Opened: 12,
            Clicked: 5,
          },
          targets: [
            { email: "john.doe@company.com", status: "clicked", timestamp: "14:32:15" },
            { email: "jane.smith@company.com", status: "opened", timestamp: "14:45:22" },
            { email: "admin@company.com", status: "delivered", timestamp: "14:30:10" },
          ],
        }

      default:
        return {
          summary: results.output,
          details: {},
        }
    }
  }

  const detailedResults = getDetailedResults()

  return (
    <div className="space-y-6">
      {/* Results Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {results.success ? (
            <CheckCircle className="h-6 w-6 text-green-500" />
          ) : (
            <XCircle className="h-6 w-6 text-red-500" />
          )}
          <div>
            <h3 className="font-semibold">{results.success ? "Execution Successful" : "Execution Failed"}</h3>
            <p className="text-sm text-muted-foreground">Completed at {results.timestamp}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Re-run
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      <Tabs defaultValue="summary" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="summary">Summary</TabsTrigger>
          <TabsTrigger value="details">Details</TabsTrigger>
          <TabsTrigger value="raw">Raw Output</TabsTrigger>
        </TabsList>

        <TabsContent value="summary" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Execution Summary</CardTitle>
              <CardDescription>{detailedResults.summary}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(detailedResults.details).map(([key, value]) => (
                  <div key={key} className="space-y-1">
                    <div className="text-sm font-medium">{key}</div>
                    <div className="text-2xl font-bold text-primary">{value}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="details" className="space-y-4">
          {module.category === "reconnaissance" && detailedResults.hosts && (
            <Card>
              <CardHeader>
                <CardTitle>Discovered Hosts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {detailedResults.hosts.map((host: any, index: number) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="font-medium">{host.hostname}</div>
                        <Badge variant="outline">{host.ip}</Badge>
                      </div>
                      <div className="text-sm text-muted-foreground mb-2">{host.os}</div>
                      <div className="flex flex-wrap gap-1">
                        {host.ports.map((port: number) => (
                          <Badge key={port} variant="secondary" className="text-xs">
                            {port}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {module.category === "weaponization" && detailedResults.artifacts && (
            <Card>
              <CardHeader>
                <CardTitle>Generated Artifacts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {detailedResults.artifacts.map((artifact: any, index: number) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <div className="font-medium">{artifact.name}</div>
                        <div className="text-sm text-muted-foreground">
                          {artifact.size} • {artifact.hash}
                        </div>
                      </div>
                      <Button variant="outline" size="sm">
                        <Download className="h-4 w-4 mr-2" />
                        Download
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {module.category === "delivery" && detailedResults.targets && (
            <Card>
              <CardHeader>
                <CardTitle>Target Results</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {detailedResults.targets.map((target: any, index: number) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <div className="font-medium">{target.email}</div>
                        <div className="text-sm text-muted-foreground">{target.timestamp}</div>
                      </div>
                      <Badge
                        variant={
                          target.status === "clicked"
                            ? "destructive"
                            : target.status === "opened"
                              ? "default"
                              : "secondary"
                        }
                      >
                        {target.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="raw" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Raw Output</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="bg-muted p-4 rounded-lg text-sm overflow-x-auto whitespace-pre-wrap">
                {results.output}
              </pre>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
