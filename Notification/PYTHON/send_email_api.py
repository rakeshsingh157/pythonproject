from fastapi import FastAPI
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText

app = FastAPI()

class EmailRequest(BaseModel):
    to: str
    subject: str
    message: str

@app.post("/sendEmail")
def send_email(req: EmailRequest):
    sender = "jobportal00000@gmail.com"
    password = "gztykeykurgggklb"

    msg = MIMEText(req.message)
    msg['Subject'] = req.subject
    msg['From'] = sender
    msg['To'] = req.to

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, req.to, msg.as_string())
        server.quit()
        return {"status": "Email sent successfully!"}
    except Exception as e:
        return {"error": str(e)}
