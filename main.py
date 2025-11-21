import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Bot configuration - DIRECT TOKEN
BOT_TOKEN = "7895976628:AAHKxnXhuDVSRl689E_wYY7gybS-u-oVX9k"
FLUX_API_URL = "https://flux-pro.vercel.app/generate?q="

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    """Send welcome message when the command /start is issued."""
    welcome_text = """
    🎨 Welcome to Flux Image Generator Bot!
    
    I can generate images from your text prompts.
    
    How to use:
    Simply type any prompt like:
    - black cat
    - beautiful sunset 
    - futuristic city
    
    And I'll generate an image for you!
    """
    await update.message.reply_text(welcome_text)

async def generate_image(update: Update, context: CallbackContext) -> None:
    """Generate image from user's text prompt."""
    user_message = update.message.text
    
    if not user_message or user_message.strip() == "":
        await update.message.reply_text("❌ Please provide a prompt. Example: black cat")
        return
    
    try:
        # Show typing action
        await update.message.chat.send_action(action="upload_photo")
        
        # Prepare the API URL with user's prompt
        prompt = user_message.strip()
        api_url = f"{FLUX_API_URL}{requests.utils.quote(prompt)}"
        
        # Send request to Flux API
        response = requests.get(api_url, stream=True)
        
        if response.status_code == 200:
            # Save the image temporarily
            with open("generated_image.jpg", "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            
            # Send the image back to user
            with open("generated_image.jpg", "rb") as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=f"🖼️ Generated image for: {prompt}"
                )
            
            logger.info(f"Image generated successfully for prompt: {prompt}")
            
        else:
            await update.message.reply_text("❌ Sorry, image generation failed. Please try again later.")
            logger.error(f"API request failed with status code: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        await update.message.reply_text("❌ Network error. Please try again later.")
        logger.error(f"Request error: {e}")
    
    except Exception as e:
        await update.message.reply_text("❌ An error occurred. Please try again.")
        logger.error(f"Unexpected error: {e}")

async def help_command(update: Update, context: CallbackContext) -> None:
    """Send help message when the command /help is issued."""
    help_text = """
    🤖 Flux Image Generator Bot Help
    
    Commands:
    /start - Start the bot and see welcome message
    /help - Show this help message
    
    How to generate images:
    Simply type any text prompt and I'll generate an image for you!
    
    Examples:
    - cute puppy playing in garden
    - abstract art with blue colors 
    - landscape of mountains
    
    Note: Image generation may take a few seconds.
    """
    await update.message.reply_text(help_text)

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_image))

    # Start the Bot
    print("🤖 Bot is running...")
    application.run_polling()
    print("Bot stopped.")

if __name__ == '__main__':
    main()
