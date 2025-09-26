import vertexai
from vertexai.generative_models import GenerativeModel
import os

def generate_podcast_script(text, style="conversational"):
    """Generate podcast script using Vertex AI"""
    try:
        vertexai.init(
            project=os.getenv('GOOGLE_CLOUD_PROJECT'),
            location=os.getenv('GOOGLE_CLOUD_LOCATION')
        )
        
        model = GenerativeModel("gemini-1.5-flash")
        
        style_prompts = {
            "conversational": "Make it friendly and engaging, like explaining to a friend.",
            "academic": "Keep it formal and detailed with technical accuracy.",
            "simple": "Explain it simply, suitable for beginners."
        }
        
        prompt = f"""
        Convert this educational content into a podcast script.
        Style: {style_prompts.get(style, style_prompts["conversational"])}
        
        Add:
        - An engaging introduction
        - Clear explanations of main points
        - A memorable conclusion
        
        Keep it under 2 minutes of speaking time.
        
        Content:
        {text[:3000]}
        
        Podcast Script:
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating script: {e}")
        # Fallback response
        return f"Welcome to your AI-generated podcast! Today we're discussing the content from your PDF. {text[:500]}..."