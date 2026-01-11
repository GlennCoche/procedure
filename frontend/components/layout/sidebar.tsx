"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { FileText, MessageSquare, Lightbulb, Camera, Settings, LayoutDashboard } from "lucide-react"

const navigation = [
  { name: "Tableau de bord", href: "/dashboard", icon: LayoutDashboard },
  { name: "Procédures", href: "/dashboard/procedures", icon: FileText },
  { name: "Chat IA", href: "/dashboard/chat", icon: MessageSquare },
  { name: "Tips & Astuces", href: "/dashboard/tips", icon: Lightbulb },
  { name: "Reconnaissance", href: "/dashboard/camera", icon: Camera },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 border-r bg-card min-h-screen p-4">
      <nav className="space-y-2">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <item.icon className="h-5 w-5" />
              <span>{item.name}</span>
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
