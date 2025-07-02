import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

async def send_verification_email(email_to: str, verification_url: str):
    if not all([settings.smtp_server, settings.smtp_port, settings.smtp_username, settings.smtp_password]):
        print(f"Email verification would be sent to {email_to} with URL: {verification_url}")
        return
    
    message = MIMEMultipart("alternative")
    message["Subject"] = "Verify your email"
    message["From"] = settings.from_email
    message["To"] = email_to

    text = f"""\
    Hi,
    Please verify your email by clicking the link below:
    {verification_url}
    """
    html = f"""\
    <html>
      <body>
        <p>Hi,<br>
           Please verify your email by clicking the link below:<br>
           <a href="{verification_url}">{verification_url}</a>
        </p>
      </body>
    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(message)