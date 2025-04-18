from config import Config

class QueueManager:
    def __init__(self):
        """Initialize the queue manager"""
        # Store queues for each chat
        self.queues = {}
        self.max_queue_size = Config.MAX_QUEUE_SIZE
    
    def get_queue(self, chat_id):
        """Get the queue for a specific chat"""
        if chat_id not in self.queues:
            self.queues[chat_id] = []
        return self.queues[chat_id]
    
    def add_to_queue(self, chat_id, song_info):
        """
        Add a song to the queue
        
        Args:
            chat_id: ID of the chat
            song_info: Dictionary with song information
            
        Returns:
            Position in queue (1 = currently playing, 2+ = in queue)
        """
        if chat_id not in self.queues:
            self.queues[chat_id] = []
        
        # Check if queue is full
        if len(self.queues[chat_id]) >= self.max_queue_size:
            raise ValueError(f"Queue is full (max {self.max_queue_size} songs)")
        
        # Add the song to the queue
        self.queues[chat_id].append(song_info)
        
        # Return position in queue (1-based)
        return len(self.queues[chat_id])
    
    def skip(self, chat_id):
        """
        Skip the current song in the queue
        
        Args:
            chat_id: ID of the chat
            
        Returns:
            The next song in queue, or None if queue is empty
        """
        if chat_id not in self.queues or not self.queues[chat_id]:
            return None
        
        # Remove the current song (first in queue)
        self.queues[chat_id].pop(0)
        
        # Return the new first song, or None if queue is empty
        if self.queues[chat_id]:
            return self.queues[chat_id][0]
        return None
    
    def clear_queue(self, chat_id):
        """Clear the queue for a specific chat"""
        if chat_id in self.queues:
            self.queues[chat_id] = []
    
    def is_empty(self, chat_id):
        """Check if the queue is empty"""
        return chat_id not in self.queues or not self.queues[chat_id]
    
    def get_current_song(self, chat_id):
        """Get the currently playing song"""
        if chat_id in self.queues and self.queues[chat_id]:
            return self.queues[chat_id][0]
        return None
