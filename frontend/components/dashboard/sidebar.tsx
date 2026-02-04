"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Upload, BarChart3, AlertCircle, FileText, Settings, Menu, X } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"

interface SidebarProps {
  t?: {
    nav: {
      upload: string
      statistics: string
      errors: string
      settings: string
    }
  }
}

const navigation = [
  { nameKey: "nav.upload", href: "/", icon: Upload },
  { nameKey: "nav.statistics", href: "/statistics", icon: BarChart3 },
  { nameKey: "nav.errors", href: "/errors", icon: AlertCircle },
]

export function Sidebar({ t }: SidebarProps) {
  const pathname = usePathname()
  
  // Extract locale from pathname (e.g., "/az/statistics" -> "az")
  const pathnameParts = pathname.split("/")
  const lang = pathnameParts[1] || "en"
  
  const getLabel = (key: string) => {
    if (!t) return key.split(".").pop()?.replace(/([A-Z])/g, " $1").trim()
    const keys = key.split(".")
    let value: any = t
    for (const k of keys) {
      value = value?.[k]
    }
    return value || key
  }

  const NavLinks = ({ mobile = false }: { mobile?: boolean }) => (
    <>
      {navigation.map((item) => {
        const isActive = pathname === `/${lang}${item.href}` || pathname === item.href
        return (
          <Link
            key={item.nameKey}
            href={`/${lang}${item.href}`}
            className={cn(
              "flex items-center rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
              isActive
                ? "bg-blue-50 text-blue-700"
                : "text-gray-700 hover:bg-gray-100 hover:text-gray-900",
              mobile && "w-full"
            )}
          >
            <item.icon className={cn("h-5 w-5", isActive ? "text-blue-600" : "text-gray-400", mobile ? "mr-3" : "mr-3")} />
            {getLabel(item.nameKey)}
          </Link>
        )
      })}
      <Link
        href={`/${lang}/settings`}
        className="flex items-center rounded-lg px-3 py-2.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-100 hover:text-gray-900"
      >
        <Settings className="mr-3 h-5 w-5 text-gray-400" />
        {t?.nav?.settings || "Settings"}
      </Link>
    </>
  )

  return (
    <>
      {/* Desktop Sidebar - Hidden on mobile */}
      <div className="hidden md:flex h-full w-64 flex-col border-r bg-white">
        <div className="flex h-16 items-center border-b px-6">
          <FileText className="mr-2 h-6 w-6 text-blue-600" />
          <span className="text-lg font-semibold">AzStat Report</span>
        </div>
        <nav className="flex-1 space-y-1 px-3 py-4">
          <NavLinks />
        </nav>
      </div>

      {/* Mobile Header & Sheet - Visible on mobile */}
      <div className="md:hidden flex h-16 items-center justify-between border-b bg-white px-4">
        <div className="flex items-center">
          <FileText className="mr-2 h-6 w-6 text-blue-600" />
          <span className="text-lg font-semibold">AzStat Report</span>
        </div>
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon">
              <Menu className="h-6 w-6" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-64 p-0">
            <div className="flex h-16 items-center border-b px-6">
              <FileText className="mr-2 h-6 w-6 text-blue-600" />
              <span className="text-lg font-semibold">AzStat Report</span>
            </div>
            <nav className="flex-1 space-y-1 px-3 py-4">
              <NavLinks mobile />
            </nav>
          </SheetContent>
        </Sheet>
      </div>
    </>
  )
}
