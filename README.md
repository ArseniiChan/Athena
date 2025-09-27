# Athena - AI-Powered PDF to Podcast Converter

Transform any PDF into an engaging, personalized podcast using Google Cloud AI services. Built for the BYTE Hackathon 2025.

## What is Athena?

Athena is an AI-powered platform that converts PDF documents into natural-sounding podcasts, making learning more accessible and flexible. Whether you're a student with mountains of reading material, a professional catching up on reports, or someone who prefers audio learning, Athena transforms your documents into engaging audio content you can enjoy anywhere.

### Key Features

- **Smart Text Extraction**: Uses Google Document AI with OCR support for both text and scanned PDFs
- **AI-Powered Scripts**: Leverages Vertex AI's **Gemini 2.0 Flash** model to create engaging narratives, not just verbatim reading
- **Natural Voice Synthesis**: Multiple voice options via Google Cloud Text-to-Speech with SSML support
- **Multiple Styles**: Choose from conversational, academic, simple, or storytelling formats
- **Fast Processing**: Get your personalized podcast in seconds
- **Modern Web Interface**: Clean, responsive UI built with Next.js and TypeScript
- **Accessibility Impact**: Perfect for auditory learners, students with dyslexia, or anyone studying on the go

## Demo Video
[![Watch the demo](https://img.youtube.com/vi/uJn69T-uYrI/0.jpg)](https://www.youtube.com/watch?v=uJn69T-uYrI)

## Hackathon Achievement

Built in under 24 hours for BYTE Hackathon 2025, Athena demonstrates the power of Google Cloud AI services working in harmony to solve a real problem students face every day.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Cloud Project with APIs enabled
- Service Account credentials

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/your-username/athena.git
cd athena
```

#### 2. Backend Setup

```bash
# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (use minimal for faster setup)
pip install -r requirements-minimal.txt

# Create .env file with your Google Cloud credentials
cp .env.example .env
# Edit .env with your credentials

# Run the backend
python api_server.py
```

The API will be available at `http://localhost:8000`  
API documentation at `http://localhost:8000/docs`

#### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd athena-web

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_BACKEND_URL=http://localhost:8000" > .env.local

# Run the development server
npm run dev
```

The web interface will be available at `http://localhost:3000`

### Docker Setup (Alternative)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

## Environment Configuration

### Backend (.env)

```env
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json

# Google Cloud AI Services
VERTEX_AI_MODEL=gemini-2.0-flash
DOCUMENTAI_PROCESSOR_ID=your-processor-id  # Optional, for OCR

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## Google Cloud Setup

### Required APIs

Enable these in your Google Cloud Console:
1. **Vertex AI API** - For Gemini 2.0 Flash model
2. **Document AI API** - For PDF text extraction and OCR
3. **Cloud Text-to-Speech API** - For audio generation

### Quick Enable Command

```bash
gcloud services enable \
  aiplatform.googleapis.com \
  documentai.googleapis.com \
  texttospeech.googleapis.com
```

### Service Account Setup

1. Create a service account in Google Cloud Console
2. Grant these roles:
   - `Vertex AI User`
   - `Document AI API User`
   - `Cloud Text-to-Speech User`
3. Download the JSON key as `service-account-key.json`
4. Place it in the project root (it's in .gitignore for security)

## Architecture

### Tech Stack

**Backend (Python + FastAPI)**
- FastAPI for high-performance REST API
- Google Document AI for intelligent PDF extraction
- Vertex AI with Gemini 2.0 Flash for script generation
- Google Cloud Text-to-Speech for audio synthesis
- Docker containerization for deployment

**Frontend (Next.js + TypeScript)**
- Next.js 14 with App Router
- TypeScript for type safety
- Tailwind CSS for styling
- Async file uploads with progress tracking

**Infrastructure**
- Docker Compose for multi-container orchestration
- Health checks and automatic restarts
- CORS configuration for secure communication
- Volume mounts for persistent storage

## Project Structure

```
athena/
├── api_server.py           # FastAPI backend server
├── requirements.txt        # Python dependencies
├── Dockerfile             # Backend container
├── docker-compose.yml     # Multi-container setup
├── .env.example          # Environment template
│
├── services/             # Core business logic
│   ├── document_ai.py    # PDF text extraction
│   ├── vertex_ai.py      # Podcast script generation  
│   └── text_to_speech.py # Audio generation
│
├── athena-web/          # Next.js frontend
│   ├── app/            # App router pages
│   ├── components/     # React components
│   ├── public/        # Static assets
│   └── Dockerfile    # Frontend container
│
├── uploads/           # Temporary PDF storage (gitignored)
└── outputs/          # Generated audio files (gitignored)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check and service status |
| `/api/process` | POST | Process PDF and generate podcast |
| `/api/voices` | GET | List available voice presets |
| `/api/styles` | GET | List podcast style options |
| `/api/audio/{filename}` | GET | Download generated audio |

### Example Usage

```bash
# Process a PDF
curl -X POST "http://localhost:8000/api/process" \
  -F "file=@lecture.pdf" \
  -F "style=conversational" \
  -F "voice_preset=female_warm" \
  -F "duration_minutes=5"

# Response
{
  "success": true,
  "audio_url": "/static/tmp123.mp3",
  "transcript": "Welcome to today's fascinating exploration...",
  "metadata": {
    "complexity": "medium",
    "word_count": 750
  }
}
```

## Customization Options

### Podcast Styles
- **Conversational**: Friendly and engaging, like explaining to a friend
- **Academic**: Formal and detailed with technical accuracy  
- **Simple**: Clear and beginner-friendly with frequent summaries
- **Storytelling**: Narrative-driven with engaging anecdotes

### Voice Presets
- Female Warm (en-US-Neural2-F)
- Female Professional (en-US-Neural2-C)
- Male Warm (en-US-Neural2-D)
- Male Professional (en-US-Neural2-A)
- British Female (en-GB-Neural2-A)

## Known Limitations

- **File Size**: Maximum 20MB per PDF
- **Text Length**: 5000 character limit per TTS request (auto-truncated)
- **Pages**: Processes up to 10 pages by default (configurable)
- **Rate Limits**: Subject to Google Cloud API quotas

## Deployment

### Google Cloud Run

```bash
# Build and deploy backend
gcloud builds submit --tag gcr.io/YOUR_PROJECT/athena-backend
gcloud run deploy athena-backend --image gcr.io/YOUR_PROJECT/athena-backend

# Deploy frontend to Vercel
cd athena-web && vercel --prod
```

## Contributing

We welcome contributions! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for **BYTE Hackathon 2025**
- Powered by **Google Cloud AI** services
- Special thanks to **Gemini 2.0 Flash** for making this possible
- Inspired by students everywhere struggling with reading overload

## Team

- **Arsenii Chan** - Backend Development & AI Integration
- **Angus Chen** - Frontend Development & UI/UX

## Contact

- Project Link: https://github.com/ArseniiChan/Athena

---

<p align="center">
  <b>Making learning accessible, one PDF at a time</b><br>
  Built with Google Cloud AI
</p>