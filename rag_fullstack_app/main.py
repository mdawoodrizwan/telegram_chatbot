# # main.py

# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from rag_system import rag_chain

# # FastAPI app
# app = FastAPI()

# # Define request body model
# class QueryRequest(BaseModel):
#     query: str

# @app.post("/rag")
# async def rag_endpoint(request: QueryRequest):
#     try:
#         # Use the rag_chain function to process the query
#         result = rag_chain(request.query)
#         return {"response": result}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="An error occurred while processing the query")






# simple way
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from rag_system import rag_chain  # Ensure this points to the correct module

# # FastAPI app instance
# app = FastAPI()

# # Define request body model
# class QueryRequest(BaseModel):
#     query: str

# # Define the GET endpoint (for basic information or health check)
# @app.get("/")
# async def root():
#     return {"message": "Welcome to the RAG-based Query API. Use POST /rag to send a query."}

# # Define the POST endpoint for RAG-based query handling
# @app.post("/rag")
# async def rag_endpoint(request: QueryRequest):
#     try:
#         # Log the received query
#         print(f"Received query: {request.query}")

#         # Use the rag_chain function to process the query
#         result = rag_chain(request.query)

#         # Return the result in a structured response
#         return {"response": result}
    
#     except Exception as e:
#         # Log the error details
#         print(f"Error occurred: {str(e)}")

#         # Raise an HTTP 500 error with a friendly message
#         raise HTTPException(status_code=500, detail="An error occurred while processing the query. Please try again later.")










# websockets....

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from rag_system import rag_chain  # Ensure this points to the correct module

app = FastAPI()

# Define request body model (for non-WebSocket HTTP requests, if needed)
class QueryRequest(BaseModel):
    query: str

# WebSocket connection manager to track connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from the WebSocket
            data = await websocket.receive_text()
            print(f"Received message: {data}")

            # Process the query using RAG
            result = rag_chain(data)

            # Send the processed result back to the WebSocket client
            await manager.send_personal_message(result, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")

# The rest of the FastAPI code (optional HTTP-based endpoint)
@app.get("/")
async def root():
    return {"message": "Welcome to the RAG-based Query API. Use POST /rag or WebSocket /ws/chat to send a query."}

@app.post("/rag")
async def rag_endpoint(request: QueryRequest):
    try:
        # Log the received query
        print(f"Received query: {request.query}")

        # Use the rag_chain function to process the query
        result = rag_chain(request.query)

        # Return the result in a structured response
        return {"response": result}
    
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the query.")
