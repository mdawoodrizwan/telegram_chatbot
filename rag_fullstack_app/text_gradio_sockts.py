# import gradio as gr
# import time
# import requests

# # URL of your FastAPI endpoint
# FASTAPI_URL = "http://localhost:8000/rag"  # Corrected to match the FastAPI endpoint

# # Custom CSS for Gradio interface
# custom_css = """
# #chatbot {
#     height: 600px;
#     overflow-y: auto;
#     padding: 20px;
#     border-radius: 10px;
#     background-color: #1f2937;
#     color: white;
#     box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
# }
# #chatbot .user {
#     background-color: #2b313e;
#     padding: 15px;
#     border-radius: 15px 15px 2px 15px;
#     margin-bottom: 10px;
#     box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
#     color: #ffffff;
# }
# #chatbot .bot {
#     background-color: #3f4b5e;
#     padding: 15px;
#     border-radius: 2px 15px 15px 15px;
#     margin-bottom: 10px;
#     box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
#     color: #ffffff;
# }
# #header {
#     text-align: center;
#     font-size: 24px;
#     font-weight: bold;
#     color: #ffffff;
#     background-color: #111827;
#     padding: 15px;
#     border-radius: 8px;
#     margin-bottom: 10px;
# }
# """

# # Function to get response from FastAPI
# def get_rag_response(query):
#     try:
#         response = requests.post(FASTAPI_URL, json={"query": query})
#         response.raise_for_status()  # Check for HTTP errors
#         return response.json().get("response", "No response from RAG system")
#     except Exception as e:
#         return f"Error: {str(e)}"

# # Simulated typing effect for bot responses
# def simulate_typing(response: str, delay: float = 0.05):
#     """Simulate typing effect by yielding one character at a time with delay."""
#     result = ""
#     for char in response:
#         result += char
#         time.sleep(delay)
#         yield result

# # Function to handle chat interaction dynamically
# def chat(message: str, history):
#     """Handles user input, calls FastAPI RAG system, and appends to chat history."""
#     # Get RAG response from FastAPI
#     response = get_rag_response(message)
    
#     # Simulate the typing effect
#     for partial_response in simulate_typing(response):
#         yield history + [(message, partial_response)], ""

# # Gradio interface definition
# with gr.Blocks(css=custom_css) as demo:
#     # Header
#     gr.Markdown("<div id='header'>🔍 RAG System Chat Interface</div>")
    
#     # Chatbot display
#     chatbot = gr.Chatbot(elem_id="chatbot")
    
#     # User input box
#     msg = gr.Textbox(placeholder="Type your message here...", label="User Input", lines=1)
    
#     # Button to clear the chat
#     clear = gr.Button("Clear")

#     # Dynamic interaction with chat function
#     msg.submit(chat, [msg, chatbot], [chatbot, msg])
    
#     # Clear chat when button is clicked
#     clear.click(lambda: None, None, chatbot, queue=False)

# # Launch the Gradio interface
# if __name__ == "__main__":
#     demo.launch()















import gradio as gr
import time
import asyncio
import websockets

# WebSocket URL for FastAPI
WS_URL = "ws://localhost:8000/ws/chat"

# Custom CSS for Gradio interface
custom_css = """
#chatbot {
    height: 600px;
    overflow-y: auto;
    padding: 20px;
    border-radius: 10px;
    background-color: #1f2937;
    color: white;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}
#chatbot .user {
    background-color: #2b313e;
    padding: 15px;
    border-radius: 15px 15px 2px 15px;
    margin-bottom: 10px;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    color: #ffffff;
}
#chatbot .bot {
    background-color: #3f4b5e;
    padding: 15px;
    border-radius: 2px 15px 15px 15px;
    margin-bottom: 10px;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    color: #ffffff;
}
#header {
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    color: #ffffff;
    background-color: #111827;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 10px;
}
"""

# Function to communicate with WebSocket
async def websocket_chat(query):
    async with websockets.connect(WS_URL) as websocket:
        # Send user query via WebSocket
        await websocket.send(query)
        
        # Receive the bot's response
        response = await websocket.recv()
        
        return response

# Simulated typing effect for bot responses
def simulate_typing(response: str, delay: float = 0.005):
    """Simulate typing effect by yielding one character at a time with delay."""
    result = ""
    for char in response:
        result += char
        time.sleep(delay)
        yield result

# Function to handle chat interaction dynamically with WebSocket
async def chat(message: str, history):
    """Handles user input, calls WebSocket RAG system, and appends to chat history."""
    response = await websocket_chat(message)
    
    # Simulate the typing effect
    simulated_response = ""
    for partial_response in simulate_typing(response):
        simulated_response = partial_response
        await asyncio.sleep(0.005)
        yield history + [(message, simulated_response)], ""

# Gradio interface definition
with gr.Blocks(css=custom_css) as demo:
    # Header
    gr.Markdown("<div id='header'>🔍 RAG System Chat Interface</div>")
    
    # Chatbot display
    chatbot = gr.Chatbot(elem_id="chatbot")
    
    # User input box
    msg = gr.Textbox(placeholder="Type your message here...", label="User Input", lines=1)
    
    # Button to clear the chat
    clear = gr.Button("Clear")

    # Dynamic interaction with chat function using WebSockets
    msg.submit(chat, [msg, chatbot], [chatbot, msg])
    
    # Clear chat when button is clicked
    clear.click(lambda: None, None, chatbot, queue=False)

# Launch the Gradio interface
if __name__ == "__main__":
    demo.launch()




