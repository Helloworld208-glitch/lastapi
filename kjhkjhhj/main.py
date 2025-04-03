from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from init_db import createtables
from auth import authentification
import gdown
import tensorflow as tf

# Consolidated lifespan with model loading [[3]][[8]]
@asynccontextmanager
async def lifespan(app: FastAPI):
    createtables()  # Database init
    
    # Model loading with error handling [[1]][[9]]
    try:
        file_id = "1-B3xH3-3xvC06WDfZdlpwvd3frUbVDBg"
        url = f"https://drive.google.com/uc?id={file_id}"
        output = "lasttry_model_new.h5"
        gdown.download(url, output, quiet=False)
        app.state.model = tf.keras.models.load_model(output)
        print("Model loaded successfully")
    except Exception as e:
        print(f"Model loading failed: {str(e)}")
        raise
    
    yield  # Transition to app runtime

app = FastAPI(lifespan=lifespan)

# Add CORS middleware first [[10]]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router after middleware [[6]]
app.include_router(authentification, tags=["auth"], prefix="/auth")

# Template setup [[2]]
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Optional health check endpoint [[5]]
@app.get("/health")
async def health_check():
    if not hasattr(app.state, "model"):
        raise HTTPException(status_code=503, detail="Model not ready")
    return {"status": "Model loaded"}

# Your existing /data endpoint remains unchanged
@app.post('/data/{text}')
def do(text: str):
    return f"{text} ,your code is delivered to backend and treated"

import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


