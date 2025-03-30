import smtplib
from email.message import EmailMessage

def send_email(subject: str, body: str, to: str):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = 'scistudyproject2025@gmail.com'
    msg['To'] = to
    msg.set_content(body)

    smtp_server = 'smtp.gmail.com'
    smtp_port = 465  # Using SSL for Gmail
    username = 'scistudyproject2025@gmail.com'
    app_password = 'nuvj utya gdbt zasx'  # Your provided app password

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
        smtp.set_debuglevel(1)  # Enable debug output
        smtp.login(username, app_password)
        smtp.send_message(msg)


