from fastapi import APIRouter, Depends, Body, BackgroundTasks, Header, HTTPException, status
from schema import Usercreate, userinlogin
from datetime import date
from database import get_db
from usermanagement import usermanagement  # Adjust import as needed
from typing import Annotated, Union
from fastapi import UploadFile, File, HTTPException, Body, Header, Depends
from pydantic import EmailStr
from fastapi import Form
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
@authentification.post("/adminuploadtouser")
async def auth(email:EmailStr = Form(...),file: UploadFile = File(...),authorization:Annotated[Union[str,None],Header()]=None,session=Depends(get_db) ):
       if not file.content_type.startswith("image/"):
         return {"error": "Invalid file type, only images are allowed!"}
       usermanagement(session=session).chk_pic(file=file,email=email,authentification=authentification)






