"use client"

import { ErrorList, ErrorItem } from "@/components/dashboard/error-list"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Download, RefreshCw } from "lucide-react"
import { useState } from "react"

// Mock error data for demonstration
const mockErrors: ErrorItem[] = [
  {
    id: "1",
    reportName: "Annual_Report_2023.html",
    errorType: "Missing DOCTYPE",
    message: "HTML document is missing the required DOCTYPE declaration",
    line: 1,
    column: 1,
    severity: "error",
    status: "pending",
    timestamp: "2024-02-03T10:30:00Z",
  },
  {
    id: "2",
    reportName: "Annual_Report_2023.html",
    errorType: "Unclosed Tag",
    message: "The <div> tag on line 45 is not properly closed",
    line: 45,
    column: 12,
    severity: "error",
    status: "pending",
    timestamp: "2024-02-03T10:30:00Z",
  },
  {
    id: "3",
    reportName: "Performance_Review.html",
    errorType: "Invalid Nesting",
    message: "Block-level element <div> cannot be nested inside inline element <span>",
    line: 120,
    column: 8,
    severity: "error",
    status: "pending",
    timestamp: "2024-02-02T14:15:00Z",
  },
  {
    id: "4",
    reportName: "Annual_Report_2023.html",
    errorType: "Deprecated Attribute",
    message: "The 'bgcolor' attribute is deprecated. Use CSS background-color instead",
    line: 78,
    column: 15,
    severity: "warning",
    status: "ignored",
    timestamp: "2024-02-03T10:30:00Z",
  },
  {
    id: "5",
    reportName: "Monthly_Summary_Dec.html",
    errorType: "Missing Alt Text",
    message: "Image element is missing required alt attribute for accessibility",
    line: 234,
    column: 5,
    severity: "warning",
    status: "resolved",
    timestamp: "2024-02-01T09:45:00Z",
  },
  {
    id: "6",
    reportName: "Budget_Analysis.html",
    errorType: "Duplicate ID",
    message: "Duplicate ID 'header' found. IDs must be unique in the document",
    line: 56,
    column: 10,
    severity: "error",
    status: "pending",
    timestamp: "2024-02-01T11:20:00Z",
  },
]

export default function ErrorsPage() {
  const [errors, setErrors] = useState<ErrorItem[]>(mockErrors)

  const pendingErrors = errors.filter((e) => e.status === "pending")
  const resolvedErrors = errors.filter((e) => e.status === "resolved")
  const ignoredErrors = errors.filter((e) => e.status === "ignored")

  const handleRefresh = () => {
    // In a real app, this would fetch the latest errors from the API
    console.log("Refreshing errors...")
  }

  const handleExport = () => {
    // In a real app, this would export the errors to a file
    console.log("Exporting errors...")
    const csvContent = errors
      .map((e) => `${e.reportName},${e.errorType},${e.message},${e.line},${e.severity},${e.status}`)
      .join("\n")
    const blob = new Blob([`Report Name,Error Type,Message,Line,Severity,Status\n${csvContent}`], {
      type: "text/csv",
    })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "validation_errors.csv"
    a.click()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Error List</h1>
          <p className="text-gray-500 mt-1">
            View and manage validation errors from your reports
          </p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={handleRefresh}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button variant="outline" onClick={handleExport}>
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
        </div>
      </div>

      <Tabs defaultValue="all" className="space-y-4">
        <TabsList>
          <TabsTrigger value="all">
            All Errors ({errors.length})
          </TabsTrigger>
          <TabsTrigger value="pending">
            Pending ({pendingErrors.length})
          </TabsTrigger>
          <TabsTrigger value="resolved">
            Resolved ({resolvedErrors.length})
          </TabsTrigger>
          <TabsTrigger value="ignored">
            Ignored ({ignoredErrors.length})
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
