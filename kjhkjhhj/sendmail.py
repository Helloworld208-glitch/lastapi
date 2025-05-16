import smtplib
from email.message import EmailMessage
import io


def send_email(subject: str, body: str, to: str):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = 'scistudyproject2025@gmail.com'
    msg['To'] = to
    msg.set_content(body)

    smtp_server = 'smtp.gmail.com'
    smtp_port = 465  
    username = 'scistudyproject2025@gmail.com'
    app_password = 'vyyo untb ktsh zdof'  

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
        smtp.set_debuglevel(1)  
        smtp.login(username, app_password)
        smtp.send_message(msg)



import io

def send_email_with_pdf(subject: str, body: str, to: str, pdf_buffer: io.BytesIO):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = 'scistudyproject2025@gmail.com'
    msg['To'] = to
    msg.set_content(body)

    
    pdf_data = pdf_buffer.read()
    msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename='results.pdf')

    smtp_server = 'smtp.gmail.com'
    smtp_port = 465  
    username = 'scistudyproject2025@gmail.com'
    app_password = 'vyyo untb ktsh zdof'  

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
        smtp.set_debuglevel(1) 
        smtp.login(username, app_password)
        smtp.send_message(msg)
    return "hello guys im working"    
