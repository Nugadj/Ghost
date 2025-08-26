"use client"

import type React from "react"

import { useAuth } from "./auth-provider"
import { Skeleton } from "@/components/ui/skeleton"

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredPermission?: string
  fallback?: React.ReactNode
}

export function ProtectedRoute({ children, requiredPermission, fallback }: ProtectedRouteProps) {
  const { user, isLoading, hasPermission } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="flex">
          <aside className="w-64 border-r border-border bg-sidebar min-h-screen">
            <div className="p-4 space-y-2">
              {Array.from({ length: 7 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          </aside>
          <main className="flex-1 p-6">
            <div className="space-y-6">
              <Skeleton className="h-8 w-64" />
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {Array.from({ length: 4 }).map((_, i) => (
                  <Skeleton key={i} className="h-32" />
                ))}
              </div>
            </div>
          </main>
        </div>
      </div>
    )
  }

  if (!user) {
    return fallback || null
  }

  if (requiredPermission && !hasPermission(requiredPermission)) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <h1 className="text-2xl font-bold">Access Denied</h1>
          <p className="text-muted-foreground">You don't have permission to access this resource.</p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}
