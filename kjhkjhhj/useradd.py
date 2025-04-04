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
from fastapi import UploadFile, File, HTTPException, Body, Header
from fastapi.responses import JSONResponse
from pydantic import EmailStr
import numpy as np
import tensorflow as tf
from PIL import Image
import io
from fastapi import UploadFile, File, Request
from PIL import Image
import numpy as np
import tensorflow as tf
from fastapi.responses import JSONResponse
import keras
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from sendmail import send_email_with_pdf
import io

AUTH_PREFIX='Bearer ' 
class_names = ['Normal', 'sick']
class Adduser(Fatherclass):
  def create_user(self,Usercreate: Usercreate):
      new_user = Userr(**Usercreate.dict(exclude_none=True))
      self.session.add(new_user)
      self.session.commit()
      self.session.refresh(new_user)
      print("finally")
      
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
  



  def get_user_name_by_id(self, authorization: Annotated[Union[str, None], Header()] = None):
      auth_exception = HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED, detail='u cant'
      )
      if not authorization:
          raise auth_exception
      if not authorization.startswith(AUTH_PREFIX):
          raise auth_exception
      payload = jwtclass.chk_token(token=authorization[len(AUTH_PREFIX):])
      if payload and payload['user_id']:
          result = self.session.query(Userr.firstname, Userr.lasttname).filter_by(id=payload['user_id']).first()
          if result:
              # Explicitly convert the tuple to a dictionary
              return {"firstname": result[0], "lastname": result[1]}
          else:
              raise auth_exception
      else:
          raise auth_exception



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
  async def results(self, request: Request, file: UploadFile,email:EmailStr):
    # Read the uploaded file
    img = Image.open(io.BytesIO(await file.read()))
    img = img.convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img)

    # Access the model from the application state
    model = request.app.state.model

    # Make a prediction
    prediction = model.predict(np.expand_dims(img_array, axis=0))
    probabilities = tf.nn.softmax(prediction).numpy()
    predicted_class_idx = np.argmax(probabilities)
    confidence = probabilities[0][predicted_class_idx]
    file.file.seek(0)
    return  await create_pdf_from_uploadfile(file=file,predicted_class= class_names[predicted_class_idx],confidence=round(confidence, 2),email=email)


  async def callai(
    self,
    email: EmailStr,
    request: Request,  # Add request parameter
    file: UploadFile = File(...),
    authorization: Annotated[Union[str, None], Header()] = None):
    auth_exeption = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='error'
    )
    if not authorization:
        raise auth_exeption
    if not authorization.startswith(AUTH_PREFIX):
        raise auth_exeption
    payload = jwtclass.chk_token(token=authorization[len(AUTH_PREFIX):])
    if payload and payload['role'] == "admin":
        await self.results(request, file,email)  
        return "done"
      


async def create_pdf_from_uploadfile( file: UploadFile,predicted_class: str,confidence: str,email:EmailStr) -> io.BytesIO:
    
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    
   
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter

    
    title = "Results of Analysis"
    c.setFont("Helvetica-Bold", 20)
    title_width = c.stringWidth(title, "Helvetica-Bold", 20)
    c.drawString((width - title_width) / 2, height - 50, title)
    
    
    img_io = io.BytesIO()
    image.save(img_io, format='PNG')
    img_io.seek(0)
    img_reader = ImageReader(img_io)
    
    
    img_width = 300  
    img_height = 300  
    img_x = (width - img_width) / 2
    img_y = (height - img_height) / 2 + 50  

    # Draw the image
    c.drawImage(img_reader, img_x, img_y, width=img_width, height=img_height)

    # Prediction results text
    result_text = f"Predicted Class: {predicted_class}\nAccuracy: {confidence}"
    c.setFont("Helvetica", 14)
    text_object = c.beginText(50, img_y - 80)
    for line in result_text.splitlines():
        text_object.textLine(line)
    c.drawText(text_object)
    
 
    if predicted_class.lower() == "sick":
        additional_msg = (
            "\nWe are sorry to tell you that the analysis indicates a potential issue.\n"
            "Please consult a healthcare professional for further \n\n diagnosis and do not rely solely on these results."
        )
        text_object = c.beginText(50, img_y - 140)
        for line in additional_msg.splitlines():
            text_object.textLine(line)
        c.drawText(text_object)

    # Disclaimer and support message
    disclaimer = (
        "This is an AI student project. Please consult a real doctor and do not rely solely on these results.\n"
        "If you notice any mistake, please contact support.\n\n"
        "Disclaimer: This is a student project prototype under active development.\n\n "
        "The AI classification feature is not yet functional, and its results are not guaranteed to be accurate."
    
    c.setFont("Helvetica-Oblique", 10)
    disclaimer_text = c.beginText(50, 100)
    for line in disclaimer.splitlines():
        disclaimer_text.textLine(line)
    c.drawText(disclaimer_text)
    sci_team_message = "SCI Team"
    c.setFont("Helvetica-Bold", 12)
    team_message_width = c.stringWidth(sci_team_message, "Helvetica-Bold", 12)
    c.drawString((width - team_message_width) / 2, 50, sci_team_message)

    # Finalize the PDF
    c.showPage()
    c.save()
    pdf_buffer.seek(0)
    
    return send_email_with_pdf(subject="result testing  mail", body = "Dear [Recipient's Name],\n\nPlease find your SCI results attached. The SCI team is available should you have any questions or need further assistance.\n\nBest regards,\nSCI Team", to=email, pdf_buffer=pdf_buffer)
