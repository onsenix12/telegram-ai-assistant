import os
import json
import logging
from datetime import datetime
from flask import Flask, request, redirect, url_for, session, render_template, jsonify
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import requests
from pymongo import MongoClient
from bson.json_util import dumps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev_secret_key')

# Set the server name (domain) for generating external URLs
SERVER_NAME = os.getenv('SERVER_NAME')
if SERVER_NAME:
    app.config['SERVER_NAME'] = SERVER_NAME
    logger.info(f"Using server name: {SERVER_NAME} for generating external URLs")

# MongoDB connection
mongo_uri = os.getenv('MONGO_URI', 'mongodb://mongo:27017/')
# In-memory fallback
authenticated_users = {}

try:
    # Use connect=False so it will only connect when actually needed
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    # Test the connection
    client.admin.command('ping')
    db = client.get_database('auth_service')
    users_collection = db.get_collection('authenticated_users')
    logger.info(f"Connected to MongoDB successfully at {mongo_uri}")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    logger.warning("Falling back to in-memory storage - user data will not persist!")
    # Set client to None to indicate MongoDB is not available
    client = None

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

# Load the secret key from the environment variable
AUTH_SECRET_KEY = os.getenv('AUTH_SECRET_KEY')

# Database operations
def save_authenticated_user(telegram_id, user_info):
    """Save user authentication data to persistent storage"""
    try:
        if client is not None:  # Check if MongoDB is available
            # Add telegram_id to the user info
            user_data = {
                'telegram_id': telegram_id,
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'authenticated_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            
            users_collection.update_one(
                {'telegram_id': telegram_id},
                {'$set': user_data},
                upsert=True
            )
            logger.info(f"User {telegram_id} saved to MongoDB")
        else:
            # Fallback to in-memory storage
            authenticated_users[telegram_id] = {
                'telegram_id': telegram_id,
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'authenticated_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            logger.info(f"User {telegram_id} saved to in-memory storage")
    except Exception as e:
        logger.error(f"Error saving user {telegram_id}: {str(e)}")
        # Fallback to in-memory as last resort
        authenticated_users[telegram_id] = {
            'telegram_id': telegram_id,
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'authenticated_at': datetime.now().isoformat()
        }

def get_authenticated_user(telegram_id):
    """Get user authentication data from persistent storage"""
    try:
        if client is not None:  # Check if MongoDB is available
            logger.debug(f"Looking for user {telegram_id} in MongoDB")
            user = users_collection.find_one({'telegram_id': telegram_id})
            if user:
                # Convert ObjectId to string for JSON serialization
                user['_id'] = str(user['_id'])
                logger.debug(f"Found user {telegram_id} in MongoDB")
                return user
            logger.debug(f"User {telegram_id} not found in MongoDB")
            return None
        else:
            # Fallback to in-memory storage
            logger.debug(f"Looking for user {telegram_id} in memory")
            return authenticated_users.get(telegram_id)
    except Exception as e:
        logger.error(f"Error retrieving user {telegram_id}: {str(e)}")
        # Fallback to in-memory as last resort
        return authenticated_users.get(telegram_id)

def authenticate(request):
    """Authenticate API requests using bearer token"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header == f"Bearer {AUTH_SECRET_KEY}":
        return True
    return False

@app.route('/')
def index():
    """Root endpoint with basic status information"""
    try:
        mongo_status = "Connected" if 'client' in globals() else "Not connected"
        oauth_status = "Configured" if os.getenv('GOOGLE_CLIENT_ID') else "Not configured"
        
        return render_template('index.html', 
                              mongo_status=mongo_status,
                              oauth_status=oauth_status)
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return 'Authentication Service - Status: Running with errors'

@app.route('/login/<telegram_id>')
def login(telegram_id):
    """Initiate OAuth flow for the given Telegram user ID"""
    try:
        logger.info(f"Login attempt for telegram_id: {telegram_id}")
        # Store the telegram ID in the session
        session['telegram_id'] = telegram_id
        
        # Get the external domain from environment variable
        external_domain = os.getenv('EXTERNAL_DOMAIN')
        
        # Redirect to Google for authentication
        if external_domain:
            # Use explicit external domain
            base_url = f"http://{external_domain}"
            redirect_uri = f"{base_url}/callback"
            logger.info(f"Using external domain for callback: {redirect_uri}")
        else:
            # Fall back to Flask's url_for
            redirect_uri = url_for('callback', _external=True)
            logger.info(f"Using default callback URL: {redirect_uri}")
            
        logger.info(f"Redirecting to Google OAuth with callback URL: {redirect_uri}")
        return google.authorize_redirect(redirect_uri)
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return render_template('error.html', 
                              message=f"Login error: {str(e)}",
                              details="There was a problem connecting to Google authentication.")

@app.route('/callback')
def callback():
    """Handle OAuth callback from Google"""
    try:
        logger.info("Received callback from Google OAuth")
        # Get the access token
        token = google.authorize_access_token()
        # Get user info
        resp = google.get('userinfo')
        user_info = resp.json()
        
        # Check if the email is from smu.edu.sg domain
        email = user_info.get('email', '')
        logger.info(f"User authenticated with email: {email}")
        
        if not email.endswith('@smu.edu.sg'):
            logger.warning(f"Authentication failed: Email {email} is not from SMU domain")
            return render_template('error.html', 
                                  message="Authentication failed. Please use your SMU email address.",
                                  details="Only email addresses ending with @smu.edu.sg are allowed.")
        
        # Get telegram ID from session
        telegram_id = session.get('telegram_id')
        if telegram_id:
            # Store authenticated user
            user_data = {
                'email': email,
                'name': user_info.get('name'),
                'authenticated_at': datetime.now().isoformat()
            }
            save_authenticated_user(telegram_id, user_data)
            
            logger.info(f"User {telegram_id} authenticated successfully with email {email}")
            return render_template('success.html', 
                                  message="Authentication successful! You can now use the Telegram bot.")
        else:
            logger.error("Callback received without telegram_id in session")
            return render_template('error.html', 
                                  message="Invalid session. Please try again.",
                                  details="The session may have expired. Please restart the authentication process from Telegram.")
    
    except Exception as e:
        logger.error(f"Callback error: {str(e)}")
        return render_template('error.html', 
                              message="Authentication error occurred.",
                              details=f"Error details: {str(e)}")

@app.route('/verify/<telegram_id>')
def verify(telegram_id):
    """API endpoint to check if a user is authenticated"""
    try:
        logger.info(f"Verification request for user {telegram_id}")
        user = get_authenticated_user(telegram_id)
        is_authenticated = user is not None
        
        # Log the result
        if is_authenticated:
            logger.info(f"User {telegram_id} is authenticated with email {user.get('email', 'unknown')}")
        else:
            logger.info(f"User {telegram_id} is not authenticated")
        
        # Use BSON serialization for MongoDB objects
        if client is not None and user:
            return dumps({
                'authenticated': is_authenticated,
                'user_info': user
            })
        else:
            # Regular JSON for in-memory storage or no user
            return json.dumps({
                'authenticated': is_authenticated,
                'user_info': user
            })
    except Exception as e:
        logger.error(f"Error verifying user {telegram_id}: {str(e)}")
        return json.dumps({
            'authenticated': False,
            'error': str(e)
        })
    
@app.route('/dev/add_test_user/<telegram_id>', methods=['POST'])
def add_test_user(telegram_id):
    """Development endpoint for adding test users (do not use in production)"""
    # Only allow in development environment
    if os.getenv('FLASK_ENV') == 'production':
        logger.warning(f"Attempt to use development endpoint in production mode")
        return jsonify({"error": "This endpoint is not available in production"}), 403
    
    try:
        logger.info(f"Adding test user for {telegram_id}")
        # Get user data from request
        user_data = request.json
        
        if not user_data:
            return jsonify({"error": "No user data provided"}), 400
        
        # Add user to authenticated users
        user_info = {
            'email': user_data.get('email', 'test.user@smu.edu.sg'),
            'name': user_data.get('name', 'Test User'),
            'authenticated_at': datetime.now().isoformat()
        }
        
        save_authenticated_user(telegram_id, user_info)
        
        # Get the user that was just saved to return in response
        saved_user = get_authenticated_user(telegram_id)
        
        return jsonify({
            "success": True,
            "message": f"Test user {telegram_id} added successfully",
            "user": saved_user
        }), 201
    except Exception as e:
        logger.error(f"Error adding test user {telegram_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/protected', methods=['GET'])
def protected():
    """Protected API endpoint that requires authentication"""
    if authenticate(request):
        return jsonify({"message": "Authenticated successfully!"}), 200
    else:
        return jsonify({"message": "Authentication failed!"}), 401

@app.route('/status', methods=['GET'])
def status():
    """Health check endpoint"""
    # Count authenticated users
    user_count = 0
    mongo_status = "disconnected"
    
    try:
        if client is not None:
            # Test MongoDB connection
            client.admin.command('ping')
            mongo_status = "connected"
            # Count users in MongoDB
            user_count = users_collection.count_documents({})
        else:
            # Count users in memory
            user_count = len(authenticated_users)
    except Exception as e:
        logger.error(f"Error in status endpoint: {str(e)}")
        mongo_status = f"error: {str(e)}"
    
    status_info = {
        "service": "auth-service",
        "status": "running",
        "version": "1.0",
        "mongo_status": mongo_status,
        "mongo_uri": os.getenv('MONGO_URI', 'not set'),
        "oauth_configured": bool(os.getenv('GOOGLE_CLIENT_ID') and os.getenv('GOOGLE_CLIENT_SECRET')),
        "authenticated_users": user_count,
        "timestamp": datetime.now().isoformat()
    }
    return jsonify(status_info)

if __name__ == '__main__':
    # Verify environment variables
    required_vars = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'SECRET_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Auth service cannot start properly without these variables")
    
    # Check MongoDB connection
    if client is not None:
        try:
            # Try a ping to verify connection
            client.admin.command('ping')
            # Initialize the collection with an index on telegram_id if it doesn't exist
            users_collection.create_index('telegram_id', unique=True)
            logger.info("Successfully connected to MongoDB and initialized collections")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            logger.error("User authentication data will not persist between restarts!")
            client = None
    else:
        logger.warning("MongoDB connection not available. Using in-memory storage only.")
    
    # Print the callback URL for debugging
    with app.test_request_context():
        callback_url = url_for('callback', _external=True)
        logger.info(f"Callback URL: {callback_url}")
        logger.info("Ensure this URL is added to your Google OAuth authorized redirect URIs")
    
    logger.info("Starting auth service on port 5050")
    app.run(host='0.0.0.0', port=5050)