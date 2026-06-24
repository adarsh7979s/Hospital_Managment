"""
Standalone Email Service for Mini HMS.
Replaces the Serverless offline endpoint with a simple Flask-like HTTP server.
Listens on http://localhost:3000/dev/email and processes email triggers.
"""
import json
import smtplib
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from email.mime.text import MIMEText


class EmailHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/dev/email':
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
            return

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Invalid JSON: {e}"}).encode())
            return

        trigger = data.get('trigger')
        email = data.get('email')

        if not trigger or not email:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Missing 'trigger' or 'email'"}).encode())
            return

        # Build email content based on trigger type
        subject = ""
        content = ""

        if trigger == "SIGNUP_WELCOME":
            name = data.get('name', 'User')
            subject = "Welcome to Mini HMS!"
            content = (
                f"Hi {name},\n\n"
                "Welcome to the Mini Hospital Management System!\n\n"
                "Your account has been created successfully. You can now log in "
                "to manage availability (doctors) or book appointments (patients).\n\n"
                "Best regards,\nThe Mini HMS Team"
            )

        elif trigger == "BOOKING_CONFIRMATION":
            recipient_name = data.get('recipient_name', 'User')
            partner_name = data.get('partner_name', 'User')
            role = data.get('role', 'patient')
            start_time = data.get('start_time', 'scheduled time')
            subject = "Appointment Confirmed - Mini HMS"

            if role == "doctor":
                content = (
                    f"Hi Dr. {recipient_name},\n\n"
                    f"Patient {partner_name} has booked an appointment with you.\n\n"
                    f"Date/Time: {start_time}\n\n"
                    "Best regards,\nThe Mini HMS Team"
                )
            else:
                content = (
                    f"Hi {recipient_name},\n\n"
                    f"You have successfully booked an appointment with Dr. {partner_name}.\n\n"
                    f"Date/Time: {start_time}\n\n"
                    "Best regards,\nThe Mini HMS Team"
                )
        else:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Unknown trigger: {trigger}"}).encode())
            return

        # Send via SMTP
        smtp_host = os.environ.get('SMTP_HOST', 'localhost')
        smtp_port = int(os.environ.get('SMTP_PORT', '1025'))

        msg = MIMEText(content)
        msg['Subject'] = subject
        msg['From'] = 'noreply@minihms.local'
        msg['To'] = email

        try:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=5)
            server.sendmail(msg['From'], [email], msg.as_string())
            server.quit()
            print(f"[EMAIL SERVICE] OK - Sent {trigger} email to {email}")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"message": f"Sent {trigger} email to {email}"}).encode())
        except Exception as e:
            print(f"[EMAIL SERVICE] FAIL - SMTP failed for {email}: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"SMTP failed: {e}"}).encode())

    def log_message(self, format, *args):
        print(f"[EMAIL SERVICE] {args[0]}")


def run():
    server = HTTPServer(('127.0.0.1', 3000), EmailHandler)
    print("=" * 50)
    print("Email Service running at http://localhost:3000/dev/email")
    print("=" * 50)
    server.serve_forever()


if __name__ == '__main__':
    run()
