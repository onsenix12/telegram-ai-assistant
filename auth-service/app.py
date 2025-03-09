import os
import json
from datetime import datetime
from flask import Flask, request, redirect, url_for, session, render_template, jsonify
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev_secret_key')

# Setup OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
)

# In-memory storage for authenticated users (replace with database in production)
authenticated_users = {}

# Load the secret key from the environment variable
AUTH_SECRET_KEY = os.getenv('AUTH_SECRET_KEY')

def authenticate(request):
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header == f"Bearer {AUTH_SECRET_KEY}":
        return True
    return False

@app.route('/')
def index():
    return 'Authentication Service'

@app.route('/login/<telegram_id>')
def login(telegram_id):
    # Store the telegram ID in the session
    session['telegram_id'] = telegram_id
    # Redirect to Google for authentication
    redirect_uri = url_for('callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/callback')
def callback():
    # Get the access token
    token = google.authorize_access_token()
    # Get user info
    resp = google.get('userinfo')
    user_info = resp.json()
    
    # Check if the email is from smu.edu.sg domain
    email = user_info.get('email', '')
    if not email.endswith('@smu.edu.sg'):
        return render_template('error.html', 
                              message="Authentication failed. Please use your SMU email address.")
    
    # Get telegram ID from session
    telegram_id = session.get('telegram_id')
    if telegram_id:
        # Store authenticated user
        authenticated_users[telegram_id] = {
            'email': email,
            'name': user_info.get('name'),
            'authenticated_at': datetime.now().isoformat()
        }
        
        # In production, save to database instead
        # Also notify the bot about successful authentication
        
        return render_template('success.html', 
                              message="Authentication successful! You can now use the Telegram bot.")
    
    return 'Invalid session. Please try again.'

@app.route('/verify/<telegram_id>')
def verify(telegram_id):
    """API endpoint to check if a user is authenticated"""
    is_authenticated = telegram_id in authenticated_users
    return json.dumps({
        'authenticated': is_authenticated,
        'user_info': authenticated_users.get(telegram_id)
    })
    
@app.route('/dev/add_test_user/<telegram_id>', methods=['POST'])
def add_test_user(telegram_id):
    """Development endpoint for adding test users (do not use in production)"""
    # Only allow in development environment
    if os.getenv('FLASK_ENV') == 'production':
        return jsonify({"error": "This endpoint is not available in production"}), 403
    
    try:
        # Get user data from request
        user_data = request.json
        
        if not user_data:
            return jsonify({"error": "No user data provided"}), 400
        
        # Add user to authenticated users
        authenticated_users[telegram_id] = {
            'email': user_data.get('email', 'test.user@smu.edu.sg'),
            'name': user_data.get('name', 'Test User'),
            'authenticated_at': datetime.now().isoformat()
        }
        
        return jsonify({
            "success": True,
            "message": f"Test user {telegram_id} added successfully",
            "user": authenticated_users[telegram_id]
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/protected', methods=['GET'])
def protected():
    if authenticate(request):
        return jsonify({"message": "Authenticated successfully!"}), 200
    else:
        return jsonify({"message": "Authentication failed!"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)  # Using port 5050 to match docker-compose