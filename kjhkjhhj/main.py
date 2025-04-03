from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastAPI.responses import HTMLResponse
from fastAPI.middleware.cors import CORSMiddleware
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
    createtables()
    yield print('db is up now')

app = FastAPI(lifespan=lifespan)
app.include_router(router=authentification, tags=["auth"], prefix="/auth")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.on_event("startup")
async def load_model():
    # Step 1: Download the pre-trained model from Google Drive
    file_id = "1-B3xH3-3xvC06WDfZdlpwvd3frUbVDBg"  # Correct file ID from your link
    url = f"https://drive.google.com/uc?id={file_id}"
    output = "lasttry_model_new.h5"
    gdown.download(url, output, quiet=False)

    # Step 2: Load the model using TensorFlow
    global model
    model = tf.keras.models.load_model(output)
    print("Model loaded successfully.")

# Define class names (from your training output)
class_names = ['Normal', 'sick']  # Verify with your training data
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post('/data/{text}')
def do(text: str):
    return f"{text} ,your code is delivered to backend and treated"

import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
