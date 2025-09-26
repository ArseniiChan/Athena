"""Vertex AI Service for generating podcast scripts"""
import os
import logging
from typing import Dict, Optional
import vertexai
from vertexai.generative_models import GenerativeModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Style configurations
STYLE_PROMPTS = {
    "conversational": {
        "description": "Friendly and engaging, like explaining to a friend",
        "tone": "casual, warm, and approachable",
        "pace": "moderate with natural pauses"
    },
    "academic": {
        "description": "Formal and detailed with technical accuracy",
        "tone": "professional and scholarly",
        "pace": "measured and deliberate"
    },
    "simple": {
        "description": "Clear and simple, suitable for beginners",
        "tone": "encouraging and patient",
        "pace": "slow with frequent summaries"
    },
    "storytelling": {
        "description": "Narrative-driven with engaging anecdotes",
        "tone": "dramatic and captivating",
        "pace": "varied for emotional impact"
    }
}


def initialize_vertex_ai() -> bool:
    """
    Initialize Vertex AI with project configuration.
    
    Returns:
        True if initialization successful, False otherwise
    """
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
        
        if not project_id:
            logger.error("GOOGLE_CLOUD_PROJECT environment variable not set")
            return False
        
        vertexai.init(project=project_id, location=location)
        logger.info(f"Initialized Vertex AI for project {project_id} in {location}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Vertex AI: {e}")
        return False


def generate_podcast_script(
    text: str, 
    style: str = "conversational",
    duration_minutes: int = 5,
    include_intro: bool = True,
    include_outro: bool = True
) -> Optional[str]:
    """
    Generate a podcast script using Vertex AI Gemini model.
    
    Args:
        text: Source text to convert into podcast script
        style: Style of the podcast (conversational, academic, simple, storytelling)
        duration_minutes: Target duration of the podcast in minutes
        include_intro: Whether to include an introduction
        include_outro: Whether to include a conclusion
    
    Returns:
        Generated podcast script or None if generation fails
    """
    try:
        # Initialize Vertex AI if not already done
        if not initialize_vertex_ai():
            logger.error("Cannot proceed without Vertex AI initialization")
            return generate_fallback_script(text, style)
        
        # Select model
        model_name = os.getenv('VERTEX_AI_MODEL', 'gemini-1.5-flash')
        model = GenerativeModel(model_name)
        
        # Get style configuration
        style_config = STYLE_PROMPTS.get(style, STYLE_PROMPTS["conversational"])
        
        # Calculate approximate word count for duration
        words_per_minute = 150  # Average speaking pace
        target_words = duration_minutes * words_per_minute
        
        # Prepare the prompt
        prompt = create_podcast_prompt(
            text, 
            style_config, 
            target_words,
            include_intro,
            include_outro
        )
        
        # Generate content
        logger.info(f"Generating {duration_minutes}-minute {style} podcast script")
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": min(8192, target_words * 2),
            }
        )
        
        if not response.text:
            logger.warning("Empty response from Vertex AI")
            return generate_fallback_script(text, style)
        
        logger.info(f"Successfully generated script with {len(response.text.split())} words")
        return format_podcast_script(response.text)
        
    except ImportError:
        logger.error("Vertex AI library not installed")
        logger.info("Install with: pip install google-cloud-aiplatform")
        return generate_fallback_script(text, style)
        
    except Exception as e:
        logger.error(f"Error generating script with Vertex AI: {e}")
        return generate_fallback_script(text, style)


