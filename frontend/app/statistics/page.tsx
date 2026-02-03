"use client"

import { StatisticsCards } from "@/components/dashboard/statistics-cards"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { BarChart3, TrendingUp, Activity } from "lucide-react"

// Mock data for demonstration
const mockStats = {
  totalReports: 156,
  validReports: 142,
  errorsCount: 14,
  pendingReports: 0,
}

const recentReports = [
  { name: "Q4_2024_Report.html", status: "Valid", validationDate: "2024-02-03", score: 98 },
  { name: "Monthly_Summary_Dec.html", status: "Valid", validationDate: "2024-02-02", score: 95 },
  { name: "Annual_Report_2023.html", status: "Warning", validationDate: "2024-02-01", score: 87 },
  { name: "Performance_Review.html", status: "Error", validationDate: "2024-01-31", score: 72 },
  { name: "Budget_Analysis.html", status: "Valid", validationDate: "2024-01-30", score: 96 },
]

export default function StatisticsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Statistics</h1>
        <p className="text-gray-500 mt-1">
          Overview of your report validation metrics
        </p>
      </div>

      <StatisticsCards {...mockStats} />

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <div>
              <CardTitle className="text-base font-medium">Recent Reports</CardTitle>
              <CardDescription>Latest 5 validated reports</CardDescription>
            </div>
            <BarChart3 className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Report Name</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Score</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recentReports.map((report) => (
                  <TableRow key={report.name}>
                    <TableCell className="font-medium truncate max-w-[200px]">
                      {report.name}
                    </TableCell>
                    <TableCell>
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          report.status === "Valid"
                            ? "bg-green-100 text-green-800"
                            : report.status === "Warning"
                            ? "bg-yellow-100 text-yellow-800"
                            : "bg-red-100 text-red-800"
                        }`}
                      >
                        {report.status}
                      </span>
                    </TableCell>
                    <TableCell className="text-right font-medium">{report.score}%</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <div>
              <CardTitle className="text-base font-medium">Validation Trend</CardTitle>
              <CardDescription>Reports processed over time</CardDescription>
            </div>
            <TrendingUp className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">This Week</span>
                <span className="font-medium">24 reports</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">This Month</span>
                <span className="font-medium">89 reports</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">This Quarter</span>
                <span className="font-medium">156 reports</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Average Score</span>
                <span className="font-medium">94.2%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Success Rate</span>
                <span className="font-medium text-green-600">91.0%</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div>
            <CardTitle className="text-base font-medium">System Activity</CardTitle>
            <CardDescription>Recent validation activity</CardDescription>
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
            <div className="flex items-center space-x-3 text-sm">
              <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
              <span className="text-gray-600">Report Q4_2024_Report.html validated</span>
              <span className="text-gray-400 ml-auto">2 min ago</span>
            </div>
            <div className="flex items-center space-x-3 text-sm">
              <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
              <span className="text-gray-600">Report Monthly_Summary_Dec.html validated</span>
              <span className="text-gray-400 ml-auto">15 min ago</span>
            </div>
            <div className="flex items-center space-x-3 text-sm">
              <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
              <span className="text-gray-600">Warning detected in Annual_Report_2023.html</span>
              <span className="text-gray-400 ml-auto">1 hour ago</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
