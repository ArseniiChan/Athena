import { NextRequest, NextResponse } from "next/server"

export async function POST(req: NextRequest) {
  const form = await req.formData()
  const file = form.get("file") as File | null
  const style = (form.get("style") as string) || "conversational"
  const speed = Number(form.get("speed") || 1.0)

  if (!file) return NextResponse.json({ error: "No file provided" }, { status: 400 })
  const isPdf = file.type === "application/pdf" || file.name?.toLowerCase().endsWith(".pdf")
  if (!isPdf) return NextResponse.json({ error: "Only PDF files are allowed" }, { status: 400 })

  // TODO: Forward to your Python service (Cloud Run). For now, return a demo mp3.
  return NextResponse.json({
    ok: true,
    audioUrl: "/audio/demo.mp3",
    script: `Demo script for "${file.name}" • style=${style} • speed=${speed}`,
  })
}
