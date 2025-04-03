from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import gdown
import tensorflow as tf
import os
from pathlib import Path  # Absolute path handling [[9]]
from auth import authentification  # Your auth routes

MODEL_FILE_ID = "14UIKtvFJ9LaprvAyUp-qKzrhrTzbn2_R"  # Verified working ID [[1]]
MODEL_PATH = Path(__file__).parent.resolve() / "lasttry_model_new.h5"  # Absolute path [[9]]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Database init (from your original code)
    from init_db import createtables
    createtables()
    
    try:
        # Model download with validation [[1]][[9]]
        if not MODEL_PATH.exists():
            print(f"Downloading model to {MODEL_PATH}...")
            url = f"https://drive.google.com/uc?id={MODEL_FILE_ID}"
            gdown.download(url, str(MODEL_PATH), quiet=False)
            
        # File integrity check [[1]]
        if MODEL_PATH.stat().st_size < 1024:
            raise OSError("Downloaded model file is corrupt")
            
        app.state.model = tf.keras.models.load_model(MODEL_PATH)
        print(f"Model loaded from: {MODEL_PATH}")
        
    except Exception as e:
        print(f"Startup failed: {str(e)}")
        print(f"Attempted path: {MODEL_PATH}")
        print("Verify:")
        print("1. Google Drive file is shared publicly")
        print("2. Network connectivity")
        raise
    
    yield

app = FastAPI(lifespan=lifespan)

# CORS configuration [[4]]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth routes
app.include_router(authentification, prefix="/auth", tags=["auth"])

# Templates [[3]]
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
    print(f"Starting server on port {port}...")  # Port verification [[5]]
    uvicorn.run(app, host="0.0.0.0", port=port)


