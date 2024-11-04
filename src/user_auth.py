from datetime import datetime
from .database import load_subscriber # Ensure correct import path

# Authenticate user
def authenticate_user(input_username, input_password):
    user_data = load_subscriber(input_username)
    if user_data and input_password == user_data[1]:  # Check password
        return True
    return False

# Check subscription status
def check_subscription_status(username):
    user_data = load_subscriber(username)
    if user_data:
        expiry_date = datetime.strptime(user_data[2], "%Y-%m-%d")
        if datetime.now() < expiry_date:
            return True, expiry_date  # Active subscription
    return False, None  # Expired or user not found

if __name__ == "__main__":
    # Example usage
    user_input_username = input("Enter your username: ")
    user_input_password = input("Enter your password: ")
    
    if authenticate_user(user_input_username, user_input_password):
        print("Authentication successful!")
        is_active, expiry_date = check_subscription_status(user_input_username)
        if is_active:
            print(f"Your subscription is active until {expiry_date.date()}.")
        else:
            print("Your subscription has expired.")
    else:
        print("Authentication failed. Please check your username and password.")
