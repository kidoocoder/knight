import os
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import StreamEnded

# Import custom exceptions
class NoActiveGroupCall(Exception):
    pass

from config import Config
from helpers.youtube import search_youtube, get_youtube_stream
from helpers.queue_manager import QueueManager
from helpers.stream_helper import leave_call, change_stream, start_stream

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
bot = Client(
    "MusicBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

# User client (needed to join voice chat)
user = Client(
    "UserBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    session_string=Config.SESSION_STRING
)

# Initialize PyTgCalls client
call_py = PyTgCalls(user)

# Queue manager for each chat
queue_manager = QueueManager()

# Helper function to create a basic info panel
def create_info_panel():
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 Commands", callback_data="cmd_help"),
            InlineKeyboardButton("🔄 Update", callback_data="refresh")
        ]
    ])
    return buttons

# Start command
@bot.on_message(filters.command("start") & filters.private)
async def start_command(_, message: Message):
    await message.reply_text(
        "👋 **Hello! I'm a Telegram Music Bot**\n\n"
        "I can play YouTube audio in voice chats. "
        "Add me to a group and use /help to see available commands.",
        reply_markup=create_info_panel()
    )

# Help command
@bot.on_message(filters.command("help"))
async def help_command(_, message: Message):
    help_text = (
        "🎵 **Available Commands:**\n\n"
        "• `/play` - Play a song by name or YouTube URL\n"
        "• `/search` - Search for a song on YouTube\n"
        "• `/skip` - Skip to the next song\n"
        "• `/stop` - Stop playing and clear queue\n"
        "• `/queue` - Show current queue\n"
        "• `/pause` - Pause the current song\n"
        "• `/resume` - Resume the paused song\n"
        "• `/ping` - Check bot's response time\n\n"
        "➡️ Add a song name or YouTube URL after commands like `/play`"
    )
    await message.reply_text(help_text)

# Ping command
@bot.on_message(filters.command("ping"))
async def ping_command(_, message: Message):
    start_time = asyncio.get_event_loop().time()
    m = await message.reply_text("🏓 Pinging...")
    end_time = asyncio.get_event_loop().time()
    ping_time = round((end_time - start_time) * 1000, 2)
    
    await m.edit(f"🏓 **Pong!** `{ping_time}ms`")

# Play command
@bot.on_message(filters.command("play"))
async def play_command(_, message: Message):
    chat_id = message.chat.id
    
    # Check if there's any text after the command
    if len(message.command) < 2:
        await message.reply_text("❌ Please provide a song name or YouTube URL after the command.")
        return
    
    query = " ".join(message.command[1:])
    m = await message.reply_text(f"🔍 Searching for: **{query}**")
    
    try:
        # Search for the song
        results = await search_youtube(query)
        if not results:
            await m.edit("❌ No results found. Try a different search term.")
            return
        
        # Get the first result
        result = results[0]
        title = result['title']
        duration = result['duration']
        thumbnail = result['thumbnail']
        video_id = result['id']
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Add to queue
        position = queue_manager.add_to_queue(chat_id, {
            'title': title,
            'url': url,
            'requested_by': message.from_user.mention() if message.from_user else "Anonymous"
        })
        
        # If it's the first song in queue, start playing
        if position == 1:
            await m.edit(f"🎵 **Starting to play:**\n**{title}**\n\n⏱ Duration: `{duration}`")
            await start_streaming(chat_id, url, m)
        else:
            await m.edit(f"🎵 **Added to queue at position #{position}:**\n**{title}**\n\n⏱ Duration: `{duration}`")
    
    except Exception as e:
        logger.error(f"Error playing song: {e}")
        await m.edit(f"❌ Error: {str(e)}")

# Queue command
@bot.on_message(filters.command("queue"))
async def queue_command(_, message: Message):
    chat_id = message.chat.id
    queue = queue_manager.get_queue(chat_id)
    
    if not queue:
        await message.reply_text("🔈 The queue is empty.")
        return
    
    queue_text = "🎵 **Current Queue:**\n\n"
    for i, song in enumerate(queue, 1):
        queue_text += f"**{i}.** {song['title']} | Requested by: {song['requested_by']}\n"
    
    await message.reply_text(queue_text)

# Skip command
@bot.on_message(filters.command("skip"))
async def skip_command(_, message: Message):
    chat_id = message.chat.id
    
    if not queue_manager.get_queue(chat_id):
        await message.reply_text("❌ No songs in queue to skip.")
        return
    
    await message.reply_text("⏭ Skipping to the next song...")
    
    # Remove current song and play next one
    queue_manager.skip(chat_id)
    queue = queue_manager.get_queue(chat_id)
    
    if queue:
        next_song = queue[0]
        await start_streaming(chat_id, next_song['url'], message)
    else:
        try:
            await call_py.leave_group_call(chat_id)
            await message.reply_text("🔈 Queue is empty, leaving voice chat.")
        except Exception as e:
            logger.error(f"Error leaving call: {e}")

