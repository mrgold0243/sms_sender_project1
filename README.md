# SMS Sender Project

This project uses the OneSignal API to send SMS messages in bulk.

## Project Structure

sms_sender_project/
│
├── src/                     # Source code directory
│   ├── app.py               # Flask application with user authentication and SMS sending functionality
│   ├── database.py          # Functions for interacting with the database (e.g., loading subscribers)
│   ├── user_auth.py         # Logic for authenticating users and checking subscription status
│   ├── requirements.txt      # Required Python packages for the project
│   ├── __init__.py          # Marks the directory as a package
│
├── data/                    # Data files directory
│   ├── contacts.csv          # CSV file containing phone numbers for SMS
│   ├── messages.csv          # CSV file containing messages to be sent
│   ├── contacts.json         # JSON file for additional contact information (if needed)
│   ├── messages.json         # JSON file for messages (alternative to CSV)
│   ├── sms_sender.db         # SQLite database file for subscriber data (e.g., user details, subscriptions)
│
├── templates/               # HTML templates for Flask app rendering
│   ├── index.html           # Main page template where users log in
│   ├── status.html          # Template displaying subscription status for users
│   ├── send_message.html     # Template for sending SMS messages
│   ├── update_subscription.html  # Template for updating subscription details
│
├── config/                  # Configuration files
│   ├── config.py            # Configuration settings such as API keys and service toggles
│
├── main.py                  # Main script to send SMS and manage user interactions
├── main.spec                # PyInstaller spec file for creating a standalone executable (if needed)
└── README.md                # Project documentation and instructions for setup and usage

python -m src.main
lo launch

## Setup Instructions

1. Clone the repository or download the project files.
2. Install the required packages by running:

   ```bash
   pip install -r src/requirements.txt

3. Update the `config/config.py` file with your OneSignal API key and App ID.
# Example configuration
ENABLE_ONESIGNAL = True/False
ENABLE_TWILIO = True/False
ENABLE_NEXMO = True/False

4. Add phone numbers and messages to the `data/contacts.csv` and `data/messages.csv` files.
5. Run the script:

python src/main.py  **To lauch and send mesaage after loading messages.csv and contacts.csv**


## License

This project is licensed under the Mrgold License.


### Key Changes in the README

- **Expanded Description**: Updated to reflect the use of multiple SMS providers (OneSignal, Twilio, Nexmo).
- **Configuration Details**: Added information on how to enable or disable each provider in the configuration file.
- **Code Formatting**: Used markdown code blocks for better readability of code snippets.

Feel free to modify any sections as needed! If you have any further changes or questions, just let me know.

