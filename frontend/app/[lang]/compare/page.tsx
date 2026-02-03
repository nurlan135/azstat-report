"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Loader2, GitCompareArrows, AlertTriangle, CheckCircle, Info, XCircle } from "lucide-react"
import { en, az } from "@/app/dictionaries/en"
import { getReports, compareReports, type Report, type CompareResult } from "@/lib/api"

const dictionaries = {
  en,
  az,
}

export default function ComparePage({
  params: { lang },
}: {
  params: { lang: string }
}) {
  const t = dictionaries[lang as keyof typeof dictionaries] || en
  const [reports, setReports] = useState<Report[]>([])
  const [selectedReportA, setSelectedReportA] = useState<string>("")
  const [selectedReportB, setSelectedReportB] = useState<string>("")
  const [compareResult, setCompareResult] = useState<CompareResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [comparing, setComparing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchReports = async () => {
      try {
        setLoading(true)
        const data = await getReports()
        setReports(data)
      } catch (err) {
        console.error("Failed to fetch reports:", err)
        setError(err instanceof Error ? err.message : "Failed to load reports")
      } finally {
        setLoading(false)
      }
    }

    fetchReports()
  }, [])

  const handleCompare = async () => {
    if (!selectedReportA || !selectedReportB) return

    try {
      setComparing(true)
      setError(null)
      const data = await compareReports([selectedReportA, selectedReportB])
      setCompareResult(data)
    } catch (err) {
      console.error("Failed to compare reports:", err)
      setError(err instanceof Error ? err.message : "Failed to compare reports")
    } finally {
      setComparing(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "valid":
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case "warning":
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      case "error":
        return <XCircle className="h-4 w-4 text-red-500" />
      default:
        return <Info className="h-4 w-4 text-blue-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "valid":
        return "bg-green-100 text-green-800"
      case "warning":
        return "bg-yellow-100 text-yellow-800"
      case "error":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
        <span className="ml-2 text-gray-500">{t.common.loading}</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">{t.compare.title}</h1>
        <p className="text-gray-500 mt-1">
          {t.compare.description}
        </p>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>{t.compare.selectReports}</CardTitle>
          <CardDescription></CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3 items-end">
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">
                {t.compare.reportA}
              </label>
              <Select value={selectedReportA} onValueChange={setSelectedReportA}>
                <SelectTrigger>
                  <SelectValue placeholder="Select report A" />
                </SelectTrigger>
                <SelectContent>
                  {reports.map((report) => (
                    <SelectItem key={report.id} value={report.id}>
                      {report.filename}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex justify-center">
              <Button
                variant="outline"
                size="icon"
                onClick={handleCompare}
                disabled={!selectedReportA || !selectedReportB || comparing}
              >
                {comparing ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <GitCompareArrows className="h-4 w-4" />
                )}
              </Button>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">
                {t.compare.reportB}
              </label>
              <Select value={selectedReportB} onValueChange={setSelectedReportB}>
                <SelectTrigger>
                  <SelectValue placeholder="Select report B" />
                </SelectTrigger>
                <SelectContent>
                  {reports.map((report) => (
                    <SelectItem key={report.id} value={report.id}>
                      {report.filename}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="mt-4 flex justify-end">
            <Button
              onClick={handleCompare}
              disabled={!selectedReportA || !selectedReportB || comparing}
            >
              {comparing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {t.common.loading}
                </>
              ) : (
                <>
                  <GitCompareArrows className="mr-2 h-4 w-4" />
                  {t.compare.compare}
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {compareResult && (
        <div className="grid gap-6 md:grid-cols-2">
          {compareResult.comparison.map((item) => {
            const report = reports.find((r) => r.id === item.report_id)
            return (
              <Card key={item.report_id}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    {getStatusIcon(item.validation_status)}
                    {item.filename || report?.filename}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 grid-cols-2">
                    <div>
                      <p className="text-sm text-gray-500">{t.compare.score}</p>
                      <p className="text-2xl font-bold">{item.score}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">{t.compare.errorCount}</p>
                      <p className="text-2xl font-bold text-red-600">{item.errors_count}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">{t.compare.warningCount}</p>
                      <p className="text-2xl font-bold text-yellow-600">{item.warnings_count}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Status</p>
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                          item.validation_status
                        )}`}
                      >
                        {item.validation_status}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {reports.length === 0 && !loading && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <GitCompareArrows className="h-12 w-12 text-gray-400 mb-4" />
            <p className="text-gray-500">{t.compare.noReports}</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
