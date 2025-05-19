from fastapi import APIRouter, Depends, Body, BackgroundTasks, Header, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from schema import Usercreate, userinlogin
from datetime import date
from database import get_db
from usermanagement import usermanagement  
from typing import Annotated, Union, Dict, List
from fastapi import UploadFile, File, Form, Request
from pydantic import EmailStr
from security.jwt import jwtclass
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, distinct
import json
from user import ChatMessage


ADMIN_ID = 44
AUTH_PREFIX = "Bearer "
authentification = APIRouter()
active_connections: Dict[int, WebSocket] = {}

# Existing endpoints
@authentification.post("/login")
def login_user(userinlogin: userinlogin, session=Depends(get_db)):
    return usermanagement(session).log_in(userinlogin)

@authentification.post("/sign_up")
def sign_up_user_endpoint(Usercreate: Usercreate, background_tasks: BackgroundTasks, session=Depends(get_db)):
    return usermanagement(session).sign_up_user(Usercreate, background_tasks)

@authentification.post("/getname")
def get_user_name_endpoint(authorization: Annotated[Union[str, None], Header()] = None, session=Depends(get_db)):
    return usermanagement(session).get_user_name(authorization=authorization)
@authentification.post("/getemail")
def get_user_name_endpoint(authorization: Annotated[Union[str, None], Header()] = None, session=Depends(get_db)):
    return usermanagement(session).get_user_email_by_id(authorization=authorization)
@authentification.post("/addappointement")
def add_appointement(
    Date: date = Body(..., embed=True),
    authorization: Annotated[Union[str, None], Header()] = None,
    session=Depends(get_db)
):
    return usermanagement(session).book_Appointement(appointment_date=Date, authorization=authorization)

@authentification.post("/getappointement")
def get_appointement_endpoint(
    authorization: Annotated[Union[str, None], Header()] = None,
    session=Depends(get_db)
):
    return usermanagement(session).get_Appointement(authorization=authorization)

@authentification.post("/SecretAdminlogin")
def admin_login(user: userinlogin, session=Depends(get_db)):
    return usermanagement(session).admin_log_in(user)

@authentification.post("/getaADMINppointement")
def get_admin_appointement_endpoint(
    authorization: Annotated[Union[str, None], Header()] = None,
    session=Depends(get_db)
):
    return usermanagement(session).get_Appointement_admin(authorization=authorization)

@authentification.post("/SecretAdminsignup")
def admin_signup(user: userinlogin, session=Depends(get_db)):
    return usermanagement(session).sign_up_admin(user)

@authentification.post("/Updatestatue")
def update_status_endpoint(
    appointmentId: int = Body(...),
    Date: date = Body(...),
    statue: str = Body(...),
    authorization: Annotated[Union[str, None], Header()] = None,
    session=Depends(get_db)
):
    return usermanagement(session).update_appointment(
        appointmentId=appointmentId,
        statue=statue,
        authorization=authorization,
        Date=Date
    )

@authentification.post("/getaadminpatiens")
def get_admin_patients(
    authorization: Annotated[Union[str, None], Header()] = None,
    session=Depends(get_db)
):
    return usermanagement(session).get_admin_app(authorization=authorization)

@authentification.post("/chkuserpremium")
def get_admin_patients(
    authorization: Annotated[Union[str, None], Header()] = None,
    session=Depends(get_db)
):
    return usermanagement(session).chk_premium(authorization=authorization)
@authentification.post("/addusertopremium")
def get_admin_patients(
    authorization: Annotated[Union[str, None], Header()] = None,
    session=Depends(get_db)
):
    return usermanagement(session).add_premium(authorization=authorization)
