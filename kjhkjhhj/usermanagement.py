from useradd import Adduser
from schema import Usercreate, userinlogin
from security.codingdata import encrypt
from security.jwt import jwtclass
from fastapi import HTTPException, Header, status, File, UploadFile, Body
from user import Userr, Appointment, Admin, UserPremium
from database import get_db
from pydantic import EmailStr
from datetime import date
from sendmail import send_email
from typing import Annotated, Union
from fastapi import Request,BackgroundTasks, HTTPException





import io
AUTH_PREFIX='Bearer ' 
class usermanagement(Adduser):
    def __init__(self, session):
        super().__init__(session)
    def get_user_email_by_id(self, authorization:Annotated[Union[str,None],Header()]=None):
       return self.get_user_name_email(authorization= authorization)
        
    def sign_up_user(self, user: Usercreate, background_tasks: BackgroundTasks):  # Fixed type annotation
        if self.chk_user_email(user.email):
            raise HTTPException(status_code=400, detail="Email already in use")
        user.password = encrypt.hash_passwords(user.password)
        background_tasks.add_task(self.send_welcome_email, user.firstname, user.email)
        return self.create_user(user)

    def log_in(self, user: userinlogin):
        if self.chk_user_email(user.email):
            encryptedpass = self.get_user_by_email(user.email).password
            if encrypt.testing_password(user.password, encryptedpass):
                return jwtclass.jwt_gen(user_id=self.get_user_id(user))
            else:
                raise HTTPException(status_code=400, detail="Invalid credentials")
        raise HTTPException(status_code=400, detail="Account not found")

    def get_user_name(self, authorization: Annotated[Union[str, None], Header()] = None):
        return self.get_user_name_by_id(authorization=authorization)

    def book_Appointement(self, 
                         appointment_date: date, 
                         authorization: Annotated[Union[str, None], Header()] = None):
        return self.add_Appointement(appointment_date=appointment_date, authorization=authorization)

    def get_Appointement(self, authorization: Annotated[Union[str, None], Header()] = None):
        return self.get_Appointements(authorization=authorization)

    def admin_log_in(self, user: userinlogin):
        if self.chk_user_email(user.email):
            encryptedpass = self.get_user_by_email(user.email).password
            user_id = self.get_user_id(user)
            if (encrypt.testing_password(user.password, encryptedpass) and
                self.session.query(Admin).filter_by(user_id=user_id).first().role == "admin"):
                return jwtclass.jwt_gen_admin(user_id=user_id)
            raise HTTPException(status_code=400, detail="Invalid admin credentials")
        raise HTTPException(status_code=400, detail="Account not found")

    def get_Appointement_admin(self, authorization: Annotated[Union[str, None], Header()] = None):
        return self.get_Appointements2(authorization=authorization)

    def sign_up_admin(self, user: userinlogin):
        return self.create_user_admin(user)

    async def chk_pic(self,request: Request,  file: UploadFile = File(...),  email: EmailStr = Body(...),  authorization: Annotated[Union[str, None], Header()] = None):
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Not an image file")
        return await self.callai( email=email,request=request,  file=file, authorization=authorization)

    async def chk_pic2(self,request: Request,  file: UploadFile = File(...),  email: EmailStr = Body(...),  authorization: Annotated[Union[str, None], Header()] = None):
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Not an image file")
        return await self.callai2( email=email,request=request,  file=file, authorization=authorization)
        
    async def chk_pic3(self,request: Request,  file: UploadFile = File(...),  email: EmailStr = Body(...),  authorization: Annotated[Union[str, None], Header()] = None):
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Not an image file")
        return await self.dontcallai( email=email,request=request,  file=file, authorization=authorization)
    async def chk_pic22(self,request: Request,  file: UploadFile = File(...),  email: EmailStr = Body(...),  authorization: Annotated[Union[str, None], Header()] = None):
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Not an image file")
        return await self.callai22( email=email,request=request,  file=file, authorization=authorization)    







    def add_premium(self,authorization:Annotated[Union[str,None],Header()]=None):
       
        auth_exeption=HTTPException(status_code =status.HTTP_401_UNAUTHORIZED,detail='error')
        if not authorization:
          raise auth_exeption
        if not authorization.startswith(AUTH_PREFIX):
          raise auth_exeption
        payload= jwtclass.chk_token(token=authorization[len(AUTH_PREFIX):])
    
        if payload :
          new_premium_user = UserPremium(user_id=payload["user_id"])
          self.session.add(new_premium_user)
          self.session.commit()
          self.session.refresh(new_premium_user)
          return "ok"
        else:
            raise HTTPException(status_code =status.HTTP_401_UNAUTHORIZED,detail='ErrorOrNothinaaaaaaaaaaaaa') 

    def chk_premium(self,authorization:Annotated[Union[str,None],Header()]=None):
       
        auth_exeption=HTTPException(status_code =status.HTTP_401_UNAUTHORIZED,detail='error')
        if not authorization:
          raise auth_exeption
        if not authorization.startswith(AUTH_PREFIX):
          raise auth_exeption
        payload= jwtclass.chk_token(token=authorization[len(AUTH_PREFIX):])
    
        if payload and self.session.query(UserPremium).filter(UserPremium.user_id == payload["user_id"]).first():
          
          return True
        else:
          return False
    def get_admin_app(self,authorization:Annotated[Union[str,None],Header()]=None):
       
        auth_exeption=HTTPException(status_code =status.HTTP_401_UNAUTHORIZED,detail='error')
        if not authorization:
          raise auth_exeption
        if not authorization.startswith(AUTH_PREFIX):
          raise auth_exeption
        payload= jwtclass.chk_token(token=authorization[len(AUTH_PREFIX):])
        print(payload['role'])
        print(payload )

        if payload and payload['role']=="admin":
          appointments= self.session.query(Userr).filter().all()
          return appointments
        else:
            raise HTTPException(status_code =status.HTTP_401_UNAUTHORIZED,detail='ErrorOrNothinaaaaaaaaaaaaa')  
            

