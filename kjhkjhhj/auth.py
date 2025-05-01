from fastapi import APIRouter, Depends, Body, BackgroundTasks, Header, HTTPException, status
from schema import Usercreate, userinlogin
from datetime import date
from database import get_db
from usermanagement import usermanagement  
from typing import Annotated, Union
from fastapi import UploadFile, File, HTTPException, Body, Header, Depends
from pydantic import EmailStr
from fastapi import Form
from fastapi import (
    APIRouter, Depends, Header, HTTPException, status,
    WebSocket, WebSocketDisconnect
)
from typing import Annotated, Union, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, distinct
import json
ADMIN_ID = 44
AUTH_PREFIX = "Bearer "
authentification = APIRouter()

@authentification.post("/login")
def login_user(userinlogin: userinlogin, session=Depends(get_db)):
    return usermanagement(session).log_in(userinlogin)

@authentification.post("/sign_up")
def sign_up_user_endpoint(Usercreate: Usercreate, background_tasks: BackgroundTasks, session=Depends(get_db)):
    return usermanagement(session).sign_up_user(Usercreate, background_tasks)

@authentification.post("/getname")
def get_user_name_endpoint(authorization: Annotated[Union[str, None], Header()] = None, session=Depends(get_db)):
    return usermanagement(session).get_user_name(authorization=authorization)

@authentification.post("/addappointement")
def add_appointement(Date: date = Body(..., embed=True),
                     authorization: Annotated[Union[str, None], Header()] = None,
                     session=Depends(get_db)):
    print("working")
    return usermanagement(session).book_Appointement(appointment_date=Date, authorization=authorization)

@authentification.post("/getappointement")
def get_appointement_endpoint(authorization: Annotated[Union[str, None], Header()] = None, session=Depends(get_db)):
    return usermanagement(session).get_Appointement(authorization=authorization)

@authentification.post("/SecretAdminlogin")
def admin_login(user: userinlogin, session=Depends(get_db)):
    return usermanagement(session).admin_log_in(user)

@authentification.post("/getaADMINppointement")
def get_admin_appointement_endpoint(authorization: Annotated[Union[str, None], Header()] = None, session=Depends(get_db)):
    return usermanagement(session).get_Appointement_admin(authorization=authorization)

@authentification.post("/SecretAdminsignup")
def admin_signup(user: userinlogin, session=Depends(get_db)):
    print("tesssssst")
    return usermanagement(session).sign_up_admin(user)

@authentification.post("/Updatestatue")
def update_status_endpoint(appointmentId: int = Body(...),
                           Date: date = Body(...),
                           statue: str = Body(...),
                           authorization: Annotated[Union[str, None], Header()] = None,
                           session=Depends(get_db)):
    return usermanagement(session).update_appointment(
        appointmentId=appointmentId,
        statue=statue,
        authorization=authorization,
        Date=Date
    )

@authentification.post("/getaadminpatiens")
def signup(authorization:Annotated[Union[str,None],Header()]=None, session = Depends(get_db)):
    
     return usermanagement(session).get_admin_app(authorization=authorization)
from fastapi import Request  

@authentification.post("/adminuploadtouser")
async def auth(
    request: Request,  
    email: EmailStr = Form(...),
    file: UploadFile = File(...),
    authorization: Annotated[Union[str, None], Header()] = None,
    session=Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        return {"error": "Invalid file type, only images are allowed!"}
    
    result = await usermanagement(session=session).chk_pic(
        request=request,  
        file=file,
        email=email,
        authorization=authorization
    )
    return result


@authentification.get("/searchmail")
def signup(email:str,authorization:Annotated[Union[str,None],Header()]=None, session = Depends(get_db)):
    
     return usermanagement(session).search_mail(email=email,authorization=authorization)



@authentification.post("/adminuploadtouser2")
async def auth(
    request: Request,  
    email: EmailStr = Form(...),
    file: UploadFile = File(...),
    authorization: Annotated[Union[str, None], Header()] = None,
    session=Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        return {"error": "Invalid file type, only images are allowed!"}
    
    result = await usermanagement(session=session).chk_pic2(
        request=request,  
        file=file,
        email=email,
        authorization=authorization
    )
    return result


@authentification.post("/adminuploadtouser3")
async def auth(
    request: Request,  
    email: EmailStr = Form(...),
    file: UploadFile = File(...),
    authorization: Annotated[Union[str, None], Header()] = None,
    session=Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        return {"error": "Invalid file type, only images are allowed!"}
    
    result = await usermanagement(session=session).chk_pic3(
        request=request,  
        file=file,
        email=email,
        authorization=authorization
    )
    return result

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    authorization: Union[str, None] = Header(None),
    session: Session = Depends(get_db),
):
    # 1) Auth
    auth_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
    )
    if not authorization or not authorization.startswith(AUTH_PREFIX):
        raise auth_exception

    token = authorization[len(AUTH_PREFIX):]
    payload = chk_token(token=token)
    if not payload or "user_id" not in payload:
        raise auth_exception

    my_id = payload["user_id"]
    other_id = ADMIN_ID  # The admin ID is hardcoded here

    await websocket.accept()
    active_connections[my_id] = websocket

    try:
        # Send chat history to the user
        messages = session.query(ChatMessage).filter(
            or_(
                and_(ChatMessage.from_id == my_id, ChatMessage.to_id == other_id),
                and_(ChatMessage.from_id == other_id, ChatMessage.to_id == my_id)
            )
        ).order_by(ChatMessage.timestamp.asc()).all()

        history_payload = [{
            "from_id": msg.from_id,
            "message": msg.message,
            "timestamp": msg.timestamp.isoformat()
        } for msg in messages]

        await send_to_websocket(websocket, {"type": "history", "messages": history_payload})

        # Notify admin that the user is connected
        await notify_admin({"type": "user_connected", "user_id": my_id})

        # Handle incoming messages
        while True:
            data_string = await websocket.receive_text()
            data = json.loads(data_string)

            message_text = data.get("message", "").strip()
            if message_text:
                new_msg = ChatMessage(from_id=my_id, to_id=other_id, message=message_text)
                session.add(new_msg)
                session.commit()
                session.refresh(new_msg)

                # Notify admin of the message
                if other_id in active_connections:
                    await send_to_websocket(active_connections[other_id], {
                        "from_id": my_id,
                        "message": message_text,
                        "timestamp": new_msg.timestamp.isoformat()
                    })

    except WebSocketDisconnect:
        pass

    finally:
        # Cleanup on disconnect
        active_connections.pop(my_id, None)
        await notify_admin({"type": "user_disconnected", "user_id": my_id})




