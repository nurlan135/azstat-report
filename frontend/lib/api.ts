const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface ApiResponse<T> {
  data: T
  success: boolean
  message?: string
}

interface Report {
  id: string
  filename: string
  upload_date: string
  validation_status: "valid" | "warning" | "error"
  score: number
  errors_count: number
  warnings_count: number
}

interface ValidationError {
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

interface Statistics {
  total_reports: number
  valid_reports: number
  error_reports: number
  pending_reports: number
  average_score: number
  success_rate: number
}

interface CompareResult {
  reports: Report[]
  comparison: {
    report_id: string
    filename: string
    score: number
    errors_count: number
    warnings_count: number
    validation_status: string
  }[]
}

// Generic fetch wrapper with error handling
async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`

  const config: RequestInit = {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  }

  try {
    const response = await fetch(url, config)

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`API Error: ${response.status} - ${errorText}`)
    }

    return await response.json()
  } catch (error) {
    console.error(`API request failed: ${endpoint}`, error)
    throw error
  }
}

// Upload API
export async function uploadReport(file: File): Promise<Report> {
  const formData = new FormData()
  formData.append("file", file)

  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: "POST",
    body: formData,
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`Upload failed: ${response.status} - ${errorText}`)
  }

  return await response.json()
}

// Get all reports
export async function getReports(filters?: {
  validation_status?: string
}): Promise<Report[]> {
  const params = new URLSearchParams()
  if (filters?.validation_status) {
    params.append("validation_status", filters.validation_status)
  }

  const queryString = params.toString()
  const endpoint = `/api/reports${queryString ? `?${queryString}` : ""}`

  return fetchApi<Report[]>(endpoint)
}

// Get single report by ID
export async function getReport(reportId: string): Promise<Report> {
  return fetchApi<Report>(`/api/reports/${reportId}`)
}

// Get statistics
export async function getStatistics(): Promise<Statistics> {
  return fetchApi<Statistics>("/api/stats")
}

// Get validation errors
export async function getErrors(filters?: {
  status?: string
  severity?: string
}): Promise<ValidationError[]> {
  const params = new URLSearchParams()
  if (filters?.status) {
    params.append("validation_status", filters.status)
  }

  const queryString = params.toString()
  const endpoint = `/api/reports${queryString ? `?${queryString}` : ""}`

  return fetchApi<ValidationError[]>(endpoint)
}

// Compare reports
export async function compareReports(reportIds: string[]): Promise<CompareResult> {
  const params = new URLSearchParams()
  reportIds.forEach((id) => params.append("ids", id))

  return fetchApi<CompareResult>(`/api/reports/compare?${params.toString()}`)
}

export type { Report, ValidationError, Statistics, CompareResult }
