from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import numpy as np
import torch
import torch.nn as nn
import joblib
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictionRequest(BaseModel):
    data: List[float]

class PredictionResponse(BaseModel):
    prediction: float
    confidence: float

class TrainingRequest(BaseModel):
    data: List[List[float]]
    labels: List[float]
    epochs: Optional[int] = 10

class SimpleNN(nn.Module):
    def __init__(self, input_size=10):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(input_size, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 1)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return x

model = None
MODEL_PATH = Path("models")
MODEL_PATH.mkdir(exist_ok=True)

def load_or_create_model(input_size=10):
    global model
    model_file = MODEL_PATH / "model.pth"
    
    model = SimpleNN(input_size)
    
    if model_file.exists():
        try:
            model.load_state_dict(torch.load(model_file))
            logger.info("Model loaded from disk")
        except:
            logger.warning("Failed to load model, using new model")
    else:
        logger.info("No saved model found, using new model")
    
    model.eval()
    return model

@app.on_event("startup")
async def startup_event():
    global model
    model = load_or_create_model()
    logger.info("AI Model service started on port 8001")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "ai-model"}

@app.post("/api/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    try:
        if model is None:
            raise HTTPException(status_code=500, detail="Model not loaded")
        
        input_data = torch.FloatTensor(request.data).unsqueeze(0)
        
        while input_data.shape[1] < 10:
            input_data = torch.cat([input_data, torch.zeros(1, 1)], dim=1)
        
        if input_data.shape[1] > 10:
            input_data = input_data[:, :10]
        
        with torch.no_grad():
            prediction = model(input_data).item()
        
        confidence = min(0.95, max(0.5, 1.0 - abs(prediction) * 0.1))
        
        return PredictionResponse(
            prediction=float(prediction),
            confidence=float(confidence)
        )
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/train")
async def train_model(request: TrainingRequest):
    try:
        global model
        
        if not request.data or not request.labels:
            raise HTTPException(status_code=400, detail="Training data and labels required")
        
        if len(request.data) != len(request.labels):
            raise HTTPException(status_code=400, detail="Data and labels must have same length")
        
        X = torch.FloatTensor(request.data)
        y = torch.FloatTensor(request.labels).unsqueeze(1)
        
        input_size = X.shape[1]
        model = SimpleNN(input_size)
        
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        
        model.train()
        losses = []
        
        for epoch in range(request.epochs):
            optimizer.zero_grad()
            outputs = model(X)
            loss = criterion(outputs, y)
            loss.backward()
            optimizer.step()
            losses.append(loss.item())
            
            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch}/{request.epochs}, Loss: {loss.item():.4f}")
        
        model_file = MODEL_PATH / "model.pth"
        torch.save(model.state_dict(), model_file)
        logger.info(f"Model saved to {model_file}")
        
        model.eval()
        
        return {
            "status": "success",
            "message": f"Model trained for {request.epochs} epochs",
            "final_loss": losses[-1] if losses else 0
        }
        
    except Exception as e:
        logger.error(f"Training error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/model/info")
async def model_info():
    if model is None:
        return {"status": "no model loaded"}
    
    param_count = sum(p.numel() for p in model.parameters())
    
    return {
        "status": "model loaded",
        "type": "Simple Neural Network",
        "parameters": param_count,
        "layers": 3,
        "architecture": {
            "input": "variable",
            "hidden1": 64,
            "hidden2": 32,
            "output": 1
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)