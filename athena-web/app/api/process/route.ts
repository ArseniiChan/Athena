import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  const formData = await request.formData()
  const file = formData.get('file') as File
  
  if (!file) {
    return NextResponse.json({ error: 'No file provided' }, { status: 400 })
  }

  // For hackathon demo, just return mock data
  // In production, this would call your Python backend
  
  return NextResponse.json({
    success: true,
    audioUrl: '/demo-podcast.mp3',
    transcript: 'This is a demo transcript of your PDF content...'
  })
}