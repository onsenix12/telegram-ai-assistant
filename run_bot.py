import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from src.nlp.Multi_part_Question_Handler import MultiPartQuestionHandler
from src.models import User, Interaction

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize components
multi_part_handler = MultiPartQuestionHandler(use_claude=True)

# Get telegram token from environment variable
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    logger.error("No TELEGRAM_BOT_TOKEN found in environment variables!")
    exit(1)

# Check if Claude API is available
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
if not ANTHROPIC_API_KEY:
    logger.warning("No ANTHROPIC_API_KEY found in environment variables! Complex questions will use fallback responses.")

def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message when the command /start is issued."""
    user = update.effective_user
    
    # Create user model
    user_model = User(
        user_id=str(user.id),
        first_name=user.first_name,
        username=user.username
    )
    
    # Store user in context
    context.user_data['user_model'] = user_model
    
    welcome_message = (
        f"Hi {user.first_name}! I am the SMU Master's Program AI Learning Assistant.\n\n"
        f"I can help you with:\n"
        f"- Course information for IS621-IS625\n"
        f"- Assignment details and deadlines\n"
        f"- Learning materials and resources\n"
        f"- Answering complex, multi-part questions about your studies\n\n"
        f"What would you like to know about your SMU Master's program today?"
    )
    
    update.message.reply_text(welcome_message)

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    help_message = (
        "I can help with your SMU Master's classes in several ways:\n\n"
        "1. Ask about specific courses by code (e.g., 'Tell me about IS623')\n"
        "2. Get assignment details (e.g., 'What are the assignments for IS624?')\n"
        "3. Find learning materials (e.g., 'Where can I find resources for IS625?')\n"
        "4. Ask complex, multi-part questions (e.g., 'Compare the assignments for IS623 and IS624')\n\n"
        "The more specific your question, the better I can help you!"
    )
    
    update.message.reply_text(help_message)

def process_message(update: Update, context: CallbackContext) -> None:
    """Process user messages using multi-part question handler."""
    try:
        user = update.effective_user
        user_id = str(user.id)
        message_text = update.message.text
        
        # Get or create user model
        user_model = context.user_data.get('user_model')
        if not user_model:
            user_model = User(
                user_id=user_id,
                first_name=user.first_name,
                username=user.username
            )
            context.user_data['user_model'] = user_model
        
        # Log the incoming message
        logger.info(f"Received message from {user.first_name} ({user_id}): {message_text}")
        
        try:
            # Use multi-part question handler to process message
            logger.info("Calling multi_part_handler.process_message")
            response = multi_part_handler.process_message(user_id, message_text)
            logger.info(f"Got response: {response[:50]}..." if len(response) > 50 else f"Got response: {response}")
        except Exception as e:
            logger.error(f"Error in process_message: {str(e)}")
            response = "I'm having trouble processing your message. Please try again."
        
        # Store interaction for analytics
        intent = "unknown"
        entities = {}
        
        # Get intent and entities from context if available
        try:
            context_data = multi_part_handler.context_manager.get_context(user_id) or {}
            if context_data:
                intent = context_data.get('last_intent', 'unknown')
                entities = context_data.get('last_entities', {})
        except Exception as e:
            logger.error(f"Error getting context: {str(e)}")
        
        # Create interaction model
        interaction = Interaction(
            user_id=user_id,
            message=message_text,
            intent=intent,
            entities=entities
        )
        
        # Log the interaction
        logger.info(f"Interaction: {interaction.to_dict()}")
        
        # Send response to the user
        try:
            logger.info("Sending response to user")
            update.message.reply_text(response)
            logger.info("Response sent successfully")
        except Exception as e:
            logger.error(f"Error sending response: {str(e)}")
    except Exception as e:
        logger.error(f"Unhandled exception in process_message: {str(e)}")
        try:
            update.message.reply_text("Sorry, I encountered an unexpected error. Please try again later.")
        except:
            logger.error("Could not send error message to user")

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_message))

    # Start the Bot
    updater.start_polling()
    logger.info("Bot started!")
    
    if not ANTHROPIC_API_KEY:
        logger.warning("Running without Claude AI integration. Complex questions will use fallback responses.")
    else:
        logger.info("Claude AI integration enabled for complex questions.")

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()