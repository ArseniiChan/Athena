"""FastAPI Backend Server for Athena"""
import os
import logging
from typing import Optional
from pathlib import Path
import tempfile
import shutil

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# Import our services
from services.document_ai import extract_text_from_pdf
from services.vertex_ai import generate_podcast_script, analyze_text_complexity
from services.text_to_speech import generate_audio, VOICE_CONFIGS

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Athena API",
    description="AI-powered PDF to Podcast conversion API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories for uploads and outputs
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Mount static files directory for serving generated audio
app.mount("/static", StaticFiles(directory=str(OUTPUT_DIR)), name="static")


# Pydantic models for requests/responses
class ProcessingRequest(BaseModel):
    style: str = "conversational"
    voice_preset: str = "female_warm"
    duration_minutes: int = 5
    speaking_rate: float = 1.0


class ProcessingResponse(BaseModel):
    success: bool
    audio_url: Optional[str] = None
    transcript: Optional[str] = None
    metadata: Optional[dict] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    services: dict


# Cleanup old files periodically
def cleanup_old_files(directory: Path, max_age_hours: int = 24):
    """Remove files older than max_age_hours"""
    import time
    current_time = time.time()
    
    for file_path in directory.iterdir():
        if file_path.is_file():
            file_age_hours = (current_time - file_path.stat().st_mtime) / 3600
            if file_age_hours > max_age_hours:
                try:
                    file_path.unlink()
                    logger.info(f"Cleaned up old file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to delete {file_path}: {e}")


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        services={
            "api": "running",
            "document_ai": "configured" if os.getenv("DOCUMENTAI_PROCESSOR_ID") else "not configured",
            "vertex_ai": "configured" if os.getenv("GOOGLE_CLOUD_PROJECT") else "not configured",
            "text_to_speech": "configured" if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") else "not configured"
        }
    )


@app.post("/api/process", response_model=ProcessingResponse)
async def process_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    style: str = Form("conversational"),
    voice_preset: str = Form("female_warm"),
    duration_minutes: int = Form(5),
    speaking_rate: float = Form(1.0)
):
    """
    Process a PDF file and generate a podcast.
    
    Args:
        file: PDF file to process
        style: Podcast style (conversational, academic, simple, storytelling)
        voice_preset: Voice configuration preset
        duration_minutes: Target podcast duration
        speaking_rate: Speech rate (0.25 to 4.0)
    
    Returns:
        ProcessingResponse with audio URL and transcript
    """
    # Validate file
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    max_size = 20 * 1024 * 1024  # 20MB
    if file.size > max_size:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size is 20MB")
    
    # Save uploaded file
    temp_pdf = UPLOAD_DIR / f"{tempfile.mktemp().split('/')[-1]}.pdf"
    try:
        with open(temp_pdf, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Processing PDF: {file.filename}")
        
        # Step 1: Extract text
        logger.info("Extracting text from PDF...")
        extracted_text = extract_text_from_pdf(str(temp_pdf))
        
        if not extracted_text:
            raise HTTPException(status_code=422, detail="Could not extract text from PDF")
        
        # Step 2: Analyze complexity
        complexity_info = analyze_text_complexity(extracted_text)
        
        # Step 3: Generate podcast script
        logger.info(f"Generating {style} podcast script...")
        script = generate_podcast_script(
            extracted_text,
            style=style,
            duration_minutes=duration_minutes
        )
        
        if not script:
            raise HTTPException(status_code=500, detail="Failed to generate podcast script")
        
        # Step 4: Generate audio
        logger.info(f"Generating audio with {voice_preset} voice...")
        audio_filename = f"{tempfile.mktemp().split('/')[-1]}.mp3"
        audio_path = OUTPUT_DIR / audio_filename
        
        result = generate_audio(
            script,
            output_path=str(audio_path),
            voice_preset=voice_preset,
            speaking_rate=speaking_rate
        )
        
        if not result or not audio_path.exists():
            # If audio generation fails, return script only
            logger.warning("Audio generation failed, returning script only")
            return ProcessingResponse(
                success=True,
                audio_url=None,
                transcript=script,
                metadata=complexity_info,
                error="Audio generation unavailable - script generated successfully"
            )
        
        # Schedule cleanup
        background_tasks.add_task(cleanup_old_files, UPLOAD_DIR)
        background_tasks.add_task(cleanup_old_files, OUTPUT_DIR)
        
        # Return success response
        audio_url = f"/static/{audio_filename}"
        
        return ProcessingResponse(
            success=True,
            audio_url=audio_url,
            transcript=script,
            metadata={
                **complexity_info,
                "original_filename": file.filename,
                "audio_filename": audio_filename,
                "voice_preset": voice_preset,
                "duration_minutes": duration_minutes
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        if temp_pdf.exists():
            temp_pdf.unlink()


@app.get("/api/voices")
async def get_available_voices():
    """Get list of available voice presets"""
    return {
        "voices": [
            {
                "id": key,
                "name": config["description"],
                "language": config["language_code"]
            }
            for key, config in VOICE_CONFIGS.items()
        ]
    }


@app.get("/api/styles")
async def get_podcast_styles():
    """Get list of available podcast styles"""
    return {
        "styles": [
            {"id": "conversational", "name": "Conversational", "description": "Friendly and engaging"},
            {"id": "academic", "name": "Academic", "description": "Formal and detailed"},
            {"id": "simple", "name": "Simple", "description": "Clear and beginner-friendly"},
            {"id": "storytelling", "name": "Storytelling", "description": "Narrative-driven"}
        ]
    }


@app.get("/api/audio/{filename}")
async def get_audio_file(filename: str):
    """Serve generated audio files"""
    audio_path = OUTPUT_DIR / filename
    
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        path=audio_path,
        media_type="audio/mpeg",
        filename=filename
    )


@app.delete("/api/cleanup")
async def cleanup_files():
    """Manually trigger cleanup of old files"""
    try:
        cleanup_old_files(UPLOAD_DIR, max_age_hours=1)
        cleanup_old_files(OUTPUT_DIR, max_age_hours=1)
        return {"message": "Cleanup completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    
    host = "0.0.0.0"
    port = 8000
    
    logger.info(f"Starting Athena API on {host}:{port}")
    logger.info("Documentation available at http://localhost:8000/docs")
    
    uvicorn.run(app, host=host, port=port, reload=True)