"use client"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Shield, Settings, Terminal, User, LogOut, Server, Wifi, WifiOff } from "lucide-react"
import Link from "next/link"
import { useAuth } from "@/components/auth/auth-provider"

export function Header() {
  const { user, logout, isConnected } = useAuth()

  return (
    <header className="border-b border-border bg-card">
      <div className="flex h-16 items-center justify-between px-6">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Shield className="h-8 w-8 text-primary" />
            <div>
              <h1 className="text-2xl font-bold">Ghost Protocol</h1>
              <p className="text-xs text-muted-foreground">Team Server Web Interface</p>
            </div>
          </div>

          <div className="flex items-center gap-2 ml-4">
            <Badge variant={isConnected ? "default" : "destructive"} className="flex items-center gap-1">
              {isConnected ? (
                <>
                  <Wifi className="h-3 w-3" />
                  Team Server Connected
                </>
              ) : (
                <>
                  <WifiOff className="h-3 w-3" />
                  Team Server Disconnected
                </>
              )}
            </Badge>

            {isConnected && (
              <Badge variant="outline" className="flex items-center gap-1">
                <Server className="h-3 w-3" />
                localhost:8080
              </Badge>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </Button>
          <Link href="/console">
            <Button variant="outline" size="sm">
              <Terminal className="h-4 w-4 mr-2" />
              Console
            </Button>
          </Link>

          {user && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  <User className="h-4 w-4 mr-2" />
                  {user.username}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>
                  <div className="space-y-1">
                    <p className="text-sm font-medium">{user.username}</p>
                    <p className="text-xs text-muted-foreground capitalize">{user.role}</p>
                    <p className="text-xs text-muted-foreground">
                      {isConnected ? "Connected to Team Server" : "Disconnected"}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <User className="h-4 w-4 mr-2" />
                  Profile
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Settings className="h-4 w-4 mr-2" />
                  Settings
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={logout} className="text-red-600">
                  <LogOut className="h-4 w-4 mr-2" />
                  Disconnect & Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </div>
    </header>
  )
}
