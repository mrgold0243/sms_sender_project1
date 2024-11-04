import json  # Make sure to import json at the top
from flask import Flask, render_template, request, redirect, url_for, flash
from .user_auth import authenticate_user, check_subscription_status
from .database import load_subscriber
from main import (
    send_sms_twilio,
    send_sms_nexmo,
    send_sms_onesignal,
    send_sms_smtp,
    send_sms_aws
)

# Load configuration from JSON
with open('config/config.json') as config_file:
    config = json.load(config_file)
    ENABLE_TWILIO = config.get('ENABLE_TWILIO', False)
    ENABLE_NEXMO = config.get('ENABLE_NEXMO', False)
    ENABLE_ONESIGNAL = config.get('ENABLE_ONESIGNAL', False)
    ENABLE_SMTP = config.get('ENABLE_SMTP', False)
    ENABLE_AWS_SNS = config.get('ENABLE_AWS_SNS', False)

import logging
import re  # Import regex for phone number validation

app = Flask(__name__)
app.secret_key = 'AKIA5CBGTD46SMVMEQ2Y'  # Change this to a random secret key

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if authenticate_user(username, password):
        is_active, expiry_date = check_subscription_status(username)
        if is_active:
            return redirect(url_for('status', username=username))
        else:
            flash('Your subscription has expired. Please contact us to renew.')
            return redirect(url_for('index'))
    else:
        flash('Authentication failed. Please check your username and password.')
        return redirect(url_for('index'))

@app.route('/status/<username>')
def status(username):
    user_data = load_subscriber(username)
    is_active, expiry_date = check_subscription_status(username)
    return render_template('status.html', username=username, is_active=is_active, expiry_date=expiry_date)

@app.route('/send', methods=['GET', 'POST'])
def send_message():
    if request.method == 'POST':
        recipient = request.form['recipient']
        message = request.form['message']
        
        # Validate the recipient phone number
        if not validate_phone_number(recipient):
            flash('Invalid phone number format. Please use E.164 format (e.g., +123456789).')
            return redirect(url_for('send_message'))

        # Attempt to send the message
        try:
            if ENABLE_TWILIO:
                send_sms_twilio(recipient, message)
            elif ENABLE_NEXMO:
                send_sms_nexmo(recipient, message)
            elif ENABLE_ONESIGNAL:
                send_sms_onesignal(recipient, message)
            elif ENABLE_SMTP:
                send_sms_smtp(recipient, message)
            elif ENABLE_AWS_SNS:
                send_sms_aws(recipient, message)
            else:
                flash('No SMS service is enabled.')
                return redirect(url_for('send_message'))
            
            flash('Message sent successfully!')
        except Exception as e:
            flash(f'Error sending message: {str(e)}')

        return redirect(url_for('index'))
    
    return render_template('send_message.html')

def validate_phone_number(phone_number):
    """Validate phone number format using E.164 format."""
    pattern = re.compile(r'^\+?[1-9]\d{1,14}$')
    return bool(pattern.match(phone_number))

if __name__ == '__main__':
    app.run(debug=True)
