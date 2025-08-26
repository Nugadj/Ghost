"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Save, RotateCcw, AlertTriangle } from "lucide-react"

interface ModuleData {
  id: string
  name: string
  category: string
  config: Record<string, any>
}

interface ModuleConfigProps {
  module: ModuleData
}

export function ModuleConfig({ module }: ModuleConfigProps) {
  const [config, setConfig] = useState(module.config)
  const [hasChanges, setHasChanges] = useState(false)

  const updateConfig = (key: string, value: any) => {
    setConfig((prev) => ({ ...prev, [key]: value }))
    setHasChanges(true)
  }

  const handleSave = () => {
    console.log(`[v0] Saving config for module ${module.id}:`, config)
    setHasChanges(false)
  }

  const handleReset = () => {
    setConfig(module.config)
    setHasChanges(false)
  }

  const renderConfigField = (key: string, value: any) => {
    switch (typeof value) {
      case "boolean":
        return (
          <div key={key} className="flex items-center justify-between">
            <Label htmlFor={key} className="capitalize">
              {key.replace(/_/g, " ")}
            </Label>
            <Switch id={key} checked={config[key]} onCheckedChange={(checked) => updateConfig(key, checked)} />
          </div>
        )

      case "number":
        return (
          <div key={key} className="space-y-2">
            <Label htmlFor={key} className="capitalize">
              {key.replace(/_/g, " ")}
            </Label>
            <Input
              id={key}
              type="number"
              value={config[key]}
              onChange={(e) => updateConfig(key, Number.parseInt(e.target.value))}
            />
          </div>
        )

      case "string":
        if (value.length > 50 || key.includes("description") || key.includes("template")) {
          return (
            <div key={key} className="space-y-2">
              <Label htmlFor={key} className="capitalize">
                {key.replace(/_/g, " ")}
              </Label>
              <Textarea id={key} value={config[key]} onChange={(e) => updateConfig(key, e.target.value)} rows={3} />
            </div>
          )
        } else {
          return (
            <div key={key} className="space-y-2">
              <Label htmlFor={key} className="capitalize">
                {key.replace(/_/g, " ")}
              </Label>
              <Input id={key} value={config[key]} onChange={(e) => updateConfig(key, e.target.value)} />
            </div>
          )
        }

      default:
        if (Array.isArray(value)) {
          return (
            <div key={key} className="space-y-2">
              <Label htmlFor={key} className="capitalize">
                {key.replace(/_/g, " ")}
              </Label>
              <Textarea
                id={key}
                value={config[key].join("\n")}
                onChange={(e) => updateConfig(key, e.target.value.split("\n"))}
                rows={4}
                placeholder="One item per line"
              />
            </div>
          )
        }
        return (
          <div key={key} className="space-y-2">
            <Label htmlFor={key} className="capitalize">
              {key.replace(/_/g, " ")}
            </Label>
            <Input
              id={key}
              value={JSON.stringify(config[key])}
              onChange={(e) => {
                try {
                  updateConfig(key, JSON.parse(e.target.value))
                } catch {
                  // Invalid JSON, keep as string
                  updateConfig(key, e.target.value)
                }
              }}
            />
          </div>
        )
    }
  }

  const getModuleSpecificConfig = () => {
    switch (module.category) {
      case "reconnaissance":
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Scan Type</Label>
              <Select value={config.scan_type} onValueChange={(value) => updateConfig("scan_type", value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="tcp">TCP Connect</SelectItem>
                  <SelectItem value="syn">SYN Stealth</SelectItem>
                  <SelectItem value="udp">UDP Scan</SelectItem>
                  <SelectItem value="comprehensive">Comprehensive</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {Object.entries(config)
              .filter(([key]) => !["scan_type"].includes(key))
              .map(([key, value]) => renderConfigField(key, value))}
          </div>
        )

      case "weaponization":
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Payload Type</Label>
              <Select value={config.payload_type} onValueChange={(value) => updateConfig("payload_type", value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="windows_exe">Windows Executable</SelectItem>
                  <SelectItem value="linux_elf">Linux ELF</SelectItem>
                  <SelectItem value="macos_app">macOS Application</SelectItem>
                  <SelectItem value="powershell">PowerShell Script</SelectItem>
                  <SelectItem value="python">Python Script</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {Object.entries(config)
              .filter(([key]) => !["payload_type"].includes(key))
              .map(([key, value]) => renderConfigField(key, value))}
          </div>
        )

      default:
        return (
          <div className="space-y-4">{Object.entries(config).map(([key, value]) => renderConfigField(key, value))}</div>
        )
    }
  }

  return (
    <div className="space-y-6">
      <Tabs defaultValue="basic" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="basic">Basic Settings</TabsTrigger>
          <TabsTrigger value="advanced">Advanced</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
        </TabsList>

        <TabsContent value="basic" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Basic Configuration</CardTitle>
              <CardDescription>Essential module settings</CardDescription>
            </CardHeader>
            <CardContent>{getModuleSpecificConfig()}</CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="advanced" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Advanced Settings</CardTitle>
              <CardDescription>Fine-tune module behavior</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Execution Timeout (seconds)</Label>
                <Input
                  type="number"
                  value={config.timeout || 300}
                  onChange={(e) => updateConfig("timeout", Number.parseInt(e.target.value))}
                />
              </div>
              <div className="space-y-2">
                <Label>Thread Count</Label>
                <Input
                  type="number"
                  value={config.threads || 10}
                  onChange={(e) => updateConfig("threads", Number.parseInt(e.target.value))}
                />
              </div>
              <div className="space-y-2">
                <Label>Log Level</Label>
                <Select value={config.log_level || "info"} onValueChange={(value) => updateConfig("log_level", value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="debug">Debug</SelectItem>
                    <SelectItem value="info">Info</SelectItem>
                    <SelectItem value="warning">Warning</SelectItem>
                    <SelectItem value="error">Error</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Security Settings</CardTitle>
              <CardDescription>Configure security and stealth options</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Label>Stealth Mode</Label>
                <Switch
                  checked={config.stealth_mode || false}
                  onCheckedChange={(checked) => updateConfig("stealth_mode", checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <Label>Anti-Detection</Label>
                <Switch
                  checked={config.anti_detection || false}
                  onCheckedChange={(checked) => updateConfig("anti_detection", checked)}
                />
              </div>
              <div className="space-y-2">
                <Label>Delay Between Operations (ms)</Label>
                <Input
                  type="number"
                  value={config.operation_delay || 1000}
                  onChange={(e) => updateConfig("operation_delay", Number.parseInt(e.target.value))}
                />
              </div>

              <div className="p-4 border border-yellow-500/20 bg-yellow-500/10 rounded-lg">
                <div className="flex items-center gap-2 text-yellow-500 mb-2">
                  <AlertTriangle className="h-4 w-4" />
                  <span className="font-medium">Security Notice</span>
                </div>
                <p className="text-sm text-muted-foreground">
                  These settings affect operational security. Higher stealth settings may reduce performance but improve
                  detection avoidance.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <div className="flex items-center justify-between pt-4 border-t">
        <div className="flex items-center gap-2">
          {hasChanges && <span className="text-sm text-yellow-500">Unsaved changes</span>}
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleReset} disabled={!hasChanges}>
            <RotateCcw className="h-4 w-4 mr-2" />
            Reset
          </Button>
          <Button onClick={handleSave} disabled={!hasChanges}>
            <Save className="h-4 w-4 mr-2" />
            Save Configuration
          </Button>
        </div>
      </div>
    </div>
  )
}
