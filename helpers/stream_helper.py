import os
import asyncio
import logging
from pytgcalls import PyTgCalls
from pytgcalls.types import StreamEnded, MediaStream, AudioQuality
from pytgcalls.types.raw import Stream

# Custom exceptions for compatibility
class NoActiveGroupCall(Exception):
    pass

class GroupCallNotFound(Exception):
    pass

from helpers.youtube import get_youtube_stream

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_stream(call_py: PyTgCalls, chat_id: int, file_path: str):
    """
    Start streaming an audio file in a voice chat
    
    Args:
        call_py: PyTgCalls client
        chat_id: ID of the chat
        file_path: Path to the audio file
    """
    try:
        await call_py.join_group_call(
            chat_id,
            MediaStream(
                file_path,
                audio_parameters=AudioQuality.HIGH,
            )
        )
        logger.info(f"Started streaming in chat {chat_id}")
    except Exception as e:
        logger.error(f"Error joining group call: {e}")
        if "no active group call" in str(e).lower():
            raise Exception("No active group call found. Please start a voice chat first.")
        else:
            raise Exception(f"Failed to join voice chat: {str(e)}")

async def change_stream(call_py: PyTgCalls, chat_id: int, url: str):
    """
    Change the current stream to a new song
    
    Args:
        call_py: PyTgCalls client
        chat_id: ID of the chat
        url: YouTube URL of the new song
    """
    try:
        # Get the audio stream from YouTube
        file_path = await get_youtube_stream(url)
        
        # Change the stream
        await call_py.change_stream(
            chat_id,
            MediaStream(
                file_path,
                audio_parameters=AudioQuality.HIGH,
            )
        )
        logger.info(f"Changed stream in chat {chat_id}")
    except Exception as e:
        logger.error(f"Error changing stream: {e}")
        # If changing stream fails, try to restart the stream
        try:
            await leave_call(call_py, chat_id)
            await asyncio.sleep(1)
            await start_stream(call_py, chat_id, file_path)
        except Exception as inner_e:
            logger.error(f"Error restarting stream: {inner_e}")
            raise Exception(f"Failed to change stream: {str(e)}")

async def leave_call(call_py: PyTgCalls, chat_id: int):
    """
    Leave the voice chat
    
    Args:
        call_py: PyTgCalls client
        chat_id: ID of the chat
    """
    try:
        await call_py.leave_group_call(chat_id)
        logger.info(f"Left voice chat in {chat_id}")
    except Exception as e:
        logger.error(f"Error leaving group call: {e}")
        # Don't raise an exception if we're already not in the call
        if not ("no active group call" in str(e).lower() or "group call not found" in str(e).lower()):
            raise Exception(f"Failed to leave voice chat: {str(e)}")

async def pause_stream(call_py: PyTgCalls, chat_id: int):
    """
    Pause the current stream
    
    Args:
        call_py: PyTgCalls client
        chat_id: ID of the chat
    """
    try:
        await call_py.pause_stream(chat_id)
        logger.info(f"Paused stream in chat {chat_id}")
    except Exception as e:
        logger.error(f"Error pausing stream: {e}")
        raise Exception(f"Failed to pause stream: {str(e)}")

async def resume_stream(call_py: PyTgCalls, chat_id: int):
    """
    Resume the paused stream
    
    Args:
        call_py: PyTgCalls client
        chat_id: ID of the chat
    """
    try:
        await call_py.resume_stream(chat_id)
        logger.info(f"Resumed stream in chat {chat_id}")
    except Exception as e:
        logger.error(f"Error resuming stream: {e}")
        raise Exception(f"Failed to resume stream: {str(e)}")
