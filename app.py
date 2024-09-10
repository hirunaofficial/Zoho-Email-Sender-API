from flask import Flask, request, jsonify
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Get credentials and API key from .env
SENDER_EMAIL = os.getenv("EMAIL_USER")
PASSWORD = os.getenv("EMAIL_PASSWORD")
API_KEY = os.getenv("API_KEY")

# Zoho Mail server configuration
SMTP_SERVER = "smtp.zoho.com"
SMTP_PORT = 465

# Decorator to require API key for access
def require_api_key(f):
    def wrap(*args, **kwargs):
        request_api_key = request.headers.get('X-API-KEY')
        if request_api_key and request_api_key == API_KEY:
            return f(*args, **kwargs)
        else:
            return jsonify({
                "status": "error",
                "status_code": 401,
                "message": "Unauthorized access. Invalid API key."
            }), 401
    return wrap

@app.route('/send-email', methods=['POST'])
@require_api_key
def send_email():
    data = request.json
    try:
        # Get email data from request
        receiver_email = data['receiver_email']
        subject = data['subject']
        body = data['body']

        # Compose the email
        message = MIMEMultipart()
        message['From'] = SENDER_EMAIL
        message['To'] = receiver_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        # Send the email
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, message.as_string())
        server.quit()

        return jsonify({
            "status": "success",
            "status_code": 200,
            "message": "Email sent successfully!"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "status_code": 500,
            "message": f"Failed to send email. Error: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
