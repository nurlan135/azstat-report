"use client"

import { useEffect, useState } from "react"
import { ErrorList, ErrorItem } from "@/components/dashboard/error-list"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Download, RefreshCw, Loader2 } from "lucide-react"
import { en, az } from "@/app/dictionaries/en"
import { getErrors, type ValidationError } from "@/lib/api"

const dictionaries = {
  en,
  az,
}

export default function ErrorsPage({
  params: { lang },
}: {
  params: { lang: string }
}) {
  const t = dictionaries[lang as keyof typeof dictionaries] || en
  const [errors, setErrors] = useState<ValidationError[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchErrors = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getErrors()
      setErrors(data)
    } catch (err) {
      console.error("Failed to fetch errors:", err)
      setError(err instanceof Error ? err.message : "Failed to load errors")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchErrors()
  }, [])

  const pendingErrors = errors.filter((e) => e.status === "pending")
  const resolvedErrors = errors.filter((e) => e.status === "resolved")
  const ignoredErrors = errors.filter((e) => e.status === "ignored")

  const handleRefresh = () => {
    fetchErrors()
  }

  const handleExport = () => {
    const csvContent = errors
      .map((e) => `${e.report_name},${e.error_type},${e.message},${e.line || ""},${e.severity},${e.status}`)
      .join("\n")
    const blob = new Blob([`Report Name,Error Type,Message,Line,Severity,Status\n${csvContent}`], {
      type: "text/csv",
    })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "validation_errors.csv"
    a.click()
    window.URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
        <span className="ml-2 text-gray-500">{t.common.loading}</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <div className="text-red-500 mb-2">Error loading errors</div>
        <p className="text-gray-500">{error}</p>
        <Button variant="outline" onClick={handleRefresh} className="mt-4">
          <RefreshCw className="mr-2 h-4 w-4" />
          {t.common.refresh}
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t.errors.title}</h1>
          <p className="text-gray-500 mt-1">
            {t.errors.description}
          </p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={handleRefresh}>
            <RefreshCw className="mr-2 h-4 w-4" />
            {t.common.refresh}
          </Button>
          <Button variant="outline" onClick={handleExport}>
            <Download className="mr-2 h-4 w-4" />
            {t.common.export}
          </Button>
        </div>
      </div>

      <Tabs defaultValue="all" className="space-y-4">
        <TabsList>
          <TabsTrigger value="all">
            {t.errors.allErrors} ({errors.length})
          </TabsTrigger>
          <TabsTrigger value="pending">
            {t.errors.pendingErrors} ({pendingErrors.length})
          </TabsTrigger>
          <TabsTrigger value="resolved">
            {t.errors.resolvedErrors} ({resolvedErrors.length})
          </TabsTrigger>
          <TabsTrigger value="ignored">
            {t.errors.ignoredErrors} ({ignoredErrors.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="all">
          <ErrorList errors={errors} />
        </TabsContent>

        <TabsContent value="pending">
          <ErrorList errors={pendingErrors} />
        </TabsContent>

        <TabsContent value="resolved">
          <ErrorList errors={resolvedErrors} />
        </TabsContent>

        <TabsContent value="ignored">
          <ErrorList errors={ignoredErrors} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
