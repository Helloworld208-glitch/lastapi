from fastapi import APIRouter, Depends, Body, BackgroundTasks, Header, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from schema import Usercreate, userinlogin
from datetime import date
from database import get_db
from usermanagement import usermanagement  
from typing import Annotated, Union, Dict
from fastapi import UploadFile, File, Form, Request
from pydantic import EmailStr
from security.jwt import chk_token
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
import json
from user import ChatMessage

ADMIN_ID = 44
AUTH_PREFIX = "Bearer "
authentification = APIRouter()
# سجّل اتصالات الـ WebSocket للمستخدمين والأدمن
active_connections: Dict[int, WebSocket] = {}

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

# رفع صور للمستخدم من قبل الأدمن
@authentification.post("/adminuploadtouser")
async def admin_upload(
    request: Request,
    email: EmailStr = Form(...),
    file: UploadFile = File(...),
    authorization: Annotated[Union[str, None], Header()] = None,
    session=Depends(get_db)
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

@authentification.post("/adminuploadtouser2")
async def admin_upload2(
    request: Request,
    email: EmailStr = Form(...),
    file: UploadFile = File(...),
    authorization: Annotated[Union[str, None], Header()] = None,
    session=Depends(get_db)
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
    session=Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type")
    return await usermanagement(session).chk_pic3(request, file, email, authorization)

# نقطة نهاية WebSocket للمستخدمين
@authentification.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    authorization: Annotated[Union[str, None], Query()] = None,
    session: Session = Depends(get_db),
):
    # مصادقة
    if not authorization or not authorization.startswith(AUTH_PREFIX):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    token = authorization[len(AUTH_PREFIX):]
    payload = chk_token(token)
    if not payload or "user_id" not in payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    my_id = payload["user_id"]
    other_id = ADMIN_ID

    await websocket.accept()
    active_connections[my_id] = websocket

    try:
        # إرسال التاريخ
        msgs = (
            session.query(ChatMessage)
            .filter(
                or_(
                    and_(ChatMessage.from_id == my_id, ChatMessage.to_id == other_id),
                    and_(ChatMessage.from_id == other_id, ChatMessage.to_id == my_id)
                )
            )
            .order_by(ChatMessage.timestamp.asc())
            .all()
        )
        history = [{"from_id": m.from_id, "message": m.message, "timestamp": m.timestamp.isoformat()} for m in msgs]
        await websocket.send_json({"type": "history", "messages": history})

        while True:
            data = await websocket.receive_text()
            obj = json.loads(data)
            text = obj.get("message", "").strip()
            if text:
                new_msg = ChatMessage(from_id=my_id, to_id=other_id, message=text)
                session.add(new_msg)
                session.commit()
                session.refresh(new_msg)
                # إرسال للأدمن
                if other_id in active_connections:
                    await active_connections[other_id].send_json({
                        "from_id": my_id,
                        "message": text,
                        "timestamp": new_msg.timestamp.isoformat()
                    })
    except WebSocketDisconnect:
        pass
    finally:
        active_connections.pop(my_id, None)




