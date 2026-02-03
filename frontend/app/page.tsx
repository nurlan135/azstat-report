"use client"

import { UploadForm } from "@/components/dashboard/upload-form"

export default function Home() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Upload Report</h1>
        <p className="text-gray-500 mt-1">
          Upload your HTML reports for validation and processing
        </p>
      </div>
      <UploadForm />
    </div>
  )
}
