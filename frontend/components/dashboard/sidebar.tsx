"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Upload, BarChart3, AlertCircle, FileText, Settings } from "lucide-react"
import { cn } from "@/lib/utils"

const navigation = [
  { name: "Upload Report", href: "/", icon: Upload },
  { name: "Statistics", href: "/statistics", icon: BarChart3 },
  { name: "Error List", href: "/errors", icon: AlertCircle },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="flex h-full w-64 flex-col border-r bg-white">
      <div className="flex h-16 items-center border-b px-6">
        <FileText className="mr-2 h-6 w-6 text-blue-600" />
        <span className="text-lg font-semibold">AzStat Report</span>
      </div>
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-blue-50 text-blue-700"
                  : "text-gray-700 hover:bg-gray-100 hover:text-gray-900"
              )}
            >
              <item.icon className={cn("mr-3 h-5 w-5", isActive ? "text-blue-600" : "text-gray-400")} />
              {item.name}
            </Link>
          )
        })}
      </nav>
      <div className="border-t p-4">
        <Link
          href="/settings"
          className="flex items-center rounded-lg px-3 py-2.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-100 hover:text-gray-900"
        >
          <Settings className="mr-3 h-5 w-5 text-gray-400" />
          Settings
        </Link>
      </div>
    </div>
  )
}
