import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import os

# HTML Templates for Production Feel
ONBOARDING_HTML = """
<html>
  <body style="font-family: Arial, sans-serif; background-color: #f4f7f6; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
      <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Welcome to the Team, {name}! 🚀</h2>
      <p style="color: #555; font-size: 16px;">We are thrilled to have you onboard. Your employee portal account has been successfully provisioned.</p>
      
      <div style="background-color: #f8f9fa; border-left: 4px solid #3498db; padding: 15px; margin: 20px 0;">
        <h4 style="margin-top: 0; color: #2c3e50;">Your Login Credentials</h4>
        <p style="margin: 5px 0; color: #555;"><strong>Login Portal:</strong> <a href="{login_url}" style="color: #3498db; text-decoration: none;">{login_url}</a></p>
        <p style="margin: 5px 0; color: #555;"><strong>Email/Username:</strong> {email}</p>
        <p style="margin: 5px 0; color: #555;"><strong>Temporary Password:</strong> <code style="background:#e9ecef; padding:2px 6px; border-radius:4px;">{password}</code></p>
      </div>
      
      <p style="color: #555; font-size: 14px;"><em>Security Note: Please log in and change your password immediately.</em></p>
      <br>
      <p style="color: #7f8c8d; font-size: 14px; border-top: 1px solid #eee; padding-top: 15px;">Best Regards,<br><strong>HR Department</strong></p>
    </div>
  </body>
</html>
"""

LEAVE_APPROVAL_HTML = """
<html>
  <body style="font-family: Arial, sans-serif; background-color: #f4f7f6; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
      <h2 style="color: #2c3e50; border-bottom: 2px solid {color}; padding-bottom: 10px;">Leave Request {status_title} {emoji}</h2>
      <p style="color: #555; font-size: 16px;">Hello {name},</p>
      <p style="color: #555; font-size: 16px;">Your recent leave request has been reviewed by HR.</p>
      
      <div style="background-color: #f8f9fa; border-left: 4px solid {color}; padding: 15px; margin: 20px 0;">
        <h4 style="margin-top: 0; color: #2c3e50;">Leave Details</h4>
        <p style="margin: 5px 0; color: #555;"><strong>Type:</strong> {leave_type}</p>
        <p style="margin: 5px 0; color: #555;"><strong>Duration:</strong> {start_date} to {end_date}</p>
        <p style="margin: 5px 0; color: #555;"><strong>Status:</strong> <span style="color: {color}; font-weight: bold;">{status}</span></p>
      </div>
      
      <br>
      <p style="color: #7f8c8d; font-size: 14px; border-top: 1px solid #eee; padding-top: 15px;">Best Regards,<br><strong>HR Department</strong></p>
    </div>
  </body>
</html>
"""

def _send_email_async(subject, recipient, html_content):
    """
    Sends an email asynchronously. If SMTP environment variables are not set,
    it falls back to printing the email to the console (perfect for local dev).
    """
    mail_server = os.getenv('MAIL_SERVER')
    mail_port = os.getenv('MAIL_PORT', 587)
    mail_user = os.getenv('MAIL_USERNAME')
    mail_pass = os.getenv('MAIL_PASSWORD')
    
    if not all([mail_server, mail_user, mail_pass]):
        print("\n" + "="*60)
        print("📧 [EMAIL INTERCEPTED - SMTP NOT CONFIGURED]")
        print(f"To: {recipient}")
        print(f"Subject: {subject}")
        print("Body (HTML):\n" + html_content)
        print("="*60 + "\n")
        return

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = mail_user
        msg['To'] = recipient

        msg.attach(MIMEText(html_content, 'html'))

        with smtplib.SMTP(mail_server, int(mail_port)) as server:
            server.starttls()
            server.login(mail_user, mail_pass)
            server.send_message(msg)
            print(f"📧 Email successfully sent to {recipient}")
    except Exception as e:
        print(f"❌ Failed to send email to {recipient}: {str(e)}")

def send_onboarding_email(name, email, password, login_url):
    html = ONBOARDING_HTML.format(name=name, email=email, password=password, login_url=login_url)
    thread = threading.Thread(target=_send_email_async, args=("Welcome to the Team! 🚀", email, html))
    thread.daemon = True
    thread.start()

def send_leave_approval_email(name, email, leave_type, start_date, end_date, status):
    status_title = "Approved" if status.lower() == "approved" else "Rejected"
    color = "#28a745" if status.lower() == "approved" else "#dc3545"
    emoji = "✅" if status.lower() == "approved" else "❌"
    
    html = LEAVE_APPROVAL_HTML.format(
        name=name,
        color=color,
        status_title=status_title,
        emoji=emoji,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        status=status.upper()
    )
    thread = threading.Thread(target=_send_email_async, args=(f"Leave Request {status_title}", email, html))
    thread.daemon = True
    thread.start()
