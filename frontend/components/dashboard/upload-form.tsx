"use client"

import { useState, useRef } from "react"
import { Upload, File, X, CheckCircle, AlertCircle, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { cn } from "@/lib/utils"
import { toast } from "sonner"
import { en, type Dictionary } from "@/app/dictionaries/en"
import { uploadReport } from "@/lib/api"

interface UploadedFile {
  id: string
  name: string
  size: number
  type: string
  status: "uploading" | "success" | "error"
  error?: string
}

interface UploadFormProps {
  t?: any
}

export function UploadForm({ t }: UploadFormProps) {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const uploadText = t?.upload || en.upload
  const commonText = t?.common || en.common

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const droppedFiles = Array.from(e.dataTransfer.files)
    addFiles(droppedFiles)
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files ? Array.from(e.target.files) : []
    addFiles(selectedFiles)
  }

  const addFiles = async (newFiles: File[]) => {
    const uploadFiles: UploadedFile[] = newFiles.map((file) => ({
      id: Math.random().toString(36).substring(7),
      name: file.name,
      size: file.size,
      type: file.type,
      status: "uploading",
    }))

    setFiles((prev) => [...prev, ...uploadFiles])

    // Upload files to the API
    for (const file of uploadFiles) {
      try {
        // Find the original file object
        const originalFile = newFiles.find((f) => f.name === file.name)
        if (!originalFile) continue

        await uploadReport(originalFile)
        
        setFiles((prev) =>
          prev.map((f) =>
            f.id === file.id
              ? { ...f, status: "success" as const }
              : f
          )
        )
        toast.success(`File "${file.name}" uploaded successfully`)
      } catch (error) {
        console.error("Upload failed:", error)
        setFiles((prev) =>
          prev.map((f) =>
            f.id === file.id
              ? { 
                  ...f, 
                  status: "error" as const, 
                  error: error instanceof Error ? error.message : "Upload failed" 
                }
              : f
          )
        )
        toast.error(`Failed to upload "${file.name}"`)
      }
    }
  }

  const removeFile = (fileId: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== fileId))
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  const getFileIcon = (fileType: string) => {
    if (fileType.includes("html")) return "📄"
    if (fileType.includes("pdf")) return "📕"
    return "📎"
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{uploadText.title}</CardTitle>
        <CardDescription>
          {uploadText.description}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div
          className={cn(
            "relative border-2 border-dashed rounded-lg p-4 md:p-8 text-center transition-colors",
            isDragging ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-gray-400"
          )}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <Upload className="mx-auto h-10 w-10 md:h-12 md:w-12 text-gray-400 mb-3 md:mb-4" />
          <p className="text-base md:text-lg font-medium text-gray-900 mb-1">
            {uploadText.dragDrop}
          </p>
          <p className="text-xs md:text-sm text-gray-500 mb-3 md:mb-4">{uploadText.browse}</p>
          <div className="relative">
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".html,.htm"
              onChange={handleFileSelect}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
            />
            <Button type="button" variant="outline">
              {uploadText.selectFiles}
            </Button>
          </div>
        </div>

        {files.length > 0 && (
          <div className="mt-6">
            <h3 className="font-medium text-gray-900 mb-3">{uploadText.uploadedFiles}</h3>
            <div className="space-y-2">
              {files.map((file) => (
                <div
                  key={file.id}
                  className="flex flex-col sm:flex-row sm:items-center justify-between p-3 bg-gray-50 rounded-lg gap-2"
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{getFileIcon(file.type)}</span>
                    <div>
                      <p className="font-medium text-gray-900 truncate max-w-[150px] sm:max-w-none">{file.name}</p>
                      <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
                    </div>
                  </div>
                  <div className="flex items-center justify-between sm:justify-end space-x-2">
                    {file.status === "uploading" && (
                      <>
                        <Progress value={45} className="w-16 h-2 sm:w-20" />
                        <Loader2 className="h-4 w-4 animate-spin text-gray-500" />
                      </>
                    )}
                    {file.status === "success" && (
                      <span className="flex items-center text-green-600">
                        <CheckCircle className="h-4 w-4 mr-1" />
                        <span className="text-sm">Uploaded</span>
                      </span>
                    )}
                    {file.status === "error" && (
                      <span className="flex items-center text-red-600">
                        <AlertCircle className="h-4 w-4 mr-1" />
                        <span className="text-sm" title={file.error}>Failed</span>
                      </span>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeFile(file.id)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
