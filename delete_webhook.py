import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def delete_webhook():
    """Delete the webhook for the Telegram bot."""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("No TELEGRAM_BOT_TOKEN found in environment variables!")
        return
    
    url = f"https://api.telegram.org/bot{token}/deleteWebhook"
    
    try:
        response = requests.get(url)
        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200 and response.json().get('ok'):
            print("Webhook deleted successfully!")
        else:
            print("Failed to delete webhook.")
    
    except Exception as e:
        print(f"Exception occurred: {str(e)}")

if __name__ == "__main__":
    delete_webhook()