def create_podcast_prompt(
    text: str,
    style_config: Dict,
    target_words: int,
    include_intro: bool,
    include_outro: bool
) -> str:
    """
    Create a detailed prompt for podcast script generation.
    
    Args:
        text: Source text
        style_config: Style configuration dictionary
        target_words: Target word count
        include_intro: Whether to include introduction
        include_outro: Whether to include outro
    
    Returns:
        Formatted prompt string
    """
    # Truncate text if too long
    max_input_chars = 10000
    if len(text) > max_input_chars:
        text = text[:max_input_chars] + "..."
        logger.info(f"Truncated input text to {max_input_chars} characters")
    
    prompt = f"""You are an expert podcast scriptwriter. Convert the following educational content into an engaging podcast script.

STYLE REQUIREMENTS:
- Description: {style_config['description']}
- Tone: {style_config['tone']}
- Pace: {style_config['pace']}

SCRIPT REQUIREMENTS:
- Target length: approximately {target_words} words ({target_words // 150} minutes of speaking)
- Speaking style: Natural, conversational flow with clear transitions
- Audience: General audience interested in learning

STRUCTURE:
"""
    
    if include_intro:
        prompt += """
1. INTRODUCTION (10% of script):
   - Hook the listener with an interesting question or fact
   - Preview what will be covered
   - Set the tone and expectations
"""
    
    prompt += """
2. MAIN CONTENT (80% of script):
   - Break down complex ideas into digestible segments
   - Use analogies and examples to illustrate points
   - Include natural transitions between topics
   - Add rhetorical questions to engage listeners
   - Include brief pauses for emphasis [pause]
"""
    
    if include_outro:
        prompt += """
3. CONCLUSION (10% of script):
   - Summarize key takeaways
   - Provide actionable insights or next steps
   - End with a memorable statement or call-to-action
"""
    
    prompt += f"""

FORMATTING GUIDELINES:
- Use [pause] for dramatic pauses
- Use [emphasis] for words that should be stressed
- Include [music] cues for intro/outro music
- Write in a natural speaking style with contractions
- Avoid overly complex sentences

SOURCE CONTENT:
{text}

GENERATE THE PODCAST SCRIPT:
"""
    
    return prompt


def format_podcast_script(script: str) -> str:
    """
    Format the generated script with proper markers and structure.
    
    Args:
        script: Raw generated script
    
    Returns:
        Formatted script with markers
    """
    # Add standard intro/outro if not present
    if not script.startswith("[music]") and not script.startswith("Welcome"):
        script = "[music fade in]\n\n" + script
    
    if not script.endswith("[music]") and not "thank" in script[-200:].lower():
        script = script + "\n\n[music fade out]"
    
    # Ensure proper formatting
    script = script.replace(" [pause]", "\n[pause]\n")
    script = script.replace("...", "...\n[brief pause]\n")
    
    return script.strip()


def generate_fallback_script(text: str, style: str) -> str:
    """
    Generate a simple fallback script without AI.
    
    Args:
        text: Source text
        style: Requested style
    
    Returns:
        Basic podcast script
    """
    logger.info("Using fallback script generation")
    
    # Extract first meaningful portion of text
    excerpt = text[:1500].strip()
    
    # Create a basic script based on style
    if style == "academic":
        intro = "Welcome to today's educational podcast. We'll be exploring important concepts from the source material."
        tone = "Let's examine this content systematically."
    elif style == "simple":
        intro = "Hi there! Welcome to our learning podcast. Today we're going to break down some interesting ideas in a simple way."
        tone = "Let me explain this in simple terms."
    else:  # conversational
        intro = "Hey everyone! Welcome back to the podcast. Today we've got some fascinating material to discuss."
        tone = "So here's what caught my attention."
    
    script = f"""[music fade in]

{intro}

[pause]

{tone}

{excerpt}

[pause]

What we've covered today provides valuable insights into this topic. The key takeaway here is the importance of understanding these concepts and how they apply to our broader understanding.

Thank you for listening to today's episode. If you found this helpful, consider exploring the source material further for a deeper understanding.

[music fade out]"""
    
    return script


def analyze_text_complexity(text: str) -> Dict:
    """
    Analyze text complexity to recommend podcast style.
    
    Args:
        text: Text to analyze
    
    Returns:
        Dictionary with complexity metrics and recommendations
    """
    # Simple complexity analysis
    words = text.split()
    sentences = text.split('.')
    
    avg_word_length = sum(len(word) for word in words) / max(len(words), 1)
    avg_sentence_length = len(words) / max(len(sentences), 1)
    
    # Determine recommended style
    if avg_word_length > 6 or avg_sentence_length > 20:
        recommended_style = "simple"
        complexity = "high"
    elif avg_word_length > 5 or avg_sentence_length > 15:
        recommended_style = "conversational"
        complexity = "medium"
    else:
        recommended_style = "academic"
        complexity = "low"
    
    return {
        "complexity": complexity,
        "recommended_style": recommended_style,
        "avg_word_length": round(avg_word_length, 2),
        "avg_sentence_length": round(avg_sentence_length, 2),
        "word_count": len(words),
        "estimated_duration_minutes": len(words) / 150
    }