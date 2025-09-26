import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export async function POST(request: NextRequest) {
  try {
    // Get form data from request
    const formData = await request.formData()
    const file = formData.get('file') as File
    
    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 })
    }

    // Validate file type
    if (!file.name.endsWith('.pdf')) {
      return NextResponse.json({ error: 'Only PDF files are supported' }, { status: 400 })
    }

    // Validate file size (20MB max)
    const MAX_SIZE = 20 * 1024 * 1024
    if (file.size > MAX_SIZE) {
      return NextResponse.json({ error: 'File size exceeds 20MB limit' }, { status: 400 })
    }

    // Forward request to Python backend
    const backendFormData = new FormData()
    backendFormData.append('file', file)
    backendFormData.append('style', formData.get('style') || 'conversational')
    backendFormData.append('voice_preset', formData.get('voice_preset') || 'female_warm')
    backendFormData.append('duration_minutes', formData.get('duration_minutes') || '5')
    backendFormData.append('speaking_rate', formData.get('speaking_rate') || '1.0')

    const response = await fetch(`${BACKEND_URL}/api/process`, {
      method: 'POST',
      body: backendFormData,
    })

    if (!response.ok) {
      const error = await response.json()
      return NextResponse.json(
        { error: error.detail || 'Processing failed' },
        { status: response.status }
      )
    }

    const data = await response.json()
    
    // Transform backend response for frontend
    return NextResponse.json({
      success: data.success,
      audioUrl: data.audio_url ? `${BACKEND_URL}${data.audio_url}` : null,
      transcript: data.transcript,
      metadata: data.metadata,
      error: data.error
    })

  } catch (error) {
    console.error('API route error:', error)
    return NextResponse.json(
      { error: 'Failed to process PDF', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    )
  }
}

export async function GET() {
  // Health check endpoint
  try {
    const response = await fetch(`${BACKEND_URL}/`)
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    return NextResponse.json(
      { status: 'error', message: 'Backend not accessible' },
      { status: 503 }
    )
  }
}