import os
import sys

# Check if required modules are installed
try:
    import pyrogram
    print("Pyrogram installed:", pyrogram.__version__)
except ImportError:
    print("Pyrogram not installed")

try:
    from pytgcalls import PyTgCalls
    # PyTgCalls class might not have the __version__ attribute
    import pytgcalls
    version = getattr(pytgcalls, "__version__", "unknown version")
    print("PyTgCalls installed:", version)
except ImportError:
    print("PyTgCalls not installed")

try:
    import yt_dlp
    print("yt-dlp installed:", yt_dlp.version.__version__)
except ImportError:
    print("yt-dlp not installed")

try:
    from dotenv import load_dotenv
    print("python-dotenv installed")
except ImportError:
    print("python-dotenv not installed")

# Analyze bot structure
if os.path.exists("bot.py"):
    with open("bot.py", "r") as f:
        code = f.read()
        print("\nBot Structure Analysis:")
        print("-" * 20)
        print("Main Client Setup:", "bot" in code and "user" in code)
        print("Command Handlers:", "on_message" in code)
        print("Callback Handlers:", "on_callback_query" in code)
        print("Stream Functions:", "start_streaming" in code)
else:
    print("\nCannot find bot.py file")

# Print all installed packages
print("\nAll installed packages:")
print("-" * 20)
os.system("pip list")