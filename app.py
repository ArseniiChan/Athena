import gradio as gr
import os
from dotenv import load_dotenv
import tempfile
from services.document_ai import extract_text_from_pdf
from services.vertex_ai import generate_podcast_script
from services.text_to_speech import generate_audio

load_dotenv()

def process_pdf(pdf_file, style="conversational"):
    """Main processing pipeline"""
    if pdf_file is None:
        return None, "Please upload a PDF file."
    
    try:
        # Step 1: Extract text
        print("📖 Extracting text from PDF...")
        extracted_text = extract_text_from_pdf(pdf_file.name)
        
        if not extracted_text:
            return None, "Could not extract text from PDF."
        
        # Step 2: Generate script
        print("🧠 Generating podcast script...")
        script = generate_podcast_script(extracted_text, style)
        
        # Step 3: Generate audio
        print("🎙️ Creating audio...")
        audio_path = generate_audio(script[:5000])  # Limit for demo
        
        return audio_path, script
        
    except Exception as e:
        return None, f"Error: {str(e)}"

# Gradio interface
with gr.Blocks(title="Athena - AI Study Companion") as demo:
    gr.Markdown("# 🦉 Athena - Your AI Study Companion")
    gr.Markdown("Transform any PDF into an engaging podcast powered by Google Cloud AI")
    
    with gr.Row():
        with gr.Column():
            pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"])
            style_choice = gr.Radio(
                choices=["conversational", "academic", "simple"],
                value="conversational",
                label="Podcast Style"
            )
            process_btn = gr.Button("🎙️ Generate Podcast", variant="primary")
        
        with gr.Column():
            audio_output = gr.Audio(label="Generated Podcast")
            script_output = gr.Textbox(label="Podcast Script", lines=10)
    
    process_btn.click(
        fn=process_pdf,
        inputs=[pdf_input, style_choice],
        outputs=[audio_output, script_output]
    )

if __name__ == "__main__":
    demo.launch(share=True)