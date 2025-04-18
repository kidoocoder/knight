import logging
import asyncio
import threading
import os
from flask import Flask, render_template, request, jsonify
from pyrogram import idle
from bot import bot, user, start_pytgcalls
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "telegrammusicbot")

# Global variable to track bot status
bot_started = False
bot_thread = None

async def run_bot():
    """Main function to start both bot and user clients"""
    global bot_started
    try:
        await bot.start()
        logger.info("Bot started successfully!")
        
        await user.start()
        logger.info("User client started successfully!")
        
        # Start PyTgCalls client
        await start_pytgcalls()
        
        # Update bot status
        bot_started = True
        
        # Keep the script running
        await idle()
    except Exception as e:
        logger.error(f"Error starting clients: {e}")
        bot_started = False
    finally:
        # Ensure clients are properly stopped
        await bot.stop()
        await user.stop()
        bot_started = False

def start_bot_thread():
    """Start the bot in a separate thread"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_bot())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        loop.close()

@app.route('/')
def home():
    """Render home page"""
    global bot_started
    return render_template('index.html', bot_status=bot_started)

@app.route('/start_bot', methods=['POST'])
def start_bot():
    """Start the Telegram bot"""
    global bot_started, bot_thread
    
    if not bot_started and (bot_thread is None or not bot_thread.is_alive()):
        bot_thread = threading.Thread(target=start_bot_thread)
        bot_thread.daemon = True
        bot_thread.start()
        return jsonify({"status": "starting"})
    
    return jsonify({"status": "already_running" if bot_started else "starting"})

@app.route('/bot_status')
def bot_status():
    """Get the current bot status"""
    global bot_started
    return jsonify({"running": bot_started})

if __name__ == "__main__":
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)
