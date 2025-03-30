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
from schema import Usercreate,userinlogin
from sqlalchemy.orm  import session

@asynccontextmanager
async def lifespan(app : FastAPI):
    createtables()

    yield print('db is up now')




app = FastAPI(lifespan=lifespan)
app.include_router(router=authentification,tags=["auth"] , prefix="/auth")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)







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


