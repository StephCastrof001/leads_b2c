import os
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model configuration
MODEL_NAME = "gemini-1.5-flash"

# Pydantic models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9

class ChatResponse(BaseModel):
    response: str
    model: str

class CompletionRequest(BaseModel):
    prompt: str
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9

class CompletionResponse(BaseModel):
    completion: str
    model: str

# Initialize client
def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not found in environment")
    
    client = genai.Client(api_key=api_key)
    return client

# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    client = get_client()
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=request.messages,
            config=types.GenerateContentConfig(
                temperature=request.temperature,
                top_p=request.top_p,
            )
        )
        
        if response.text:
            return ChatResponse(response=response.text, model=MODEL_NAME)
        else:
            raise HTTPException(status_code=500, detail="Empty response from model")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Completion endpoint
@app.post("/complete", response_model=CompletionResponse)
async def complete(request: CompletionRequest):
    client = get_client()
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=request.prompt,
            config=types.GenerateContentConfig(
                temperature=request.temperature,
                top_p=request.top_p,
            )
        )
        
        if response.text:
            return CompletionResponse(completion=response.text, model=MODEL_NAME)
        else:
            raise HTTPException(status_code=500, detail="Empty response from model")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": MODEL_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