# Stop command
@bot.on_message(filters.command("stop"))
async def stop_command(_, message: Message):
    chat_id = message.chat.id
    
    # Clear the queue
    queue_manager.clear_queue(chat_id)
    
    try:
        await call_py.leave_group_call(chat_id)
        await message.reply_text("⏹ Stopped playing and cleared queue.")
    except NoActiveGroupCall:
        await message.reply_text("⏹ No active voice chat to stop.")
    except Exception as e:
        logger.error(f"Error stopping playback: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")

# Pause command
@bot.on_message(filters.command("pause"))
async def pause_command(_, message: Message):
    chat_id = message.chat.id
    
    try:
        await call_py.pause_stream(chat_id)
        await message.reply_text("⏸ Paused playback.")
    except NoActiveGroupCall:
        await message.reply_text("❌ Not currently playing anything.")
    except Exception as e:
        logger.error(f"Error pausing: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")

# Resume command
@bot.on_message(filters.command("resume"))
async def resume_command(_, message: Message):
    chat_id = message.chat.id
    
    try:
        await call_py.resume_stream(chat_id)
        await message.reply_text("▶️ Resumed playback.")
    except NoActiveGroupCall:
        await message.reply_text("❌ Nothing to resume.")
    except Exception as e:
        logger.error(f"Error resuming: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")

# Search command
@bot.on_message(filters.command("search"))
async def search_command(_, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❌ Please provide a search term after the command.")
        return
    
    query = " ".join(message.command[1:])
    m = await message.reply_text(f"🔍 Searching for: **{query}**")
    
    try:
        results = await search_youtube(query)
        if not results:
            await m.edit("❌ No results found. Try a different search term.")
            return
        
        text = "🎵 **Search Results:**\n\n"
        for i, result in enumerate(results[:5], 1):
            title = result['title']
            duration = result['duration']
            video_id = result['id']
            text += f"**{i}.** {title} | `{duration}`\n" \
                    f"   `/play https://www.youtube.com/watch?v={video_id}`\n\n"
        
        await m.edit(text)
    
    except Exception as e:
        logger.error(f"Error searching: {e}")
        await m.edit(f"❌ Error: {str(e)}")

# Function to start streaming
async def start_streaming(chat_id, url, message):
    try:
        # Get the audio stream from YouTube
        file_path = await get_youtube_stream(url)
        
        # Start the stream
        await start_stream(call_py, chat_id, file_path)
    except Exception as e:
        logger.error(f"Error in start_streaming: {e}")
        await message.reply(f"❌ Error starting stream: {str(e)}")
        # Remove the song from queue and try the next one
        queue_manager.skip(chat_id)
        queue = queue_manager.get_queue(chat_id)
        if queue:
            next_song = queue[0]
            await message.reply_text(f"⏭ Skipping to next song due to error: **{next_song['title']}**")
            await start_streaming(chat_id, next_song['url'], message)

# Handle stream end
@call_py.on_update()
async def stream_end_handler(_, update):
    if isinstance(update, StreamEnded):
        chat_id = update.chat_id
        
        # Remove the current song from the queue
        queue_manager.skip(chat_id)
        queue = queue_manager.get_queue(chat_id)
        
        if queue:
            # Play the next song
            next_song = queue[0]
            await change_stream(call_py, chat_id, next_song['url'])
            
            # Send notification to the chat
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=f"🎵 **Now playing:** {next_song['title']}\n**Requested by:** {next_song['requested_by']}"
                )
            except Exception as e:
                logger.error(f"Error sending notification: {e}")
        else:
            # Leave the voice chat if queue is empty
            await leave_call(call_py, chat_id)
            try:
                await bot.send_message(chat_id=chat_id, text="🔈 Queue is empty, leaving voice chat.")
            except Exception as e:
                logger.error(f"Error sending notification: {e}")

# Start PyTgCalls client
async def start_pytgcalls():
    await call_py.start()
    print("PyTgCalls client started!")

# Register callback query handler for buttons
@bot.on_callback_query()
async def callback_handler(_, query):
    data = query.data
    
    if data == "cmd_help":
        help_text = (
            "🎵 **Available Commands:**\n\n"
            "• `/play` - Play a song by name or YouTube URL\n"
            "• `/search` - Search for a song on YouTube\n"
            "• `/skip` - Skip to the next song\n"
            "• `/stop` - Stop playing and clear queue\n"
            "• `/queue` - Show current queue\n"
            "• `/pause` - Pause the current song\n"
            "• `/resume` - Resume the paused song\n"
            "• `/ping` - Check bot's response time\n\n"
            "➡️ Add a song name or YouTube URL after commands like `/play`"
        )
        await query.message.edit_text(help_text, reply_markup=create_info_panel())
    
    elif data == "refresh":
        await query.message.edit_text(
            "👋 **Hello! I'm a Telegram Music Bot**\n\n"
            "I can play YouTube audio in voice chats. "
            "Add me to a group and use /help to see available commands.",
            reply_markup=create_info_panel()
        )
    
    await query.answer()
