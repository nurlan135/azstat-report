"use client"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { AlertCircle, XCircle, CheckCircle } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

export interface ErrorItem {
  id: string
  reportName: string
  errorType: string
  message: string
  line?: number
  column?: number
  severity: "error" | "warning" | "info"
  status: "pending" | "resolved" | "ignored"
  timestamp: string
}

// API response type
export interface ValidationError {
  id: string
  report_id: string
  report_name: string
  error_type: string
  message: string
  line?: number
  column?: number
  severity: "error" | "warning" | "info"
  status: "pending" | "resolved" | "ignored"
  timestamp: string
}

interface ErrorListProps {
  errors: ErrorItem[] | ValidationError[]
}

const severityConfig = {
  error: { icon: XCircle, color: "text-red-600", badge: "bg-red-100 text-red-800" },
  warning: { icon: AlertCircle, color: "text-yellow-600", badge: "bg-yellow-100 text-yellow-800" },
  info: { icon: CheckCircle, color: "text-blue-600", badge: "bg-blue-100 text-blue-800" },
}

const statusConfig = {
  pending: { label: "Pending", className: "bg-gray-100 text-gray-800" },
  resolved: { label: "Resolved", className: "bg-green-100 text-green-800" },
  ignored: { label: "Ignored", className: "bg-gray-100 text-gray-600" },
}

// Transform API response to ErrorItem format
const transformError = (error: ErrorItem | ValidationError): ErrorItem => {
  if ("reportName" in error) {
    return error as ErrorItem
  }
  return {
    id: error.id,
    reportName: error.report_name,
    errorType: error.error_type,
    message: error.message,
    line: error.line,
    column: error.column,
    severity: error.severity,
    status: error.status,
    timestamp: error.timestamp,
  }
}

export function ErrorList({ errors }: ErrorListProps) {
  if (errors.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <CheckCircle className="h-12 w-12 text-green-500 mb-4" />
        <h3 className="text-lg font-medium text-gray-900">No Errors Found</h3>
        <p className="text-gray-500 mt-1">All reports have been validated successfully.</p>
      </div>
    )
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[180px]">Report Name</TableHead>
            <TableHead className="w-[120px]">Severity</TableHead>
            <TableHead>Error Message</TableHead>
            <TableHead className="w-[100px]">Line</TableHead>
            <TableHead className="w-[120px]">Status</TableHead>
            <TableHead className="w-[180px]">Timestamp</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {errors.map((error) => {
            const transformedError = transformError(error)
            const severity = severityConfig[transformedError.severity]
            const status = statusConfig[transformedError.status]
            const SeverityIcon = severity.icon

            return (
              <TableRow key={transformedError.id}>
                <TableCell className="font-medium">{transformedError.reportName}</TableCell>
                <TableCell>
                  <Badge className={severity.badge}>
                    <SeverityIcon className={cn("mr-1 h-3 w-3", severity.color)} />
                    {transformedError.severity}
                  </Badge>
                </TableCell>
                <TableCell>
                  <div>
                    <span className="font-medium">{transformedError.errorType}</span>
                    <p className="text-sm text-gray-500 mt-0.5">{transformedError.message}</p>
                  </div>
                </TableCell>
                <TableCell>
                  {transformedError.line && (
                    <span className="text-sm text-gray-600">
                      {transformedError.line}
                      {transformedError.column && `:${transformedError.column}`}
                    </span>
                  )}
                </TableCell>
                <TableCell>
                  <Badge className={status.className}>{status.label}</Badge>
                </TableCell>
                <TableCell className="text-sm text-gray-500">
                  {new Date(transformedError.timestamp).toLocaleString()}
                </TableCell>
              </TableRow>
            )
          })}
        </TableBody>
      </Table>
    </div>
  )
}
