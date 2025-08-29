from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx
import json

app = FastAPI()

OLLAMA_BASE_URL = "http://localhost:11434"

class OllamaRequest(BaseModel):
    prompt: str
    model: str = "llama3.2"
    system: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None

class OllamaEmbeddingRequest(BaseModel):
    text: str
    model: str = "nomic-embed-text"

class HybridRequest(BaseModel):
    text: str
    numerical_features: List[float]
    task: str = "classify"

async def query_ollama(prompt: str, model: str = "llama3.2", system: str = None) -> str:
    """Query Ollama for text generation"""
    async with httpx.AsyncClient() as client:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()["message"]["content"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")

async def get_embeddings(text: str, model: str = "nomic-embed-text") -> List[float]:
    """Get embeddings from Ollama"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/embeddings",
                json={
                    "model": model,
                    "prompt": text
                },
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Embedding error: {str(e)}")

@app.post("/api/ollama/generate")
async def generate_text(request: OllamaRequest):
    """Generate text using Ollama LLM"""
    result = await query_ollama(
        prompt=request.prompt,
        model=request.model,
        system=request.system
    )
    return {"response": result, "model": request.model}

@app.post("/api/ollama/analyze")
async def analyze_data(data: Dict[Any, Any]):
    """Use LLM to analyze structured data"""
    prompt = f"""Analyze this data and provide insights:
    {json.dumps(data, indent=2)}
    
    Provide:
    1. Key patterns
    2. Anomalies
    3. Recommendations
    """
    
    result = await query_ollama(prompt, model="llama3.2")
    return {"analysis": result}

@app.post("/api/hybrid/predict")
async def hybrid_prediction(request: HybridRequest):
    """Combine LLM understanding with numerical predictions"""
    
    # Get text embeddings from Ollama
    embeddings = await get_embeddings(request.text)
    
    # Combine with numerical features
    combined_features = embeddings[:50] + request.numerical_features  # Truncate embeddings
    
    # Here you would use your PyTorch model with combined features
    # For demo, returning mock result
    prediction = sum(combined_features) / len(combined_features)
    
    # Get LLM interpretation
    interpretation = await query_ollama(
        f"Explain this prediction: {prediction} for text: {request.text}",
        model="llama3.2"
    )
    
    return {
        "prediction": prediction,
        "interpretation": interpretation,
        "confidence": 0.85
    }

@app.post("/api/ollama/code-review")
async def review_code(code: str):
    """Use LLM for code review"""
    prompt = f"""Review this code for:
    1. Bugs
    2. Security issues  
    3. Performance improvements
    4. Best practices
    
    Code:
    ```
    {code}
    ```
    """
    
    result = await query_ollama(prompt, model="qwen2.5-coder")
    return {"review": result}

@app.get("/api/ollama/models")
async def list_models():
    """List available Ollama models"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            response.raise_for_status()
            models = response.json()["models"]
            return {
                "models": [m["name"] for m in models],
                "count": len(models)
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Cannot connect to Ollama: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)