"use client"

import { useRef, useState } from "react"
import { toast } from "sonner"

type Props = {
  onValidFile: (file: File) => void
  maxSizeMB?: number
}

export default function FileUpload({ onValidFile, maxSizeMB = 25 }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragOver, setDragOver] = useState(false)

  const accept = "application/pdf"

  const validate = (f: File) => {
    const isPdf = f.type === accept || f.name.toLowerCase().endsWith(".pdf")
    if (!isPdf) {
      toast.error("Only PDF files are allowed")
      return false
    }
    const tooBig = f.size > maxSizeMB * 1024 * 1024
    if (tooBig) {
      toast.error(`File is too large. Max ${maxSizeMB}MB`)
      return false
    }
    return true
  }

  const handleFiles = (files?: FileList | null) => {
    const f = files?.[0]
    if (!f) return
    if (!validate(f)) return
    onValidFile(f)
  }

  return (
    <div
      className={`upload-area ${dragOver ? "ring-2 ring-black/50" : ""}`}
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFiles(e.dataTransfer.files) }}
      role="button"
      aria-label="Upload PDF"
    >
      <svg className="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
        strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
        <polyline points="17 8 12 3 7 8"></polyline>
        <line x1="12" y1="3" x2="12" y2="15"></line>
      </svg>
      <div className="upload-text">Drop your PDF here or click to browse</div>
      <div className="upload-subtext">PDF only • up to {maxSizeMB}MB</div>

      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={(e) => handleFiles(e.currentTarget.files)}
      />
    </div>
  )
}
