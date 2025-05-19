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
from user import Userr, Appointment, Admin, UserPremium
from typing import Annotated,Union
from pydantic import EmailStr
from fastapi import UploadFile, File, HTTPException, Body, Header
from fastapi.responses import JSONResponse
from pydantic import EmailStr
import numpy as np
import tensorflow as tf
from PIL import Image
from fastapi.responses import Response
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

from PIL import Image
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from sendmail import send_email_with_pdf
import io
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Image
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas

from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import io
from PIL import Image
from fastapi import UploadFile
from pydantic import EmailStr



AUTH_PREFIX='Bearer ' 
class_names = ['Normal', 'sick']
class_names2 = ['Lung_Opacity', 'Normal', 'Pneumonia_Merged']
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
  


  def get_user_name_email(self,authorization:Annotated[Union[str,None],Header()]=None):
    auth_exeption = HTTPException(
      status_code= status.HTTP_401_UNAUTHORIZED,detail='u cant')
    if not authorization:
      raise auth_exeption
    if not authorization.startswith(AUTH_PREFIX):
      raise   auth_exeption
    payload= jwtclass.chk_token(token=authorization[len(AUTH_PREFIX):])
    if payload and payload['user_id']:
     result = self.session.query(Userr.email).filter_by(id=payload['user_id']).first()
     if result:
        
        return  return {"email": result[0]}
     else:
        raise auth_exeption 
      
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
    return  await self.create_pdf_from_uploadfile(file=file,predicted_class= class_names[predicted_class_idx],confidence=round(confidence, 2),email=email)

  def search_mail(self,email:str, authorization: Annotated[Union[str, None], Header()] = None):
        auth_exeption = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='error')
        if not authorization:
          raise auth_exeption
        if not authorization.startswith(AUTH_PREFIX):
          raise auth_exeption
        payload = jwtclass.chk_token(token=authorization[len(AUTH_PREFIX):])
        if payload and payload['role'] == "admin":
           return self.session.query(Userr).filter(Userr.email.startswith(email)).limit(5).all()




  async def dontcallai(
    self,
    email: EmailStr,
    request: Request, 
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
        name=self.get_user_by_email(email).firstname
        send_email_with_pdf(
        subject="SCI Analysis Results",
        body=f"Dear {name},\n\nPlease find your analysis  attached. Contact us for further assistance.\n\nBest regards,\nSCI Team",
        to=email,
        pdf_buffer=file.file
    ) 
        return "done"
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
  async def callai2(
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
    if payload:
        return await self.results2(request, file,email)  
  async def callai22(
    self,
    email: EmailStr,
    request: Request,  
    file: UploadFile = File(...),
    authorization: Annotated[Union[str, None], Header()] = None):
    auth_exeption = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='error'
    )
    premium_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, 
    detail="Premium access required. Please upgrade your account to unlock this feature."
        )  
    if not authorization:
        raise auth_exeption
    if not authorization.startswith(AUTH_PREFIX):
        raise auth_exeption
    payload = jwtclass.chk_token(token=authorization[len(AUTH_PREFIX):])
    if payload:
        if self.session.query(UserPremium).filter(UserPremium.user_id == payload["user_id"]).first():
          return await self.results3(request, file,email)
        else:
          raise premium_exception
  from reportlab.lib.pagesizes import letter
  async def results3(self, request: Request, file: UploadFile, email: EmailStr):
    # Read & preprocess exactly like in Colab
    data = await file.read()
    img = Image.open(io.BytesIO(data)).convert("RGB").resize((224, 224))

    # ← Normalize to [0,1] and add batch dimension
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Access model 2 from the app state
    model2 = request.app.state.model2

    # Make prediction on the normalized batch
    prediction = model2.predict(img_array)
    probabilities = tf.nn.softmax(prediction, axis=1).numpy()
    predicted_class_idx = np.argmax(probabilities)
    confidence = probabilities[0][predicted_class_idx]

    # Reset file pointer for PDF creation
    file.file.seek(0)

    return await self.create_pdf_from(
        file=file,
        predicted_class=class_names2[predicted_class_idx],
        confidence=round(confidence, 2),
        email=email
    )

  async def create_pdf_from_uploadfile(self, file: UploadFile, predicted_class: str, confidence: str, email: EmailStr) -> io.BytesIO:
    # Read and process the uploaded file
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    # Create a PDF buffer
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter  # Width: 612, Height: 792 (letter size)

    # Title section (Top of the page)
    title = "Results of Analysis"
    c.setFont("Helvetica-Bold", 20)
    title_width = c.stringWidth(title, "Helvetica-Bold", 20)
    title_y = height - 50  # 50 points from the top (visible area)
    c.drawString((width - title_width) / 2, title_y, title)

    # Image section (centered below the title)
    img_io = io.BytesIO()
    image.save(img_io, format='PNG')
    img_io.seek(0)
    img_reader = ImageReader(img_io)

    img_width = 300
    img_height = 300
    img_x = (width - img_width) / 2
    img_y = title_y - 70 - img_height  # Position image 70 points below the title
    c.drawImage(img_reader, img_x, img_y, width=img_width, height=img_height)

    # Prediction result text (below the image)
    # FIX: Convert confidence to percentage (e.g., 0.99 → 99.00%)
    confidence = round(float(confidence) * 100, 2)  # Multiply by 100 to convert decimal to percentage
    result_text = f"Predicted Class: {predicted_class}\nConfidence: {confidence:.2f}%"  # Force 2 decimal places
    c.setFont("Helvetica", 14)
    text_y = img_y - 50  # 50 points below the image
    text_object = c.beginText(50, text_y)
    for line in result_text.splitlines():
        text_object.textLine(line)
    c.drawText(text_object)

    # Add message for "normal" class to reduce spacing
    if predicted_class.lower() == "normal":
        normal_msg = (
            "We're happy to inform you that the analysis did not detect any health issues. "
            "Maintain regular check-ups for preventive care."
        )
        c.setFont("Helvetica", 12)
        text_y -= 40  # Position below confidence text
        text_object = c.beginText(50, text_y)

        # Wrap text
        max_line_width = width - 100
        lines = []
        current_line = ""
        for word in normal_msg.split(" "):
            test_line = current_line + (" " if current_line else "") + word
            if c.stringWidth(test_line, "Helvetica", 12) <= max_line_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        # Draw wrapped text
        for line in lines:
            text_object.textLine(line)
        c.drawText(text_object)
        text_y -= (len(lines) * 14)  # Update position for next sections

    # Additional message if "sick" (positioned closer to the disclaimer)
    if predicted_class.lower() == "sick":
        additional_msg = (
            "We regret to inform you that the analysis suggests a potential health issue. "
            "Please consult a healthcare professional for further diagnosis. Do not rely solely on these results."
        )
        c.setFont("Helvetica", 12)
        text_y -= 40  # Move 40 points below the prediction result

        # Text wrapping logic
        max_line_width = width - 100
        lines = []
        current_line = ""
        for word in additional_msg.split(" "):
            test_line = current_line + (" " if current_line else "") + word
            if c.stringWidth(test_line, "Helvetica", 12) <= max_line_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        # Draw the wrapped text
        text_object = c.beginText(50, text_y)
        for line in lines:
            text_object.textLine(line)
        c.drawText(text_object)
        text_y -= (len(lines) * 14)  # Update position for next sections

    # Disclaimer (red text, positioned dynamically)
    c.setFillColorRGB(1, 0, 0)
    disclaimer = (
        "This is an AI student project. Please consult a real doctor for professional medical advice."
        "\nThe AI classification feature is not yet fully functional, and results may not be accurate."
        "\nFor any concerns, please contact support."
    )
    c.setFont("Helvetica-Oblique", 10)
    disclaimer_y = text_y - 30  # Position below the last message
    text_object = c.beginText(50, disclaimer_y)
    for line in disclaimer.splitlines():
        text_object.textLine(line)
    c.drawText(text_object)

    # SCI Team footer (bottom of the page)
    c.setFillColor(colors.black)
    sci_team_message = "SCI Team"
    c.setFont("Helvetica-Bold", 12)
    team_message_width = c.stringWidth(sci_team_message, "Helvetica-Bold", 12)
    c.drawString((width - team_message_width) / 2, 50, sci_team_message)  # 50 points from the bottom

    # Finalize and return the PDF
    c.showPage()
    c.save()
    pdf_buffer.seek(0)

    name=self.get_user_by_email(email).firstname
    send_email_with_pdf(
        subject="SCI Analysis Results",
        body=f"Dear {name},\n\nPlease find your analysis results attached. Contact us for further assistance.\n\nBest regards,\nSCI Team",
        to=email,
        pdf_buffer=pdf_buffer
    )
    return pdf_buffer

  async def results2(self, request: Request, file: UploadFile,email:EmailStr):
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
    return  await self.create_pdf_from(file=file,predicted_class= class_names[predicted_class_idx],confidence=round(confidence, 2),email=email)
  async def create_pdf_from(self, file: UploadFile, predicted_class: str, confidence: str, email: EmailStr) -> io.BytesIO:
      # Read and process the uploaded file
      contents = await file.read()
      image = Image.open(io.BytesIO(contents)).convert("RGB")
  
      # Create a PDF buffer
      pdf_buffer = io.BytesIO()
      c = canvas.Canvas(pdf_buffer, pagesize=letter)
      width, height = letter  # Width: 612, Height: 792 (letter size)
  
      # Title section (Top of the page)
      title = "Results of Analysis"
      c.setFont("Helvetica-Bold", 20)
      title_width = c.stringWidth(title, "Helvetica-Bold", 20)
      title_y = height - 50  # 50 points from the top (visible area)
      c.drawString((width - title_width) / 2, title_y, title)
  
      # Image section (centered below the title)
      img_io = io.BytesIO()
      image.save(img_io, format='PNG')
      img_io.seek(0)
      img_reader = ImageReader(img_io)
  
      img_width = 300
      img_height = 300
      img_x = (width - img_width) / 2
      img_y = title_y - 70 - img_height  # Position image 70 points below the title
      c.drawImage(img_reader, img_x, img_y, width=img_width, height=img_height)
  
      # Prediction result text (below the image)
      # FIX: Convert confidence to percentage (e.g., 0.99 → 99.00%)
      confidence = round(float(confidence) * 100, 2)  # Multiply by 100 to convert decimal to percentage
      result_text = f"Predicted Class: {predicted_class}\nConfidence: {confidence:.2f}%"  # Force 2 decimal places
      c.setFont("Helvetica", 14)
      text_y = img_y - 50  # 50 points below the image
      text_object = c.beginText(50, text_y)
      for line in result_text.splitlines():
          text_object.textLine(line)
      c.drawText(text_object)
  
      # Add message for "normal" class to reduce spacing
      if predicted_class.lower() == "normal":
          normal_msg = (
              "We're happy to inform you that the analysis did not detect any health issues. "
              "Maintain regular check-ups for preventive care."
          )
          c.setFont("Helvetica", 12)
          text_y -= 40  # Position below confidence text
          text_object = c.beginText(50, text_y)
  
          # Wrap text
          max_line_width = width - 100
          lines = []
          current_line = ""
          for word in normal_msg.split(" "):
              test_line = current_line + (" " if current_line else "") + word
              if c.stringWidth(test_line, "Helvetica", 12) <= max_line_width:
                  current_line = test_line
              else:
                  lines.append(current_line)
                  current_line = word
          if current_line:
              lines.append(current_line)
  
          # Draw wrapped text
          for line in lines:
              text_object.textLine(line)
          c.drawText(text_object)
          text_y -= (len(lines) * 14)  # Update position for next sections
  
      # Additional message if "sick" (positioned closer to the disclaimer)
      if predicted_class.lower() == "sick":
          additional_msg = (
              "We regret to inform you that the analysis suggests a potential health issue. "
              "Please consult a healthcare professional for further diagnosis. Do not rely solely on these results."
          )
          c.setFont("Helvetica", 12)
          text_y -= 40  # Move 40 points below the prediction result
  
          # Text wrapping logic
          max_line_width = width - 100
          lines = []
          current_line = ""
          for word in additional_msg.split(" "):
              test_line = current_line + (" " if current_line else "") + word
              if c.stringWidth(test_line, "Helvetica", 12) <= max_line_width:
                  current_line = test_line
              else:
                  lines.append(current_line)
                  current_line = word
          if current_line:
              lines.append(current_line)
  
          # Draw the wrapped text
          text_object = c.beginText(50, text_y)
          for line in lines:
              text_object.textLine(line)
          c.drawText(text_object)
          text_y -= (len(lines) * 14)  # Update position for next sections
  
      # Disclaimer (red text, positioned dynamically)
      c.setFillColorRGB(1, 0, 0)
      disclaimer = (
          "This is an AI student project. Please consult a real doctor for professional medical advice."
          "\nThe AI classification feature is not yet fully functional, and results may not be accurate."
          "\nFor any concerns, please contact support."
      )
      c.setFont("Helvetica-Oblique", 10)
      disclaimer_y = text_y - 30  # Position below the last message
      text_object = c.beginText(50, disclaimer_y)
      for line in disclaimer.splitlines():
          text_object.textLine(line)
      c.drawText(text_object)
  
      # SCI Team footer (bottom of the page)
      c.setFillColor(colors.black)
      sci_team_message = "SCI Team"
      c.setFont("Helvetica-Bold", 12)
      team_message_width = c.stringWidth(sci_team_message, "Helvetica-Bold", 12)
      c.drawString((width - team_message_width) / 2, 50, sci_team_message)  # 50 points from the bottom
  
      # Finalize and return the PDF
      c.showPage()
      c.save()
      pdf_buffer.seek(0)
      pdf_content = pdf_buffer.getvalue()
  
      return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=example.pdf"})
    
