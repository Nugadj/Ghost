"use client"

import { Button } from "@/components/ui/button"
import { Activity, Target, Users, Server, Zap, Eye, Terminal } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useAuth } from "@/components/auth/auth-provider"

export function Sidebar() {
  const pathname = usePathname()
  const { hasPermission } = useAuth()

  const navItems = [
    { href: "/", icon: Activity, label: "Dashboard", permission: "read" },
    { href: "/beacons", icon: Target, label: "Beacons", permission: "read" },
    { href: "/listeners", icon: Server, label: "Listeners", permission: "read" },
    { href: "/targets", icon: Users, label: "Targets", permission: "read" },
    { href: "/modules", icon: Zap, label: "Modules", permission: "execute" },
    { href: "/reports", icon: Eye, label: "Reports", permission: "read" },
    { href: "/console", icon: Terminal, label: "Console", permission: "execute" },
  ]

  return (
    <aside className="w-64 border-r border-border bg-sidebar min-h-[calc(100vh-4rem)]">
      <nav className="p-4 space-y-2">
        {navItems.map((item) => {
          if (!hasPermission(item.permission)) return null

          const isActive = pathname === item.href
          const Icon = item.icon

          return (
            <Link key={item.href} href={item.href}>
              <Button
                variant={isActive ? "default" : "ghost"}
                className="w-full justify-start text-sidebar-foreground hover:bg-sidebar-accent"
              >
                <Icon className="h-4 w-4 mr-2" />
                {item.label}
              </Button>
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
