"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Shield, Eye, EyeOff, AlertCircle, Server } from "lucide-react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/components/auth/auth-provider"

export default function LoginPage() {
  const [credentials, setCredentials] = useState({
    username: "",
    password: "",
    serverHost: "localhost",
    serverPort: "8080",
  })
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const router = useRouter()
  const { login } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    try {
      const success = await login(credentials.username, credentials.password)

      if (success) {
        router.push("/")
      } else {
        setError("Authentication failed. Please check your credentials and ensure the Team Server is running.")
      }
    } catch (err) {
      setError("Connection failed. Please verify the Team Server is accessible.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Shield className="h-12 w-12 text-primary" />
          </div>
          <h1 className="text-3xl font-bold">Ghost Protocol</h1>
          <p className="text-muted-foreground">Team Server Web Interface</p>
        </div>

        {/* Login Form */}
        <Card>
          <CardHeader>
            <CardTitle>Team Server Connection</CardTitle>
            <CardDescription>Connect to your Ghost Protocol Team Server</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-2">
                  <Label htmlFor="serverHost">Server Host</Label>
                  <Input
                    id="serverHost"
                    type="text"
                    placeholder="localhost"
                    value={credentials.serverHost}
                    onChange={(e) => setCredentials({ ...credentials, serverHost: e.target.value })}
                    required
                    disabled={isLoading}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="serverPort">Port</Label>
                  <Input
                    id="serverPort"
                    type="number"
                    placeholder="8080"
                    value={credentials.serverPort}
                    onChange={(e) => setCredentials({ ...credentials, serverPort: e.target.value })}
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  type="text"
                  placeholder="Enter your username"
                  value={credentials.username}
                  onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
                  required
                  disabled={isLoading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    value={credentials.password}
                    onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                    required
                    disabled={isLoading}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowPassword(!showPassword)}
                    disabled={isLoading}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
              </div>

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? (
                  <div className="flex items-center gap-2">
                    <Server className="h-4 w-4 animate-pulse" />
                    Connecting to Team Server...
                  </div>
                ) : (
                  "Connect to Team Server"
                )}
              </Button>
            </form>

            <div className="mt-6 p-4 bg-muted rounded-lg">
              <p className="text-sm font-medium mb-2">Default Configuration:</p>
              <p className="text-sm text-muted-foreground">
                Server: <code className="bg-background px-1 rounded">localhost:8080</code>
              </p>
              <p className="text-sm text-muted-foreground">
                Username: <code className="bg-background px-1 rounded">admin</code>
              </p>
              <p className="text-sm text-muted-foreground">
                Password: <code className="bg-background px-1 rounded">ghost123</code>
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Security Notice */}
        <div className="text-center text-sm text-muted-foreground">
          <p>Ensure your Ghost Protocol Team Server is running before connecting.</p>
          <p>All team activities are synchronized and logged.</p>
        </div>
      </div>
    </div>
  )
}
