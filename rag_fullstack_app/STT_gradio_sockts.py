import gradio as gr
import websockets
import asyncio
import json
from transformers import pipeline

# Load Whisper model for speech-to-text transcription
whisper_model = pipeline("automatic-speech-recognition", model="openai/whisper-small", device='cpu')

# WebSocket URL of your FastAPI backend (adjust if necessary)
WS_URL = "ws://localhost:8000/ws/chat"  # Ensure this is your FastAPI WebSocket endpoint

# Function to handle WebSocket communication for text and audio queries
async def send_ws_query(query):
    try:
        # Establish WebSocket connection
        async with websockets.connect(WS_URL) as websocket:
            # Send the query to the backend via WebSocket
            await websocket.send(query)

            # Wait for the response
            response = await websocket.recv()
            return response
    except Exception as e:
        return f"Error: {str(e)}"

# Function to transcribe audio using Whisper and send query via WebSocket
async def transcribe_and_query_ws(audio, history):
    # Transcribe audio to text
    transcription = whisper_model(audio)["text"]

    # Query via WebSocket with transcription
    result = await send_ws_query(transcription)
    
    # Append transcription and result to chat history
    history.append((transcription, result))
    
    return result, history

# Function to send text query via WebSocket
async def process_text_query_ws(query, history):
    # Query via WebSocket with the input text
    result = await send_ws_query(query)
    
    # Append query and result to chat history
    history.append((query, result))
    
    return result, history

# Function to clear inputs and history
def clear_fields():
    return None, []  # Reset the audio and chat history

# Gradio interface for RAG app with enhanced UI and WebSocket functionality
def gradio_interface():
    with gr.Blocks() as ui:
        gr.Markdown("<h1 style='text-align: center; color: #4CAF50;'>RAG-based Chat with Speech and Text Queries (WebSockets)</h1>")

        # Chat history to store previous transcriptions and queries
        chat_history = gr.State([])

        with gr.Row():
            audio_input = gr.Audio(type="filepath", label="Upload or Record Audio for Query")
            text_input = gr.Textbox(label="Or Enter Text Query")
        
        with gr.Row():
            result_output = gr.Textbox(label="RAG Response Output", lines=5)
        
        with gr.Row():
            transcribe_button = gr.Button("Process Audio", variant="primary")
            text_button = gr.Button("Process Text", variant="primary")
            clear_button = gr.Button("Clear", variant="secondary")
        
        # Display chat history (previous queries and results)
        history_display = gr.Chatbot(label="Chat History")

        # Define functions for WebSocket communication
        transcribe_button.click(fn=lambda audio, history: asyncio.run(transcribe_and_query_ws(audio, history)), 
                                inputs=[audio_input, chat_history], outputs=[result_output, history_display])

        text_button.click(fn=lambda query, history: asyncio.run(process_text_query_ws(query, history)), 
                          inputs=[text_input, chat_history], outputs=[result_output, history_display])

        # Clear button functionality to reset inputs and history
        clear_button.click(fn=clear_fields, inputs=None, outputs=[audio_input, history_display])

    return ui

# Launch the Gradio app
if __name__ == "__main__":
    gradio_interface().launch(share=False)
