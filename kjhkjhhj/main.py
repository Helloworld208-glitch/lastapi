from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import gdown
import tensorflow as tf
import os
from auth import authentification  # Assuming your auth routes are here

# Model configuration [[6]][[9]]
MODEL_FILE_ID = "14UIKtvFJ9LaprvAyUp-qKzrhrTzbn2_R"  # From your working Colab code
MODEL_PATH = "lasttry_model_new.h5"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Database initialization (from your original code)
    from init_db import createtables
    createtables()
    
    # Model loading with validation [[1]][[6]]
    try:
        if not os.path.exists(MODEL_PATH):
            print("Downloading model...")
            url = f"https://drive.google.com/uc?id={MODEL_FILE_ID}"
            gdown.download(url, MODEL_PATH, quiet=False)
            
        # File integrity check [[1]]
        if os.path.getsize(MODEL_PATH) < 1024:
            raise OSError("Model file appears corrupt")
            
        app.state.model = tf.keras.models.load_model(MODEL_PATH)
        print("Model loaded successfully")
        
    except Exception as e:
        print(f"Startup failed: {str(e)}")
        print("1. Verify Google Drive file is shared publicly")
        print("2. Check network connectivity")
        raise
    
    yield

app = FastAPI(lifespan=lifespan)

# CORS configuration [[7]]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(authentification, prefix="/auth", tags=["auth"])

# Template setup [[2]]
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
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))


