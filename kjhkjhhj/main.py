import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager

import gdown
import tensorflow as tf
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from auth import authentification  # Your auth routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the Google Drive file ID (verified working) and local model path
MODEL_FILE_ID = "14UIKtvFJ9LaprvAyUp-qKzrhrTzbn2_R"
MODEL_PATH = Path(__file__).parent.resolve() / "lasttry_model_new.h5"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database tables
    from init_db import createtables
    createtables()
    
    try:
        # If the model file does not exist, download it
        if not MODEL_PATH.exists():
            logger.info("Downloading model to %s...", MODEL_PATH)
            url = f"https://drive.google.com/uc?id={MODEL_FILE_ID}"
            gdown.download(url, str(MODEL_PATH), quiet=False)
            
        # Validate the downloaded file (basic integrity check)
        if MODEL_PATH.stat().st_size < 1024:
            raise OSError("Downloaded model file is corrupt or too small.")
        
        # Load the model into application state
        app.state.model = tf.keras.models.load_model(str(MODEL_PATH))
        logger.info("Model loaded from: %s", MODEL_PATH)
        
    except Exception as e:
        logger.error("Startup failed: %s", str(e))
        logger.error("Attempted path: %s", MODEL_PATH)
        logger.error("Verify:\n1. Google Drive file is shared publicly\n2. Network connectivity")
        raise
    
    yield

# Create FastAPI instance with lifespan management
app = FastAPI(lifespan=lifespan)

# Set up CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth routes
app.include_router(authentification, prefix="/auth", tags=["auth"])

# Set up Jinja2 templates directory
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    if not hasattr(app.state, "model"):
        raise HTTPException(503, "Model not loaded")
    return {"status": "Model ready"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info("Starting server on port %s...", port)
    uvicorn.run(app, host="0.0.0.0", port=port)

