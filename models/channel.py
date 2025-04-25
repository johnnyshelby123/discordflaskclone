from datetime import datetime
import uuid

class Channel:
    def __init__(self, id=None, name=None, server_id=None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.server_id = server_id
        self.created_at = datetime.now().isoformat()
        
    def to_dict(self):
        """Convert channel object to dictionary for JSON storage."""
        return {
            'id': self.id,
            'name': self.name,
            'server_id': self.server_id,
            'created_at': self.created_at
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create a channel object from dictionary data."""
        channel = cls()
        channel.id = data.get('id')
        channel.name = data.get('name')
        channel.server_id = data.get('server_id')
        channel.created_at = data.get('created_at')
        return channel
        
    @classmethod
    def get(cls, storage, channel_id):
        """Get a channel by ID from storage."""
        data = storage.read('channels', channel_id)
        if not data:
            return None
        return cls.from_dict(data)
        
    @classmethod
    def get_by_server(cls, storage, server_id):
        """Get all channels for a server."""
        channels = storage.query('channels', lambda c: c.get('server_id') == server_id)
        return [cls.from_dict(channel) for channel in channels]
        
    def save(self, storage):
        """Save the channel to storage."""
        storage.write('channels', self.id, self.to_dict())
        return self
