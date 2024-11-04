import requests
import csv
import json
import smtplib
import time
import logging
import re
import boto3
from botocore.exceptions import ClientError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from vonage import Client as VonageClient
import os
import sys
import watchdog.events
import watchdog.observers
from src.user_auth import authenticate_user, check_subscription_status  # Adjust import based on your structure

# Setup logging
logging.basicConfig(level=logging.DEBUG)

def load_config():
    """Load configuration from a JSON file."""
    base_path = getattr(sys, 'frozen', False) and sys._MEIPASS or os.path.dirname(__file__)
    config_path = os.path.join(base_path, 'config', 'config.json')
    logging.debug(f'Loading config from: {config_path}')
    with open(config_path) as config_file:
        return json.load(config_file)

def get_data_file_path(filename):
    """Returns the absolute path for data files."""
    base_path = getattr(sys, 'frozen', False) and sys._MEIPASS or os.path.dirname(__file__)
    return os.path.join(base_path, 'data', filename)

# Load configuration
config = load_config()

# Assign variables from config
API_KEY = config['API_KEY']
APP_ID = config['APP_ID']
TWILIO_ACCOUNT_SID = config['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = config['TWILIO_AUTH_TOKEN']
TWILIO_PHONE_NUMBER = config['TWILIO_PHONE_NUMBER']
NEXMO_API_KEY = config['NEXMO_API_KEY']
NEXMO_API_SECRET = config['NEXMO_API_SECRET']
NEXMO_PHONE_NUMBER = config['NEXMO_PHONE_NUMBER']
SMTP_SERVER = config['SMTP_SERVER']
SMTP_PORT = config['SMTP_PORT']
SMTP_USER = config['SMTP_USER']
SMTP_PASSWORD = config['SMTP_PASSWORD']
SMTP_DELAY = config['SMTP_DELAY']
AWS_ACCESS_KEY = config['AWS_ACCESS_KEY']
AWS_SECRET_KEY = config['AWS_SECRET_KEY']
AWS_REGION = config['AWS_REGION']
ENABLE_ONESIGNAL = config['ENABLE_ONESIGNAL']
ENABLE_TWILIO = config['ENABLE_TWILIO']
ENABLE_NEXMO = config['ENABLE_NEXMO']
ENABLE_SMTP = config['ENABLE_SMTP']
ENABLE_AWS_SNS = config['ENABLE_AWS_SNS']

def validate_phone_number(phone_number):
    """Validate phone number format using E.164 format."""
    pattern = re.compile(r'^\+?[1-9]\d{1,14}$')
    return bool(pattern.match(phone_number))

def display_user_info(username, subscription_type, subscription_expiry):
    """Display user information."""
    print("User Information:")
    print(f"Username: {username}")
    print(f"Subscription Type: {subscription_type}")
    print(f"Subscription Expiry: {subscription_expiry}")

def send_sms_onesignal(phone_number, message):
    """Send SMS via OneSignal."""
    if not validate_phone_number(phone_number):
        logging.error(f'Invalid phone number format: {phone_number}')
        return None

    logging.debug(f'Sending SMS via OneSignal to {phone_number}')
    url = 'https://onesignal.com/api/v1/notifications'
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f'Basic {API_KEY}',
    }

    data = {
        'app_id': APP_ID,
        'include_external_user_ids': [phone_number],
        'contents': {'en': message},
        'channel_for_external_user_ids': 'sms'
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            logging.error(f'OneSignal Error: {response.status_code} - {response.text}')
    except Exception as e:
        logging.error(f'Error during OneSignal request: {e}')
        return None

    logging.info(f'SMS sent via OneSignal to {phone_number}')
    return response

def send_sms_twilio(phone_number, message):
    """Send SMS via Twilio."""
    if not validate_phone_number(phone_number):
        logging.error(f'Invalid phone number format: {phone_number}')
        return None

    logging.debug(f'Sending SMS via Twilio to {phone_number}')
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    try:
        message = client.messages.create(body=message, from_=TWILIO_PHONE_NUMBER, to=phone_number)
        logging.info(f'Twilio message SID: {message.sid}')
        return message.sid
    except Exception as e:
        logging.error(f'Error sending SMS via Twilio: {e}')
        return None

def send_sms_nexmo(phone_number, message):
    """Send SMS via Nexmo."""
    if not validate_phone_number(phone_number):
        logging.error(f'Invalid phone number format: {phone_number}')
        return None

    logging.debug(f'Sending SMS via Nexmo to {phone_number}')
    client = VonageClient(key=NEXMO_API_KEY, secret=NEXMO_API_SECRET)
    try:
        response = client.sms.send_message({
            'from': NEXMO_PHONE_NUMBER,
            'to': phone_number,
            'text': message,
        })
        logging.info(f'SMS sent via Nexmo to {phone_number}')
        return response
    except Exception as e:
        logging.error(f'Error sending SMS via Nexmo: {e}')
        return None

def send_sms_smtp(phone_number, message):
    """Send SMS via SMTP."""
    if '@' not in phone_number:
        logging.error(f'Phone number must include carrier domain: {phone_number}')
        return False

    logging.debug(f'Sending SMS via SMTP to {phone_number}')
    gateway_address = phone_number

    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = gateway_address
    msg['Subject'] = 'Notification'
    msg.attach(MIMEText(message, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, gateway_address, msg.as_string())
        logging.info(f'SMS sent successfully via SMTP to {phone_number}')
        return True
    except Exception as e:
        logging.error(f'Error sending SMS via SMTP to {phone_number}: {e}')
        return False

def send_sms_aws(phone_number, message):
    """Send SMS via AWS SNS."""
    if not validate_phone_number(phone_number):
        logging.error(f'Invalid phone number format: {phone_number}')
        return None

    logging.debug(f'Sending SMS via AWS SNS to {phone_number}')
    
    sns_client = boto3.client(
        'sns',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = sns_client.publish(
                PhoneNumber=phone_number,
                Message=message
            )
            logging.info(f'SMS sent via AWS SNS to {phone_number}')
            return response['ResponseMetadata']['HTTPStatusCode'] == 200
        except ClientError as e:
            logging.error(f'Attempt {attempt + 1}: Error sending SMS via AWS SNS: {e.response["Error"]["Message"]}')
            if attempt == max_retries - 1:
                return None
            time.sleep(1)

def load_data():
    """Load phone numbers and messages from CSV files."""
    logging.debug('Loading phone numbers and messages')
    sms_phone_numbers, smtp_phone_numbers = [], []

    contacts_file_path = get_data_file_path('contacts.csv')
    messages_file_path = get_data_file_path('messages.csv')

    logging.debug(f'Contacts file path: {contacts_file_path}')
    logging.debug(f'Messages file path: {messages_file_path}')

    try:
        # Load contacts
        with open(contacts_file_path, mode='r') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            logging.debug(f'CSV headers: {headers}')

            for row in reader:
                sms_phone_number = row.get('phone_number')
                smtp_phone_number = row.get('phone_number@carrier')

                if sms_phone_number:
                    sms_phone_numbers.append(sms_phone_number)
                if smtp_phone_number:
                    smtp_phone_numbers.append(smtp_phone_number)

        # Load messages
        messages = []
        with open(messages_file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                messages.append(row['message'])

        if not messages:
            logging.warning('No messages found in messages.csv, using a default message.')
            messages.append("Default message")

        logging.debug(f'Loaded {len(sms_phone_numbers)} SMS phone numbers, {len(smtp_phone_numbers)} SMTP phone numbers, and {len(messages)} messages')
        return sms_phone_numbers, smtp_phone_numbers, messages

    except FileNotFoundError as e:
        logging.error(f'File not found: {e}')
        return [], [], []
    except Exception as e:
        logging.error(f'Error loading data: {e}')
        return [], [], []

class ConfigFileHandler(watchdog.events.FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('config/config.json'):
            global config
            config = load_config()
            logging.info('Configuration reloaded due to changes in config.json')

def start_config_watcher():
    """Start watching the configuration file for changes."""
    observer = watchdog.observers.Observer()
    observer.schedule(ConfigFileHandler(), path=os.path.dirname(__file__), recursive=False)
    observer.start()
    return observer

if __name__ == "__main__":
    # Start watching the config file for changes
    config_watcher = start_config_watcher()

    user_input_username = input("Enter your username: ")
    user_input_password = input("Enter your password: ")

    if authenticate_user(user_input_username, user_input_password):
        print("Authentication successful!")
        is_active, expiry_date = check_subscription_status()

        if is_active:
            print(f"Your subscription is active until {expiry_date.date()}.")
            display_user_info(user_input_username, "Standard", expiry_date)  # Adjust as needed

            # Load data and send SMS
            sms_phone_numbers, smtp_phone_numbers, messages = load_data()
            message_to_send = messages[0] if messages else "Default message"

            # Sending messages using available services
            if ENABLE_TWILIO:
                for number in sms_phone_numbers:
                    send_sms_twilio(number, message_to_send)
                    time.sleep(SMTP_DELAY)

            if ENABLE_NEXMO:
                for number in sms_phone_numbers:
                    send_sms_nexmo(number, message_to_send)
                    time.sleep(SMTP_DELAY)

            if ENABLE_ONESIGNAL:
                for number in sms_phone_numbers:
                    send_sms_onesignal(number, message_to_send)
                    time.sleep(SMTP_DELAY)

            if ENABLE_SMTP:
                for number in smtp_phone_numbers:
                    send_sms_smtp(number, message_to_send)
                    time.sleep(SMTP_DELAY)

            if ENABLE_AWS_SNS:
                for number in sms_phone_numbers:
                    send_sms_aws(number, message_to_send)
                    time.sleep(SMTP_DELAY)

        else:
            print("Your subscription has expired. Please renew to continue.")
    else:
        print("Authentication failed.")

    # Clean up the observer
    config_watcher.stop()
    config_watcher.join()
    input("Press Enter to quit...")
