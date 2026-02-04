import type { Metadata } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import { Toaster } from "sonner"
import "../globals.css"
import { Sidebar } from "@/components/dashboard/sidebar"
import { en, az } from "@/app/dictionaries/en"

const dictionaries = {
  en,
  az,
}

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
})

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
})

export const metadata: Metadata = {
  title: "AzStat Report Dashboard",
  description: "HTML Report Validation and Statistics Dashboard",
}

export function generateStaticParams() {
  return [{ lang: "en" }, { lang: "az" }]
}

export default async function RootLayout({
  children,
  params,
}: {
  children: React.ReactNode
  params: Promise<{ lang: string }>
}) {
  const { lang } = await params
  const t = dictionaries[lang as keyof typeof dictionaries] || en
  
  return (
    <html lang={lang}>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <div className="flex h-screen">
          <Sidebar t={t} />
          <main className="flex-1 overflow-auto bg-gray-50 p-6">
            {children}
          </main>
        </div>
        <Toaster position="top-right" />
      </body>
    </html>
  )
}
