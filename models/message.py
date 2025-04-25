from datetime import datetime
import uuid

class Message:
    def __init__(self, id=None, channel_id=None, user_id=None, content=None):
        self.id = id or str(uuid.uuid4())
        self.channel_id = channel_id
        self.user_id = user_id
        self.content = content
        self.created_at = datetime.now().isoformat()
        self.updated_at = None
        
    def to_dict(self):
        """Convert message object to dictionary for JSON storage."""
        return {
            'id': self.id,
            'channel_id': self.channel_id,
            'user_id': self.user_id,
            'content': self.content,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create a message object from dictionary data."""
        message = cls()
        message.id = data.get('id')
        message.channel_id = data.get('channel_id')
        message.user_id = data.get('user_id')
        message.content = data.get('content')
        message.created_at = data.get('created_at')
        message.updated_at = data.get('updated_at')
        return message
        
    @classmethod
    def get(cls, storage, message_id):
        """Get a message by ID from storage."""
        data = storage.read('messages', message_id)
        if not data:
            return None
        return cls.from_dict(data)
        
    @classmethod
    def get_by_channel(cls, storage, channel_id, limit=50):
        """Get messages for a channel, with optional limit."""
        messages = storage.query('messages', lambda m: m.get('channel_id') == channel_id)
        # Sort by created_at
        messages.sort(key=lambda m: m.get('created_at'))
        # Return the most recent messages if limit is provided
        if limit:
            messages = messages[-limit:]
        return [cls.from_dict(message) for message in messages]
        
    def save(self, storage):
        """Save the message to storage."""
        storage.write('messages', self.id, self.to_dict())
        return self
        
    def update(self, content):
        """Update message content and set updated_at timestamp."""
        self.content = content
        self.updated_at = datetime.now().isoformat()
        return self
