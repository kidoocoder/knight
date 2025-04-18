import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for bot settings"""
    
    # Telegram API credentials
    API_ID = int(os.getenv("API_ID", "0"))
    API_HASH = os.getenv("API_HASH", "")
    
    # Bot token from @BotFather
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    
    # Pyrogram string session for the user account
    # This is needed because bots can't join voice chats
    SESSION_STRING = os.getenv("SESSION_STRING", "")
    
    # Prefixes for commands (optional)
    COMMAND_PREFIXES = list(os.getenv("COMMAND_PREFIXES", "! / .").split())
    
    # Sudo users who can use admin commands (optional)
    SUDO_USERS = list(map(int, os.getenv("SUDO_USERS", "").split()))
    
    # Maximum number of songs in queue
    MAX_QUEUE_SIZE = int(os.getenv("MAX_QUEUE_SIZE", "10"))
    
    # Default language for song searches
    DEFAULT_LANG = os.getenv("DEFAULT_LANG", "en")
    
    # Temporary directory for audio files
    TEMP_DOWNLOAD_DIRECTORY = os.getenv("TEMP_DOWNLOAD_DIRECTORY", "./downloads/")
    
    # Create temp directory if it doesn't exist
    if not os.path.isdir(TEMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TEMP_DOWNLOAD_DIRECTORY)
