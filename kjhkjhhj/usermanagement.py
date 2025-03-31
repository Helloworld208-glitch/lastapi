from useradd import Adduser
from schema import Usercreate,userinlogin
from security.codingdata import encrypt
from security.jwt import jwtclass
from fastapi import HTTPException
from user import Userr
from database import get_db
from base import Fatherclass
from schema import Usercreate,userinlogin
from user import Userr
from security.jwt import  jwtclass
from typing import Annotated,Union
import pydantic
from fastapi import Header,HTTPException,status
import security.jwt
from useradd import Fatherclass
from user import Appointment
from datetime import date
from user import Admin
from sendmail import send_email
from fastapi import BackgroundTasks, HTTPException, APIRouter
class usermanagement(Adduser):
    
    def __init__(self, session):
        super().__init__(session)
        
    def sign_up_user(self, Usercreate: Usercreate, background_tasks: BackgroundTasks):
        if self.chk_user_email(Usercreate.email):
            raise HTTPException(status_code=400, detail="Email already in use")
        Usercreate.password = encrypt.hash_passwords(Usercreate.password)
        print("im here")
        # Your inline instantiation:
        background_tasks.add_task(usermanagement(self.session).send_welcome_email, Usercreate.firstname, Usercreate.email)
        return self.create_user(Usercreate)

    
    def log_in(self,user:userinlogin):
        if(self.chk_user_email(user.email)):
          encryptedpass=self.session.query(Userr).filter_by(email=user.email).first().password
          encryptedpass=self.get_user_by_email(user.email).password
          if(encrypt.testing_password(user.password,encryptedpass)):
             return jwtclass.jwt_gen(user_id=self.get_user_id(user))
          else:
              raise HTTPException(status_code=400, detail="please check yout inputs") 
        raise HTTPException(status_code=400, detail="account not found")
    
    def get_user_name(self, authorization:Annotated[Union[str,None],Header()]=None):
       return self.get_user_name_by_id(authorization= authorization)
    

    def book_Appointement(self,appointment_date:date,authorization:Annotated[Union[str,None],Header()]=None):
       return self.add_Appointement(appointment_date=appointment_date,authorization=authorization)
    



    def get_Appointement(self,authorization:Annotated[Union[str,None],Header()]=None):
       return self.get_Appointements(authorization=authorization)

    def admin_log_in(self,user:userinlogin):
        if(self.chk_user_email(user.email)):
          encryptedpass=self.session.query(Userr).filter_by(email=user.email).first().password
          encryptedpass=self.get_user_by_email(user.email).password
          userr=self.get_user_id(user)
          if(encrypt.testing_password(user.password,encryptedpass)) and self.session.query(Admin).filter_by(user_id=userr).first().role=="admin":
             return jwtclass.jwt_gen_admin(user_id=self.get_user_id(user))
          else:
              raise HTTPException(status_code=400, detail="please check yout inputs") 
        raise HTTPException(status_code=400, detail="account not found")       
    def get_Appointement_admin(self,authorization:Annotated[Union[str,None],Header()]=None):
       return self.get_Appointements2(authorization=authorization) 
    
    def sign_up_admin(self,user:userinlogin):
       
        
        return   self.create_user_admin(user)

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
        



