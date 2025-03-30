from base import Fatherclass
from schema import Usercreate,userinlogin
from user import Userr,Admin
from security.jwt import  jwtclass
from typing import Annotated,Union
import pydantic
from fastapi import Header,HTTPException,status
import security.jwt
from user import Appointment
from datetime import date
from schema import datemodel
from sendmail import send_email
from typing import Annotated,Union
from pydantic import EmailStr

AUTH_PREFIX='Bearer ' 

class Adduser(Fatherclass):
  def create_user(self,Usercreate: Usercreate):
      new_user = Userr(**Usercreate.dict(exclude_none=True))
      self.session.add(new_user)
      self.session.commit()
      self.session.refresh(new_user)
      print("finally")
      self.send_welcome_email(Usercreate.firstname,Usercreate.email)
      return jwtclass.jwt_gen(new_user.id)
  




  def create_user_admin(self,user:userinlogin):
      user_id= self.get_user_id(user=user)
      new= Admin(user_id=user_id)
      self.session.add(new)
      self.session.commit()
      self.session.refresh(new)
      print("finally")
      return jwtclass.jwt_gen_admin(new.id)
  




  def get_user_by_email(self,email:str):
    user = self.session.query(Userr).filter_by(email=email).first()
    return user
  

  def chk_user_email(self,email:str):
    user = self.session.query(Userr).filter_by(email=email).first()
    return bool(user)
  



  def get_user_name_by_id(self,authorization:Annotated[Union[str,None],Header()]=None):
    auth_exeption = HTTPException(
      status_code= status.HTTP_401_UNAUTHORIZED,detail='u cant')
    if not authorization:
      raise auth_exeption
    if not authorization.startswith(AUTH_PREFIX):
      raise   auth_exeption
    payload= jwtclass.chk_token(token=authorization[len(AUTH_PREFIX):])
    if payload and payload['user_id']:
     result = self.session.query(Userr.firstname, Userr.lasttname).filter_by(id=payload['user_id']).first()
     if result:
    # Explicitly convert the tuple to a dictionary
       return {"firstname": result[0], "lastname": result[1]}
      else:
      raise auth_exeption
    else:
      raise auth_exeption


  def get_user_id(self,user:userinlogin):
    return self.session.query(Userr).filter_by(email=user.email).first().id
  

  def add_Appointement(self,appointment_date:date,authorization:Annotated[Union[str,None],Header()]=None):
    auth_exeption=HTTPException(status_code =status.HTTP_401_UNAUTHORIZED,detail='wyd')
      
    
    if not authorization:
      raise auth_exeption
    if not authorization.startswith(AUTH_PREFIX):
      raise auth_exeption
    payload= jwtclass.chk_token(token=authorization[len(AUTH_PREFIX):])
    if payload and payload['user_id']:
      appointment_count = self.session.query(Appointment).filter(Appointment.user_id == payload['user_id']).count()
      if appointment_count<3:
        new_Appointement= datemodel(appointment_date=appointment_date,user_id=payload['user_id'],status='pending')
        new_Appointement = Appointment(**new_Appointement.dict(exclude_none=True))
        self.session.add(new_Appointement)
        self.session.commit()
        self.session.refresh(new_Appointement)
        return "success"
      else:
        raise HTTPException(status_code =status.HTTP_401_UNAUTHORIZED,detail='cant')   
      

  def get_Appointements(self,authorization:Annotated[Union[str,None],Header()]=None):
        auth_exeption=HTTPException(status_code =status.HTTP_401_UNAUTHORIZED,detail='error')
        if not authorization:
          raise auth_exeption
        if not authorization.startswith(AUTH_PREFIX):
          raise auth_exeption
        payload= jwtclass.chk_token(token=authorization[len(AUTH_PREFIX):])
        if payload and payload['user_id']:
          appointments= self.session.query(Appointment).filter(Appointment.user_id == payload['user_id']).all()
          return appointments
        else:
            raise HTTPException(status_code =status.HTTP_401_UNAUTHORIZED,detail='ErrorOrNothing')   
          



  def get_Appointements2(self,authorization:Annotated[Union[str,None],Header()]=None):
        auth_exeption=HTTPException(status_code =status.HTTP_401_UNAUTHORIZED,detail='error')
        if not authorization:
          raise auth_exeption
        if not authorization.startswith(AUTH_PREFIX):
          raise auth_exeption
        payload= jwtclass.chk_token(token=authorization[len(AUTH_PREFIX):])
        print(payload['role'])
        print(payload )

        if payload and payload['role']=="admin":
          appointments= self.session.query(Appointment).filter(Appointment.status=='pending').all()
          return appointments
        else:
            raise HTTPException(status_code =status.HTTP_401_UNAUTHORIZED,detail='ErrorOrNothinaaaaaaaaaaaaa')  
         
  def update_appointment(self,Date:date,appointmentId:int,statue:str,authorization:Annotated[Union[str,None],Header()]=None):
        auth_exeption=HTTPException(status_code =status.HTTP_401_UNAUTHORIZED,detail='danger')
        auth_exeption2=HTTPException(status_code =status.HTTP_401_UNAUTHORIZED,detail='danger')
        if not authorization:
          raise auth_exeption
        if not authorization.startswith(AUTH_PREFIX):
          raise auth_exeption
        payload= jwtclass.chk_token(token=authorization[len(AUTH_PREFIX):])
        if payload and payload['role']=="admin":
           self.session.query(Appointment).filter(Appointment.appointment_id==appointmentId).update({Appointment.status:statue})
           self.session.commit()
           id=self.session.query(Appointment).filter(Appointment.appointment_id==appointmentId).first().user_id
           user=self.session.query(Userr).filter(Userr.id==id).first()
           self.mail_respond(user.firstname,statue,Date,user.email)
           
           return "ok"
           
  def mail_respond(self, first_name: str, state: str, Date: date, mail: EmailStr):
    if state == 'approved':
        send_email(
            subject="Appointment Approved",
            body=f"Hi {first_name},\n\nYour appointment at {Date} has been approved. We look forward to seeing you!\n\nBest regards,\nSCI Team",
            to=mail
        )
    elif state == 'rejected':
        send_email(
            subject="Appointment Rejected",
            body=f"Hi {first_name},\n\nWe regret to inform you that your appointment on {Date} has been rejected. "
                 "For more information, please contact our support.\n\n"
                 "Best regards,\nSCI Team",
            to=mail
        )
          
  def send_welcome_email(self,first_name: str, mail: EmailStr):
   
      send_email(
          subject="Welcome to SCI!",
          body=  f"Hi {first_name},\n\n"
          "Welcome to SCI! We're glad to have you with us.\n"
          "If you need any help, feel free to reach out.\n\n"
          "Best regards,\nSCI Team",
          to=mail
      )
      
