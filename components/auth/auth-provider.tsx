"use client"

import type React from "react"

import { createContext, useContext, useEffect, useState } from "react"
import { useRouter, usePathname } from "next/navigation"
import ghostAPI from "@/lib/api-client"

interface User {
  id: string
  username: string
  role: "administrator" | "operator" | "viewer"
  permissions: string[]
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (username: string, password: string) => Promise<boolean>
  logout: () => void
  hasPermission: (permission: string) => boolean
  isConnected: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isConnected, setIsConnected] = useState(false)
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    const token = localStorage.getItem("ghost_auth_token")
    const userData = localStorage.getItem("ghost_user")

    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData)
        setUser(parsedUser)
        setIsConnected(true)

        // Set up WebSocket event handlers for real-time updates
        ghostAPI.on("beacon.checkin", (data: any) => {
          console.log("[v0] Beacon check-in received:", data)
        })

        ghostAPI.on("beacon.output", (data: any) => {
          console.log("[v0] Beacon output received:", data)
        })

        ghostAPI.on("session.create", (data: any) => {
          console.log("[v0] Session created:", data)
        })
      } catch (error) {
        // Invalid user data, clear storage
        localStorage.removeItem("ghost_auth_token")
        localStorage.removeItem("ghost_user")
      }
    }

    setIsLoading(false)
  }, [])

  useEffect(() => {
    // Redirect to login if not authenticated and not already on login page
    if (!isLoading && !user && pathname !== "/login") {
      router.push("/login")
    }
  }, [user, isLoading, pathname, router])

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true)

      // Authenticate with Ghost Protocol Team Server
      const success = await ghostAPI.authenticate(username, password)

      if (success) {
        // Create user object with role-based permissions
        const userData: User = {
          id: username,
          username,
          role: username === "admin" ? "administrator" : "operator",
          permissions:
            username === "admin"
              ? ["beacon.manage", "listener.manage", "module.execute", "operation.manage", "user.manage"]
              : ["beacon.view", "listener.view", "module.execute", "operation.view"],
        }

        // Store auth data
        localStorage.setItem("ghost_auth_token", "authenticated")
        localStorage.setItem("ghost_user", JSON.stringify(userData))

        setUser(userData)
        setIsConnected(true)

        return true
      }

      return false
    } catch (error) {
      console.error("[v0] Authentication error:", error)
      return false
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    ghostAPI.disconnect()
    localStorage.removeItem("ghost_auth_token")
    localStorage.removeItem("ghost_user")
    setUser(null)
    setIsConnected(false)
    router.push("/login")
  }

  const hasPermission = (permission: string) => {
    return user?.permissions.includes(permission) || false
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout, hasPermission, isConnected }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
