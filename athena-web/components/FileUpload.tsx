"use client"

import { useRef, useState } from "react"
import { toast } from "sonner"

type Props = {
  onValidFile: (file: File) => void
}

export default function FileUpload({ onValidFile }: Props) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)

  const handleFile = (file: File) => {
    if (!file.type.includes("pdf")) {
      toast.error("Please upload a PDF file")
      return
    }
    if (file.size > 25 * 1024 * 1024) {
      toast.error("File too large. Max size is 25MB")
      return
    }
    setSelectedFile(file.name)
    onValidFile(file)
    toast.success(`Loaded: ${file.name}`)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }

  return (
    <div
      className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${
        isDragging ? "border-blue-500 bg-blue-50" : "border-gray-300"
      } ${selectedFile ? "bg-green-50 border-green-400" : ""}`}
      onDragOver={(e) => {
        e.preventDefault()
        setIsDragging(true)
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current?.click()}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        onChange={handleFileSelect}
        className="hidden"
      />
      <svg
        className="mx-auto h-12 w-12 text-gray-400 mb-4"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
        />
      </svg>
      {selectedFile ? (
        <div>
          <p className="text-lg font-medium text-green-600">File loaded:</p>
          <p className="text-sm text-gray-600 mt-1">{selectedFile}</p>
          <p className="text-xs text-gray-500 mt-2">Click to change file</p>
        </div>
      ) : (
        <>
          <p className="text-lg font-medium">Drop your PDF here or click to browse</p>
          <p className="text-sm text-gray-500 mt-2">PDF only • up to 25MB</p>
        </>
      )}
    </div>
  )
}
