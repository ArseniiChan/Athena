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
      toast.error("File too large. Maximum size is 25MB")
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
    <div style={{ display: "grid", gap: "1rem" }}>
      <div>
        <label className="feature-number" style={{ 
          display: "block", 
          marginBottom: ".5rem",
          textAlign: "center"
        }}>
          Upload document
        </label>
        <div
          className={`btn btn-secondary ${
            isDragging ? "bg-gray-100" : ""
          }`}
          style={{
            width: "100%",
            textAlign: "center",
            borderColor: selectedFile ? "var(--athena-accent)" : isDragging ? "black" : "var(--athena-gray-300)",
            background: selectedFile ? "var(--athena-gray-50)" : isDragging ? "var(--athena-gray-100)" : "white",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "0.5rem"
          }}
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
          
          {selectedFile ? (
            <>
              <svg
                className="h-4 w-4"
                style={{ color: "var(--athena-accent)" }}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span style={{ fontSize: "14px" }}>{selectedFile}</span>
            </>
          ) : (
            <>
              <svg
                className="h-4 w-4"
                style={{ color: "var(--athena-gray-600)" }}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={1.5}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M18.375 12.739l-7.693 7.693a4.5 4.5 0 01-6.364-6.364l10.94-10.94A3 3 0 1119.5 7.372L8.552 18.32m.009-.01l-.01.01m5.699-9.941l-7.81 7.81a1.5 1.5 0 002.112 2.13"
                />
              </svg>
              <span>{isDragging ? "Drop PDF here" : "Choose PDF file"}</span>
            </>
          )}
        </div>
        {selectedFile && (
          <div className="upload-subtext" style={{ 
            marginTop: "0.25rem",
            textAlign: "center"
          }}>
            Click to replace file
          </div>
        )}
      </div>
    </div>
  )
}