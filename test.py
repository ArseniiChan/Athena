import gradio as gr
print("✅ Gradio imported successfully!")

def greet(name):
    return f"Hello {name}! Athena is ready! 🚀"

demo = gr.Interface(fn=greet, inputs="text", outputs="text", title="Athena Test")

if __name__ == "__main__":
    print("Launching test interface...")
    demo.launch()
