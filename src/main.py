# Updated src/main.py content
import os
import logging
import threading
import time
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from src.nlp.context_manager import ContextManager
from src.dialog.conversation_handler import ConversationHandler
from src.tracking.progress_tracker import ProgressTracker
from src.admin.dashboard import Dashboard
from src.admin.system_monitor import SystemMonitor
from src.admin.faq.faq_manager import FAQManager
from src.integrations.elearn.synchronizer import ELearnSynchronizer
from src.error.error_handler import ErrorHandler
from src.error.logger import get_logger
from src.monitoring.metrics import MetricsCollector
from src.monitoring.alerts import AlertManager

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__, log_dir='logs')

# Global components
context_manager = ContextManager()
conversation_handler = ConversationHandler()
progress_tracker = ProgressTracker()
dashboard = Dashboard()
system_monitor = SystemMonitor()
faq_manager = FAQManager()
elearn_synchronizer = ELearnSynchronizer(dummy_mode=True)
error_handler = ErrorHandler()
metrics_collector = MetricsCollector()
alert_manager = AlertManager(metrics_collector)

# Get telegram token from environment variable
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    logger.error("No TELEGRAM_BOT_TOKEN found in environment variables!")
    exit(1)

def start_command(update: Update, context: CallbackContext) -> None:
    """Send a welcome message when the command /start is issued."""
    try:
        # Start measuring response time
        start_time = time.time()
        
        user = update.effective_user
        user_id = str(user.id)
        
        # Record user activity
        metrics_collector.record_user_activity(user_id)
        
        # Send welcome message
        response = f"Hi {user.first_name}! I am the SMU Master's Program AI Learning Assistant. I can help you with course information, assignments, and learning materials. Type /help to see what I can do."
        update.message.reply_text(response)
        
        # Record message
        metrics_collector.record_message('bot')
        
        # Record response time
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        metrics_collector.record_response_time('start_command', duration_ms)
    except Exception as e:
        # Handle error
        error_message = error_handler.handle_error(e, 'default', {'command': 'start'})
        update.message.reply_text(error_message)
        
        # Record error
        metrics_collector.record_error('command_error')

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    try:
        # Start measuring response time
        start_time = time.time()
        
        user = update.effective_user
        user_id = str(user.id)
        
        # Record user activity
        metrics_collector.record_user_activity(user_id)
        
        # Send help message
        response = (
            "I can help you with your SMU Master's Program courses. Here's what you can ask me:\n\n"
            "- Course information (e.g., 'Tell me about IS621')\n"
            "- Assignments and deadlines (e.g., 'What are the assignments for IS621?')\n"
            "- Learning materials (e.g., 'Show me learning materials for IS621')\n"
            "- Course schedule (e.g., 'When is the next IS621 class?')\n"
            "- Track your progress (e.g., 'Show my learning progress')\n\n"
            "Type your question and I'll do my best to help!"
        )
        update.message.reply_text(response)
        
        # Record message
        metrics_collector.record_message('bot')
        
        # Record response time
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        metrics_collector.record_response_time('help_command', duration_ms)
    except Exception as e:
        # Handle error
        error_message = error_handler.handle_error(e, 'default', {'command': 'help'})
        update.message.reply_text(error_message)
        
        # Record error
        metrics_collector.record_error('command_error')

