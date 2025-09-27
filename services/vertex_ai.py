"""Vertex AI Service for generating podcast scripts"""
import os
import logging
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import Vertex AI, but don't fail if not available
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    logger.warning("Vertex AI not available - using fallback script generation")


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
    if not VERTEX_AI_AVAILABLE:
        return False
        
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
        
        if not project_id:
            logger.error("GOOGLE_CLOUD_PROJECT environment variable not set")
            return False
        
        logger.info(f"Attempting to init Vertex AI with project={project_id}, location={location}")
        vertexai.init(project=project_id, location=location)
        logger.info(f"✓ Successfully initialized Vertex AI for project {project_id} in {location}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to initialize Vertex AI: {type(e).__name__}: {e}")
        return False


def generate_podcast_script(
    text: str, 
    style: str = "conversational",
    duration_minutes: int = 5,
    include_intro: bool = True,
    include_outro: bool = True
) -> Optional[str]:
    """
    Generate a podcast script using Vertex AI Gemini model or fallback.
    
    Args:
        text: Source text to convert into podcast script
        style: Style of the podcast (conversational, academic, simple, storytelling)
        duration_minutes: Target duration of the podcast in minutes
        include_intro: Whether to include an introduction
        include_outro: Whether to include a conclusion
    
    Returns:
        Generated podcast script or None if generation fails
    """
    # If Vertex AI not available, use fallback immediately
    if not VERTEX_AI_AVAILABLE:
        logger.info("Using fallback script generation (Vertex AI not available)")
        return generate_fallback_script(text, style)
    
    try:
        # Initialize Vertex AI if not already done
        if not initialize_vertex_ai():
            logger.error("✗ Vertex AI initialization failed - using fallback")
            return generate_fallback_script(text, style)
        
        # Select model
        model_name = os.getenv('VERTEX_AI_MODEL', 'gemini-2.0-flash')
        logger.info(f"Creating model: {model_name}")
        
        try:
            model = GenerativeModel(model_name)
            logger.info(f"✓ Model '{model_name}' created successfully")
        except Exception as model_error:
            logger.error(f"✗ Failed to create model: {model_error}")
            return generate_fallback_script(text, style)
        
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
        
        logger.info(f"Prompt created, length: {len(prompt)} chars")
        
        # Generate content
        logger.info(f"Calling Gemini API to generate {target_words}-word script...")
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.8,
                "top_p": 0.85,
                "top_k": 40,
                "max_output_tokens": min(8192, target_words * 2),
            }
        )
        
        if not response or not response.text:
            logger.warning("✗ Empty response from Vertex AI")
            return generate_fallback_script(text, style)
        
        logger.info(f"✓ Successfully generated script with {len(response.text.split())} words")
        return format_podcast_script(response.text)
        
    except Exception as e:
        logger.error(f"✗ Unexpected error generating script: {type(e).__name__}: {e}")
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
    
    prompt = f"""You are an expert podcast host who transforms academic content into engaging audio experiences.

CRITICAL INSTRUCTIONS:
- DO NOT simply read the document verbatim or quote it directly
- DO NOT say things like "the document states" or "according to the text"
- CREATE an engaging narrative that teaches the concepts
- EXPLAIN ideas in your own words as if you're having a conversation
- USE analogies, examples, and storytelling to make concepts memorable
- SYNTHESIZE the information into insights, not just repeat facts

STYLE REQUIREMENTS:
- Description: {style_config['description']}
- Tone: {style_config['tone']}
- Pace: {style_config['pace']}

SCRIPT REQUIREMENTS:
- Target length: approximately {target_words} words ({target_words // 150} minutes of speaking)
- Speaking style: Like you're explaining to a friend who's genuinely interested
- Audience: Someone who wants to understand the topic, not just hear it read

STRUCTURE:
"""
    
    if include_intro:
        prompt += """
1. INTRODUCTION (15% of script):
   - Start with a relatable hook or interesting question
   - Connect the topic to real-world applications
   - Give listeners a reason to care about this topic
   - Preview the main insights they'll gain
"""
    
    prompt += """
2. MAIN CONTENT (70% of script):
   - Transform key concepts into conversational explanations
   - Use "Let me explain this differently..." or "Think of it this way..."
   - Add personal touches like "What I find fascinating is..."
   - Include rhetorical questions: "Ever wondered why...?"
   - Use concrete examples and analogies
   - Create a narrative thread that connects ideas
   - Add [pause] markers for natural breathing spaces
   - Build understanding progressively, don't just list facts
"""
    
    if include_outro:
        prompt += """
3. CONCLUSION (15% of script):
   - Synthesize the main insights (don't just repeat them)
   - Explain why these concepts matter in the bigger picture
   - Suggest how listeners can apply or explore these ideas further
   - End with a thought-provoking question or memorable insight
"""
    
    prompt += f"""

EXAMPLES OF GOOD TRANSFORMATIONS:
BAD (verbatim): "The document states that mitochondria are the powerhouse of the cell."
GOOD (engaging): "You know how a city needs power plants to keep the lights on? Well, your cells have their own tiny power plants called mitochondria, and they're absolutely fascinating..."

BAD (reading): "Section 2.3 discusses three types of market structures."
GOOD (conversational): "So imagine you're starting a business. The success you'll have depends hugely on what kind of market you're entering. Let me walk you through three completely different scenarios..."

FORMATTING:
- Use [pause] for natural breaks
- Use [emphasis] sparingly for key words
- Start with [music fade in] and end with [music fade out]
- Write conversationally with contractions (it's, we'll, you're)

SOURCE CONTENT TO TRANSFORM (not read):
{text}

REMEMBER: You're a podcast host sharing fascinating insights, not a text-to-speech robot. Make this content come alive through storytelling and explanation.

GENERATE THE ENGAGING PODCAST SCRIPT:
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
    logger.info("Using fallback script generation (Vertex AI not available)")
    
    # Extract key points from text (first 1000 chars)
    excerpt = text[:1000].strip()
    
    # Identify the topic (usually in first few sentences)
    first_sentence = excerpt.split('.')[0] if '.' in excerpt else excerpt[:100]
    
    # Create a basic but engaging script based on style
    if style == "academic":
        intro = "Welcome to today's educational podcast where we explore fascinating academic concepts."
        tone = "Let's dive deep into understanding"
    elif style == "simple":
        intro = "Hey there! Welcome to our learning podcast where we make complex ideas simple and fun."
        tone = "Let me break this down in a way that just makes sense"
    else:  # conversational
        intro = "Hey everyone! Welcome back. Today we're diving into something really interesting."
        tone = "So here's what really caught my attention"
    
    script = f"""[music fade in]

{intro}

[pause]

Today's topic is all about {first_sentence.lower()}. {tone}.

[pause]

Think about it this way - we encounter these concepts every day, but rarely stop to understand what's really happening behind the scenes. That's what we're going to explore today.

[pause]

{excerpt}

[pause]

What I find most fascinating about this is how it connects to our everyday experiences. These aren't just abstract concepts - they're principles that shape the world around us.

The key insight here is understanding not just what happens, but why it matters. When you grasp these fundamentals, suddenly a lot of other things start to make sense too.

[pause]

So next time you encounter this topic, remember what we discussed today. Think about the bigger picture and how these pieces fit together.

Thanks for joining me on this exploration. Until next time, keep questioning, keep learning, and keep discovering.

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