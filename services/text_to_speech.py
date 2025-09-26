"""Text to Speech Service using Google Cloud TTS"""
import os
import logging
from typing import Optional, Tuple
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Voice configurations
VOICE_CONFIGS = {
    "female_warm": {
        "language_code": "en-US",
        "name": "en-US-Neural2-F",
        "ssml_gender": "FEMALE",
        "description": "Warm female voice"
    },
    "female_professional": {
        "language_code": "en-US",
        "name": "en-US-Neural2-C",
        "ssml_gender": "FEMALE",
        "description": "Professional female voice"
    },
    "male_warm": {
        "language_code": "en-US",
        "name": "en-US-Neural2-D",
        "ssml_gender": "MALE",
        "description": "Warm male voice"
    },
    "male_professional": {
        "language_code": "en-US",
        "name": "en-US-Neural2-A",
        "ssml_gender": "MALE",
        "description": "Professional male voice"
    },
    "british_female": {
        "language_code": "en-GB",
        "name": "en-GB-Neural2-A",
        "ssml_gender": "FEMALE",
        "description": "British female voice"
    }
}


def initialize_tts_client():
    """
    Initialize Google Cloud Text-to-Speech client.
    
    Returns:
        TTS client or None if initialization fails
    """
    try:
        from google.cloud import texttospeech
        
        # Check for credentials
        if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS') and not os.getenv('GOOGLE_CLOUD_PROJECT'):
            logger.warning("Google Cloud credentials not configured")
            return None
        
        client = texttospeech.TextToSpeechClient()
        logger.info("Successfully initialized Text-to-Speech client")
        return client
        
    except ImportError:
        logger.error("Google Cloud Text-to-Speech library not installed")
        logger.info("Install with: pip install google-cloud-texttospeech")
        return None
        
    except Exception as e:
        logger.error(f"Failed to initialize TTS client: {e}")
        return None


def generate_audio(
    text: str,
    output_path: str = "output.mp3",
    voice_preset: str = "female_warm",
    speaking_rate: float = 1.0,
    pitch: float = 0.0,
    audio_format: str = "mp3"
) -> Optional[str]:
    """
    Convert text to speech using Google Cloud TTS.
    
    Args:
        text: Text to convert to speech
        output_path: Path for output audio file
        voice_preset: Voice configuration preset
        speaking_rate: Speed of speech (0.25 to 4.0, 1.0 is normal)
        pitch: Voice pitch (-20.0 to 20.0, 0.0 is normal)
        audio_format: Output format (mp3, wav, ogg)
    
    Returns:
        Path to generated audio file or None if generation fails
    """
    try:
        from google.cloud import texttospeech
        
        # Initialize client
        client = initialize_tts_client()
        if not client:
            logger.error("Cannot proceed without TTS client")
            return generate_fallback_audio(text, output_path)
        
        # Process script markers
        text, ssml_text = process_script_markers(text)
        
        # Check text length (Google TTS has a 5000 character limit per request)
        if len(ssml_text) > 5000:
            logger.info("Text too long, truncating for demo")
            ssml_text = ssml_text[:4900] + "</speak>"  # Truncate and close SSML
        
        # Get voice configuration
        voice_config = VOICE_CONFIGS.get(voice_preset, VOICE_CONFIGS["female_warm"])
        
        # Set up synthesis input
        synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)
        
        # Set up voice parameters
        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_config["language_code"],
            name=voice_config["name"],
            ssml_gender=texttospeech.SsmlVoiceGender[voice_config["ssml_gender"]]
        )
        
        # Set up audio configuration
        audio_encoding = get_audio_encoding(audio_format, texttospeech)
        audio_config = texttospeech.AudioConfig(
            audio_encoding=audio_encoding,
            speaking_rate=speaking_rate,
            pitch=pitch,
            effects_profile_id=["headphone-class-device"]  # Optimize for headphones
        )
        
        # Perform text-to-speech request
        logger.info(f"Generating audio with {voice_config['description']}")
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Save audio file
        with open(output_path, "wb") as audio_file:
            audio_file.write(response.audio_content)
        
        logger.info(f"Generated audio saved to {output_path}")
        
        # Save metadata
        save_audio_metadata(output_path, voice_config, len(text))
        
        return output_path
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.info("TTS libraries not properly installed")
        return generate_fallback_audio(text, output_path)
        
    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        logger.info("This might be a permission issue with Text-to-Speech API")
        return generate_fallback_audio(text, output_path)


