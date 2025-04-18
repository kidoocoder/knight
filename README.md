# Telegram Music Bot

A Telegram music bot using Pyrogram and Py-TgCalls to play YouTube audio in voice chats without requiring cookies. Includes a web interface for easy management.

## Features

- Play YouTube audio in Telegram voice chats
- Search for songs by name or URL
- Queue management for multiple song requests
- Basic playback controls (play, skip, pause, resume, stop)
- No YouTube cookies required
- Web interface for bot management
- Real-time bot status monitoring

## Requirements

- Python 3.9 or higher
- FFmpeg
- A Telegram API key (API ID and API Hash)
- A Telegram Bot Token from @BotFather
- A Pyrogram user session string

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/telegram-music-bot.git
cd telegram-music-bot
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Copy the example environment file and edit it with your credentials:
```bash
cp .env.example .env
nano .env  # or use any text editor
```

4. Fill in the following information in the .env file:
   - API_ID and API_HASH from [my.telegram.org/apps](https://my.telegram.org/apps)
   - BOT_TOKEN from [@BotFather](https://t.me/BotFather)
   - SESSION_STRING - a Pyrogram session string for a user account
   - SESSION_SECRET - a random string for Flask session security

## Usage

### Starting the Bot

1. Run the Flask application:
```bash
python main.py
```

2. Open the web interface in your browser (http://localhost:5000 or your server address)

3. Click the "Start Bot" button on the web interface to activate the Telegram bot

### Available Commands

Once the bot is running and added to a Telegram group:

- `/play <song name or YouTube URL>` - Play a song
- `/search <query>` - Search for songs on YouTube
- `/queue` - Show the current music queue
- `/skip` - Skip to the next song
- `/pause` - Pause the current playback
- `/resume` - Resume playback
- `/stop` - Stop playback and clear queue

## How It Works

This bot utilizes two separate Telegram accounts:
1. A bot account (using BOT_TOKEN) that handles commands and user interactions
2. A user account (using SESSION_STRING) that joins and streams audio in voice chats

This dual-account approach is necessary because Telegram bots cannot join voice chats directly.

## Web Interface

The built-in web interface provides:
- Bot status monitoring
- Easy bot startup
- Command reference
- Setup instructions