@authentification.post("/adminuploadtouser")
async def admin_upload(
    request: Request,
    email: EmailStr = Form(...),
    file: UploadFile = File(...),
    authorization: Annotated[Union[str, None], Header()] = None,
    session: Session = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type")
    return await usermanagement(session).chk_pic(request, file, email, authorization)

@authentification.get("/searchmail")
def search_mail(
    email: str,
    authorization: Annotated[Union[str, None], Header()] = None,
    session=Depends(get_db)
):
    return usermanagement(session).search_mail(email=email, authorization=authorization)

# Fixed adminuploadtouser2 endpoint
@authentification.post("/adminuploadtouser2")
async def admin_upload2(
    request: Request,
    email: EmailStr = Form(...),
    file: UploadFile = File(...),
    authorization: Annotated[Union[str, None], Header()] = None,
    session: Session = Depends(get_db)  # Fixed line
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type")
    return await usermanagement(session).chk_pic2(request, file, email, authorization)

@authentification.post("/adminuploadtouser3")
async def admin_upload3(
    request: Request,
    email: EmailStr = Form(...),
    file: UploadFile = File(...),
    authorization: Annotated[Union[str, None], Header()] = None,
    session: Session = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type")
    return await usermanagement(session).chk_pic3(request, file, email, authorization)

# WebSocket endpoints
@authentification.websocket("/ws")
async def user_websocket(
    websocket: WebSocket,
    authorization: Annotated[Union[str, None], Query()] = None,
    session: Session = Depends(get_db),
):
    if not authorization or not authorization.startswith(AUTH_PREFIX):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    token = authorization[len(AUTH_PREFIX):]
    payload = jwtclass.chk_token(token)
    
    if not payload or "user_id" not in payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = payload["user_id"]
    await websocket.accept()
    active_connections[user_id] = websocket

    if ADMIN_ID in active_connections:
        await active_connections[ADMIN_ID].send_json({
            "type": "user_connected",
            "user_id": user_id
        })

    try:
        msgs = (
            session.query(ChatMessage)
            .filter(
                or_(
                    and_(ChatMessage.from_id == user_id, ChatMessage.to_id == ADMIN_ID),
                    and_(ChatMessage.from_id == ADMIN_ID, ChatMessage.to_id == user_id)
                )
            )
            .order_by(ChatMessage.timestamp.asc())
            .all()
        )
        history = [{
            "from_id": m.from_id,
            "message": m.message,
            "timestamp": m.timestamp.isoformat()
        } for m in msgs]
        await websocket.send_json({"type": "history", "messages": history})

        while True:
            data = await websocket.receive_text()
            message = json.loads(data).get("message", "").strip()
            
            if message:
                new_msg = ChatMessage(
                    from_id=user_id,
                    to_id=ADMIN_ID,
                    message=message
                )
                session.add(new_msg)
                session.commit()
                
                if ADMIN_ID in active_connections:
                    await active_connections[ADMIN_ID].send_json({
                        "from_id": user_id,
                        "message": message,
                        "timestamp": new_msg.timestamp.isoformat()
                    })

    except WebSocketDisconnect:
        pass
    finally:
        active_connections.pop(user_id, None)
        if ADMIN_ID in active_connections:
            await active_connections[ADMIN_ID].send_json({
                "type": "user_disconnected",
                "user_id": user_id
            })

@authentification.websocket("/admin_ws")
async def admin_websocket(
    websocket: WebSocket,
    authorization: Annotated[Union[str, None], Query()] = None,
    session: Session = Depends(get_db),
):
    if not authorization or not authorization.startswith(AUTH_PREFIX):
        await websocket.close()
        return
    
    token = authorization[len(AUTH_PREFIX):]
    payload = jwtclass.chk_token(token)
    
    if not payload or payload.get('user_id') != ADMIN_ID or payload.get('role') != 'admin':
        await websocket.close()
        return

    await websocket.accept()
    active_connections[ADMIN_ID] = websocket

    try:
        users = [uid for uid in active_connections if uid != ADMIN_ID]
        await websocket.send_json({"type": "user_list", "users": users})

        while True:
            data = await websocket.receive_text()
            msg_data = json.loads(data)
            
            target_user = msg_data.get("user_id")
            message = msg_data.get("message", "").strip()
            
            if target_user and message:
                new_msg = ChatMessage(
                    from_id=ADMIN_ID,
                    to_id=target_user,
                    message=message
                )
                session.add(new_msg)
                session.commit()
                
                if target_user in active_connections:
                    await active_connections[target_user].send_json({
                        "from_id": ADMIN_ID,
                        "message": message,
                        "timestamp": new_msg.timestamp.isoformat()
                    })

    except WebSocketDisconnect:
        pass
    finally:
        active_connections.pop(ADMIN_ID, None)

# New endpoint for chat users
@authentification.post("/adminuploadtouser22")
async def admin_upload2(
    request: Request,
    email: EmailStr = Form(...),
    file: UploadFile = File(...),
    authorization: Annotated[Union[str, None], Header()] = None,
    session: Session = Depends(get_db)  # Fixed line
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type")
    return await usermanagement(session).chk_pic22(request, file, email, authorization)
@authentification.get("/chat-users", response_model=List[int])
def get_chat_users(
    authorization: Annotated[Union[str, None], Header()] = None,
    session: Session = Depends(get_db)
):
    if not authorization or not authorization.startswith(AUTH_PREFIX):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    token = authorization[len(AUTH_PREFIX):]
    payload = jwtclass.chk_token(token)
    
    if not payload or payload.get('user_id') != ADMIN_ID or payload.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    from_users = session.query(distinct(ChatMessage.from_id))\
                        .filter(ChatMessage.to_id == ADMIN_ID)\
                        .all()
    to_users   = session.query(distinct(ChatMessage.to_id))\
                        .filter(ChatMessage.from_id == ADMIN_ID)\
                        .all()

    all_users = {uid for (uid,) in from_users + to_users if uid != ADMIN_ID}
    return list(all_users)

    # Add this endpoint after the /chat-users endpoint
@authentification.get("/chat-history/{user_id}")
def get_chat_history(
    user_id: int,
    authorization: Annotated[Union[str, None], Header()] = None,
    session: Session = Depends(get_db)
):
    # Authentication check
    if not authorization or not authorization.startswith(AUTH_PREFIX):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    token = authorization[len(AUTH_PREFIX):]
    payload = jwtclass.chk_token(token)
    
    if not payload or payload.get('user_id') != ADMIN_ID or payload.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    # Get chat history between admin and selected user
    messages = session.query(ChatMessage).filter(
        or_(
            and_(ChatMessage.from_id == user_id, ChatMessage.to_id == ADMIN_ID),
            and_(ChatMessage.from_id == ADMIN_ID, ChatMessage.to_id == user_id)
        )
    ).order_by(ChatMessage.timestamp.asc()).all()

    return [{
        "from_id": msg.from_id,
        "message": msg.message,
        "timestamp": msg.timestamp.isoformat()
    } for msg in messages]
    
    return list(all_users)
