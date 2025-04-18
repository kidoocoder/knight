import os
import re
import uuid
import logging
import yt_dlp
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure yt-dlp options
ytdl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': f"{Config.TEMP_DOWNLOAD_DIRECTORY}%(id)s.%(ext)s",
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'extract_flat': 'in_playlist',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

# Function to search for YouTube videos
async def search_youtube(query):
    """
    Search for videos on YouTube
    
    Args:
        query: Search query, can be a video URL or search terms
        
    Returns:
        List of dictionaries with video information
    """
    # If query is a valid YouTube URL, get info directly
    if re.match(r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$", query):
        video_id = extract_video_id(query)
        if video_id:
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                try:
                    info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                    return [{
                        'id': info['id'],
                        'title': info['title'],
                        'duration': format_duration(info.get('duration', 0)),
                        'thumbnail': info.get('thumbnail', '')
                    }]
                except Exception as e:
                    logger.error(f"Error extracting video info: {e}")
                    return []
    
    # Otherwise search YouTube
    search_opts = {
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch5',  # Get top 5 results
        'noplaylist': True,
        'source_address': '0.0.0.0',
        'extract_flat': 'in_playlist'
    }
    
    try:
        with yt_dlp.YoutubeDL(search_opts) as ydl:
            info = ydl.extract_info(f"ytsearch5:{query}", download=False)
            results = info.get('entries', [])
            
            formatted_results = []
            for result in results:
                if not result:
                    continue
                
                # For search results, we need to get full info for each video
                try:
                    video_info = ydl.extract_info(
                        f"https://www.youtube.com/watch?v={result['id']}", 
                        download=False
                    )
                    formatted_results.append({
                        'id': video_info['id'],
                        'title': video_info['title'],
                        'duration': format_duration(video_info.get('duration', 0)),
                        'thumbnail': video_info.get('thumbnail', '')
                    })
                except Exception as e:
                    logger.error(f"Error getting full video info: {e}")
                    continue
            
            return formatted_results
    except Exception as e:
        logger.error(f"Error searching YouTube: {e}")
        return []

# Function to extract the YouTube video ID from a URL
def extract_video_id(url):
    """Extract the video ID from a YouTube URL"""
    # Regular expressions for different YouTube URL formats
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    
    match = re.match(youtube_regex, url)
    if match:
        return match.group(6)
    return None

# Function to format duration
def format_duration(duration_seconds):
    """Format duration in seconds to HH:MM:SS format"""
    if not duration_seconds:
        return "Unknown"
    
    minutes, seconds = divmod(int(duration_seconds), 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours:
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    else:
        return f"{minutes:02}:{seconds:02}"

# Function to download and process YouTube audio
async def get_youtube_stream(url):
    """
    Download and process audio from YouTube video
    
    Args:
        url: YouTube video URL
        
    Returns:
        Path to the downloaded audio file
    """
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")
    
    output_path = f"{Config.TEMP_DOWNLOAD_DIRECTORY}{video_id}.mp3"
    
    # Check if file already exists to avoid re-downloading
    if os.path.isfile(output_path):
        return output_path
    
    # Download the audio
    with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
        try:
            ydl.extract_info(url, download=True)
            return output_path
        except Exception as e:
            logger.error(f"Error downloading audio: {e}")
            raise Exception(f"Failed to download audio: {str(e)}")
