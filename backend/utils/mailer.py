import os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

MAIL_USER = os.getenv("MAIL_USERNAME")
MAIL_PASS = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM", MAIL_USER)
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

def send_mail(to_addr: str, subject: str, html_body: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = MAIL_FROM
    msg["To"] = to_addr
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
        server.starttls()
        server.login(MAIL_USER, MAIL_PASS)
        server.send_message(msg)

def send_thank_you(user_email: str, name: str):
    body = f"""
    <p>Hi {name.split()[0]},</p>
    <p>Thank you for joining the <b>Chief AI Insights Beta Program</b>!</p>
    <p>We’ll review your inputs and share tailored insights soon.</p>
    <p>Warm regards,<br><b>Team Chief AI Insights</b></p>
    """
    send_mail(user_email, "Thanks for Joining Chief AI Insights Beta", body)

def notify_admin(name, email, company, role):
    body = f"""
    <h3>New Join Beta Submission</h3>
    <ul>
      <li><b>Name:</b> {name}</li>
      <li><b>Email:</b> {email}</li>
      <li><b>Company:</b> {company}</li>
      <li><b>Role:</b> {role}</li>
    </ul>
    """
    send_mail(ADMIN_EMAIL, f"New Join Beta – {name}", body)
