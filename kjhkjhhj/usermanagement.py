from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager
from init_db import createtables
from auth import authentification
from database import get_db
from schema import Usercreate, userinlogin
from sqlalchemy.orm import session
import gdown
import tensorflow as tf

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    createtables()
    
    # Download and load model
    file_id = "1-B3xH3-3xvC06WDfZdlpwvd3frUbVDBg"
    url = f"https://drive.google.com/uc?id={file_id}"
    output = "lasttry_model_new.h5"
    gdown.download(url, output, quiet=False)
    model = tf.keras.models.load_model(output)
    app.state.model = model  # Store model in app state
    print("Model loaded successfully.")
    
    yield  # This line was corrected
    
    # Shutdown code (if needed)
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)
app.include_router(router=authentification, tags=["auth"], prefix="/auth")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Removed the @app.on_event("startup") decorator and load_model function

class_names = ['Normal', 'sick']
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post('/data/{text}')
def do(text: str):
    return f"{text} ,your code is delivered to backend and treated"

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)