def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle incoming messages."""
    try:
        user_id = update.effective_user.id
        message_text = update.message.text
        intents = conversation_handler.intent_classifier.classify(message_text)
        intent = intents[0] if intents else "unknown_intent"
        dashboard.update_counters(user_id, message_text, intent)
        response = conversation_handler.process_message(user_id, message_text)
        update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        error_handler.handle_error(e)

def sync_command(update: Update, context: CallbackContext) -> None:
    """Sync course data from E-Learn."""
    try:
        # Verify if user is admin
        user = update.effective_user
        user_id = str(user.id)
        
        # TODO: Implement proper admin verification
        # For now, just allow any user to trigger sync
        
        # Get course code from arguments
        args = context.args
        if args and len(args) > 0:
            course_code = args[0].upper()
            update.message.reply_text(f"Syncing course {course_code}. This may take a few moments...")
            
            # Sync course in background thread
            threading.Thread(
                target=_sync_course_background,
                args=(update, course_code)
            ).start()
        else:
            update.message.reply_text(f"Syncing all courses. This may take a few moments...")
            
            # Sync all courses in background thread
            threading.Thread(
                target=_sync_all_background,
                args=(update,)
            ).start()
    except Exception as e:
        # Handle error
        error_message = error_handler.handle_error(e, 'default', {'command': 'sync'})
        update.message.reply_text(error_message)
        
        # Record error
        metrics_collector.record_error('command_error')

def _sync_course_background(update: Update, course_code: str) -> None:
    """Sync a course in the background."""
    try:
        # Sync course
        result = elearn_synchronizer.sync_course(course_code)
        
        # Send result
        if result["course_synced"]:
            update.message.reply_text(
                f"Course {course_code} synced successfully:\n"
                f"- Materials: {result['materials_synced']}\n"
                f"- Assignments: {result['assignments_synced']}\n"
                f"- Schedule: {result['schedule_synced']}"
            )
        else:
            errors = "\n".join([f"- {e['error']}" for e in result["errors"]])
            update.message.reply_text(
                f"Failed to sync course {course_code}:\n{errors}"
            )
    except Exception as e:
        logger.error(f"Error in background sync: {str(e)}")
        update.message.reply_text(f"An error occurred during sync: {str(e)}")

def _sync_all_background(update: Update) -> None:
    """Sync all courses in the background."""
    try:
        # Sync all courses
        result = elearn_synchronizer.sync_all()
        
        # Send result
        update.message.reply_text(
            f"All courses synced successfully:\n"
            f"- Courses: {result['courses_synced']}\n"
            f"- Materials: {result['materials_synced']}\n"
            f"- Assignments: {result['assignments_synced']}\n"
            f"- Schedule: {result['schedule_synced']}"
        )
        
        if result["errors"]:
            errors = "\n".join([f"- {e['course']}: {e['error']}" for e in result["errors"]])
            update.message.reply_text(
                f"Errors during sync:\n{errors}"
            )
    except Exception as e:
        logger.error(f"Error in background sync: {str(e)}")
        update.message.reply_text(f"An error occurred during sync: {str(e)}")

def stats_command(update: Update, context: CallbackContext) -> None:
    """Show bot statistics."""
    try:
        # Get statistics
        usage_stats = dashboard.get_usage_statistics()
        metrics_summary = metrics_collector.get_metrics_summary()
        
        # Send statistics
        update.message.reply_text(
            f"Bot Statistics:\n\n"
            f"Usage:\n"
            f"- Total Messages: {usage_stats['message_count']}\n"
            f"- Total Users: {usage_stats['user_count']}\n"
            f"- Active Users Today: {metrics_summary['active_users_today']}\n\n"
            f"Performance:\n"
            f"- Average Response Time: {metrics_summary['average_response_time_ms']:.2f} ms\n"
            f"- Error Rate: {metrics_summary['error_rate'] * 100:.2f}%\n"
        )
    except Exception as e:
        # Handle error
        error_message = error_handler.handle_error(e, 'default', {'command': 'stats'})
        update.message.reply_text(error_message)
        
        # Record error
        metrics_collector.record_error('command_error')
        
def login_command(update: Update, context: CallbackContext) -> None:
    """Send authentication link to the user."""
    try:
        user = update.effective_user
        user_id = str(user.id)
        
        # Record user activity
        metrics_collector.record_user_activity(user_id)
        
        # Check if the user is already authenticated
        import requests
        try:
            # Try with the Docker network name first
            response = requests.get(f"http://auth-service:5050/verify/{user_id}", timeout=3)
        except requests.exceptions.RequestException:
            # Fall back to localhost
            response = requests.get(f"http://localhost:5050/verify/{user_id}", timeout=3)
            
        if response.status_code == 200:
            data = response.json()
            if data.get('authenticated', False):
                # User is already authenticated
                update.message.reply_text(
                    "You are already authenticated. You can continue using the bot."
                )
                return
        
        # Generate authentication link using public-facing domain
        # First try to get the external auth URL
        external_domain = os.getenv('EXTERNAL_DOMAIN')
        if external_domain:
            auth_link = f"http://{external_domain}/login/{user_id}"
            logger.info(f"Using external domain for auth link: {auth_link}")
        else:
            # Fall back to AUTH_SERVICE_URL
            auth_base_url = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5050')
            auth_link = f"{auth_base_url}/login/{user_id}"
            logger.info(f"Using AUTH_SERVICE_URL for auth link: {auth_link}")
        
        # Send authentication link
        update.message.reply_text(
            "Please authenticate using your SMU email address by clicking the link below:\n\n"
            f"{auth_link}\n\n"
            "You need to authenticate to use the full features of this bot."
        )
        
    except Exception as e:
        logger.error(f"Error in login command: {str(e)}")
        # Handle error
        error_message = error_handler.handle_error(e, 'default', {'command': 'login'})
        update.message.reply_text(error_message)
        
        # Record error
        metrics_collector.record_error('command_error')

def progress_command(update: Update, context: CallbackContext) -> None:
    """Show user's learning progress."""
    try:
        user = update.effective_user
        user_id = str(user.id)
        
        # Get progress data
        progress = progress_tracker.get_user_progress(user_id)
        
        if not progress:
            update.message.reply_text("You haven't interacted with any courses yet.")
            return
        
        # Format progress message
        message = f"Your Learning Progress:\n\n"
        
        for course_code, data in progress.items():
            topic_count = len(data.get('topics', {}))
            interaction_count = len(data.get('interactions', []))
            
            message += f"{course_code}:\n"
            message += f"- Topics Explored: {topic_count}\n"
            message += f"- Total Interactions: {interaction_count}\n"
            
            # Get active topics
            active_topics = progress_tracker.get_active_topics(user_id, course_code, limit=3)
            if active_topics:
                message += "- Most Active Topics:\n"
                for topic in active_topics:
                    message += f"  • {topic['name']} ({topic['interaction_count']} interactions)\n"
            
            message += "\n"
        
        update.message.reply_text(message)
    except Exception as e:
        # Handle error
        error_message = error_handler.handle_error(e, 'default', {'command': 'progress'})
        update.message.reply_text(error_message)
        
        # Record error
        metrics_collector.record_error('command_error')

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("sync", sync_command))
    dispatcher.add_handler(CommandHandler("stats", stats_command))
    dispatcher.add_handler(CommandHandler("progress", progress_command))
    dispatcher.add_handler(CommandHandler("login", login_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start the Bot
    updater.start_polling()
    logger.info("Bot started!")
    
    # Start alert monitoring
    alert_manager.start_monitoring()
    logger.info("Alert monitoring started!")

    # Run the bot until you press Ctrl-C
    updater.idle()
    
    # Stop alert monitoring
    alert_manager.stop_monitoring()

if __name__ == '__main__':
    main()