def process_script_markers(text: str) -> Tuple[str, str]:
    """
    Process podcast script markers and convert to SSML.
    
    Args:
        text: Raw script text with markers
    
    Returns:
        Tuple of (clean text, SSML formatted text)
    """
    import re
    
    # Clean text for fallback
    clean_text = re.sub(r'\[.*?\]', '', text).strip()
    
    # Start building SSML
    ssml_text = text
    
    # Replace markers with SSML tags
    replacements = {
        r'\[pause\]': '<break time="1s"/>',
        r'\[brief pause\]': '<break time="500ms"/>',
        r'\[long pause\]': '<break time="2s"/>',
        r'\[music.*?\]': '<break time="2s"/>',  # Replace music cues with pauses
    }
    
    for pattern, replacement in replacements.items():
        ssml_text = re.sub(pattern, replacement, ssml_text, flags=re.IGNORECASE)
    
    # Escape special characters for XML
    ssml_text = ssml_text.replace('&', '&amp;')
    
    # Wrap in speak tags
    ssml_text = f'<speak>{ssml_text}</speak>'
    
    return clean_text, ssml_text


def get_audio_encoding(audio_format: str, texttospeech):
    """
    Get Google TTS audio encoding enum for format.
    
    Args:
        audio_format: Audio format string
        texttospeech: The texttospeech module
    
    Returns:
        AudioEncoding enum value
    """
    encodings = {
        "mp3": texttospeech.AudioEncoding.MP3,
        "wav": texttospeech.AudioEncoding.LINEAR16,
        "ogg": texttospeech.AudioEncoding.OGG_OPUS
    }
    return encodings.get(audio_format.lower(), texttospeech.AudioEncoding.MP3)


def save_audio_metadata(audio_path: str, voice_config: dict, text_length: int):
    """
    Save metadata about generated audio.
    
    Args:
        audio_path: Path to audio file
        voice_config: Voice configuration used
        text_length: Length of input text
    """
    metadata = {
        "audio_file": audio_path,
        "voice": voice_config["description"],
        "language": voice_config["language_code"],
        "text_length": text_length,
        "words_estimate": text_length // 5,  # Rough estimate
        "generation_timestamp": os.path.getmtime(audio_path) if os.path.exists(audio_path) else None
    }
    
    metadata_path = audio_path.replace('.mp3', '_metadata.json').replace('.wav', '_metadata.json')
    try:
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Metadata saved to {metadata_path}")
    except Exception as e:
        logger.warning(f"Could not save metadata: {e}")


def generate_fallback_audio(text: str, output_path: str) -> Optional[str]:
    """
    Generate a fallback when TTS service is unavailable.
    Returns None to indicate no audio was generated.
    
    Args:
        text: Text that would have been converted
        output_path: Path for output file
    
    Returns:
        None (indicating no audio generated)
    """
    logger.warning("Text-to-Speech unavailable - returning transcript only")
    
    try:
        # Save the script as a text file for reference
        text_path = output_path.replace('.mp3', '_script.txt').replace('.wav', '_script.txt')
        with open(text_path, 'w') as f:
            f.write("PODCAST SCRIPT\n")
            f.write("=" * 50 + "\n\n")
            f.write(text)
        
        logger.info(f"Script saved to {text_path}")
        
    except Exception as e:
        logger.error(f"Failed to save script: {e}")
    
    # Return None to indicate no audio was generated
    return None


def list_available_voices(language_code: str = "en-US") -> list:
    """
    List all available voices for a language.
    
    Args:
        language_code: Language code to filter voices
    
    Returns:
        List of available voice names
    """
    try:
        client = initialize_tts_client()
        if not client:
            return []
        
        voices = client.list_voices(language_code=language_code)
        
        voice_list = []
        for voice in voices.voices:
            voice_list.append({
                "name": voice.name,
                "language": voice.language_codes[0],
                "gender": voice.ssml_gender.name
            })
        
        return voice_list
        
    except Exception as e:
        logger.error(f"Error listing voices: {e}")
        return []


# For testing purposes
if __name__ == "__main__":
    test_text = "Hello, this is a test of the text to speech system."
    result = generate_audio(test_text, "test_output.mp3")
    if result:
        print(f"Audio generated: {result}")
    else:
        print("Audio generation failed, but script was saved")