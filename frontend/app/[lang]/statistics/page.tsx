"use client"

import { useEffect, useState } from "react"
import { StatisticsCards } from "@/components/dashboard/statistics-cards"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { BarChart3, TrendingUp, Activity, Loader2 } from "lucide-react"
import { en, az } from "@/app/dictionaries/en"
import { getStatistics, getReports, type Report, type Statistics } from "@/lib/api"

const dictionaries = {
  en,
  az,
}

export default function StatisticsPage({
  params: { lang },
}: {
  params: { lang: string }
}) {
  const t = dictionaries[lang as keyof typeof dictionaries] || en
  const [stats, setStats] = useState<Statistics | null>(null)
  const [recentReports, setRecentReports] = useState<Report[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const [statsData, reportsData] = await Promise.all([
          getStatistics(),
          getReports(),
        ])
        setStats(statsData)
        // Get the 5 most recent reports
        setRecentReports(reportsData.slice(0, 5))
      } catch (err) {
        console.error("Failed to fetch statistics:", err)
        setError(err instanceof Error ? err.message : "Failed to load statistics")
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case "valid":
        return "bg-green-100 text-green-800"
      case "warning":
        return "bg-yellow-100 text-yellow-800"
      default:
        return "bg-red-100 text-red-800"
    }
  }

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      valid: "Valid",
      warning: "Warning",
      error: "Error",
    }
    return labels[status] || status
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
        <div className="text-red-500 mb-2">Error loading statistics</div>
        <p className="text-gray-500">{error}</p>
      </div>
    )
  }

  const displayStats = stats || {
    total_reports: 0,
    valid_reports: 0,
    error_reports: 0,
    pending_reports: 0,
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">{t.statistics.title}</h1>
        <p className="text-gray-500 mt-1">
          {t.statistics.description}
        </p>
      </div>

      <StatisticsCards
        totalReports={displayStats.total_reports}
        validReports={displayStats.valid_reports}
        errorsCount={displayStats.error_reports}
        pendingReports={displayStats.pending_reports}
      />

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <div>
              <CardTitle className="text-base font-medium">{t.statistics.recentReports}</CardTitle>
              <CardDescription>{t.statistics.validationDate}</CardDescription>
            </div>
            <BarChart3 className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t.statistics.reportName}</TableHead>
                  <TableHead>{t.statistics.status}</TableHead>
                  <TableHead className="text-right">{t.statistics.score}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recentReports.length > 0 ? (
                  recentReports.map((report) => (
                    <TableRow key={report.id}>
                      <TableCell className="font-medium truncate max-w-[200px]">
                        {report.filename}
                      </TableCell>
                      <TableCell>
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                            report.validation_status
                          )}`}
                        >
                          {getStatusLabel(report.validation_status)}
                        </span>
                      </TableCell>
                      <TableCell className="text-right font-medium">
                        {report.score}%
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={3} className="text-center text-gray-500">
                      No reports found
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <div>
              <CardTitle className="text-base font-medium">{t.statistics.validationTrend}</CardTitle>
              <CardDescription></CardDescription>
            </div>
            <TrendingUp className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{t.statistics.averageScore}</span>
                <span className="font-medium">
                  {stats?.average_score ? `${stats.average_score.toFixed(1)}%` : "N/A"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{t.statistics.successRate}</span>
                <span className="font-medium text-green-600">
                  {stats?.success_rate ? `${(stats.success_rate * 100).toFixed(1)}%` : "N/A"}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div>
            <CardTitle className="text-base font-medium">{t.statistics.systemActivity}</CardTitle>
            <CardDescription></CardDescription>
          </div>
          <Activity className="h-4 w-4 text-gray-400" />
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center space-x-3 text-sm">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              <span className="text-gray-600">System operational</span>
              <span className="text-gray-400 ml-auto">Just now</span>
            </div>
            {recentReports.length > 0 && (
              <div className="flex items-center space-x-3 text-sm">
                <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                <span className="text-gray-600">
                  Report {recentReports[0].filename} validated
                </span>
                <span className="text-gray-400 ml-auto">
                  {new Date(recentReports[0].upload_date).toLocaleString()}
                </span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
