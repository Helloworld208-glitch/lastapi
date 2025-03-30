from pydantic import EmailStr,BaseModel
from datetime import date


class Usercreate(BaseModel):
    firstname:str
    lasttname:str
    email: EmailStr
    password:str





class userinlogin(BaseModel):
      email: EmailStr
      password:str
class datemodel(BaseModel):
     appointment_date: date
     user_id:int
     status: str