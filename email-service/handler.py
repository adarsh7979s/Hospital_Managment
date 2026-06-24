import json
import smtplib
import os
from email.mime.text import MIMEText

def send_email(event, context):
    try:
        # API Gateway HTTP proxy event passes the POST payload as a string under 'body'
        body = event.get('body', '{}')
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = body
    except Exception as e:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"Invalid JSON request body: {str(e)}"})
        }

    trigger = data.get('trigger')
    email = data.get('email')

    if not trigger or not email:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing 'trigger' or 'email' parameter."})
        }

    # Generate email subject and body based on the trigger type
    subject = ""
    content = ""

    if trigger == "SIGNUP_WELCOME":
        name = data.get('name', 'User')
        subject = "Welcome to Mini HMS!"
        content = f"Hi {name},\n\nWelcome to the Mini Hospital Management System (HMS)!\n\nYour account has been successfully created. You can now log in to manage your availability slots (as a doctor) or browse doctors and schedule bookings (as a patient).\n\nBest regards,\nThe Mini HMS Team"
        
    elif trigger == "BOOKING_CONFIRMATION":
        recipient_name = data.get('recipient_name', 'User')
        partner_name = data.get('partner_name', 'User')
        role = data.get('role', 'patient')
        start_time = data.get('start_time', 'scheduled time')

        subject = "Appointment Confirmed - Mini HMS"
        if role == "doctor":
            content = f"Hi Dr. {recipient_name},\n\nThis email is to confirm that patient {partner_name} has booked an appointment with you.\n\nDetails:\n- Date/Time: {start_time}\n- Location: Doctor Dashboard / Google Calendar\n\nBest regards,\nThe Mini HMS Team"
        else:
            content = f"Hi {recipient_name},\n\nThis email is to confirm that you have successfully booked an appointment with Dr. {partner_name}.\n\nDetails:\n- Date/Time: {start_time}\n- Location: Patient Dashboard / Google Calendar\n\nBest regards,\nThe Mini HMS Team"
    else:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"Unsupported trigger type: {trigger}"})
        }

    # Retrieve SMTP configurations (defaults to local python debugging SMTP server)
    smtp_host = os.environ.get('SMTP_HOST', 'localhost')
    smtp_port = int(os.environ.get('SMTP_PORT', '1025'))
    smtp_user = os.environ.get('SMTP_USER', '')
    smtp_pass = os.environ.get('SMTP_PASSWORD', '')

    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = 'noreply@minihms.local'
    msg['To'] = email

    try:
        # Connect and send via SMTP
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=5)
        if smtp_user and smtp_pass:
            if smtp_port == 587:
                server.starttls()
            server.login(smtp_user, smtp_pass)
        
        server.sendmail(msg['From'], [email], msg.as_string())
        server.quit()
        
        print(f"Sent email for {trigger} to {email} successfully.")
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": f"Successfully sent {trigger} email to {email}."})
        }
    except Exception as e:
        print(f"Error occurred while sending email to {email}: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"SMTP delivery failed: {str(e)}"})
        }
