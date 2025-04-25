from datetime import datetime
import uuid
import random
import string

class Server:
    def __init__(self, id=None, name=None, description=None, image_url=None, owner_id=None, is_private=False, members=None, invite_code=None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.image_url = image_url or "/static/images/default_server_icon.png"
        self.owner_id = owner_id
        self.is_private = is_private
        self.members = members or [owner_id] if owner_id else []
        self.created_at = datetime.now().isoformat()
        self.invite_code = invite_code or self.generate_invite_code()
        
    def generate_invite_code(self):
        """Generate a unique 7-character invite code."""
        # Get all existing invite codes
        from utils.json_storage import JSONStorage
        import os
        storage_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        storage = JSONStorage(storage_path)
        
        all_servers = storage.query('servers', lambda s: True)
        existing_codes = [s.get('invite_code', '') for s in all_servers]
        
        # Generate a new unique code
        while True:
            # Generate a random 7-character string using letters and numbers
            chars = string.ascii_letters + string.digits
            code = ''.join(random.choice(chars) for _ in range(7))
            
            # Ensure uniqueness
            if code not in existing_codes:
                return code
    
    def to_dict(self):
        """Convert server object to dictionary for JSON storage."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url,
            'owner_id': self.owner_id,
            'is_private': self.is_private,
            'members': self.members,
            'created_at': self.created_at,
            'invite_code': self.invite_code
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create a server object from dictionary data."""
        server = cls()
        server.id = data.get('id')
        server.name = data.get('name')
        server.description = data.get('description')
        server.image_url = data.get('image_url')
        server.owner_id = data.get('owner_id')
        server.is_private = data.get('is_private', False)
        server.members = data.get('members', [])
        server.created_at = data.get('created_at')
        server.invite_code = data.get('invite_code')
        return server
        
    @classmethod
    def get(cls, storage, server_id):
        """Get a server by ID from storage."""
        data = storage.read('servers', server_id)
        if not data:
            return None
        return cls.from_dict(data)
        
    @classmethod
    def get_by_owner(cls, storage, owner_id):
        """Get all servers owned by a user."""
        servers = storage.query('servers', lambda s: s.get('owner_id') == owner_id)
        return [cls.from_dict(server) for server in servers]
        
    @classmethod
    def get_by_member(cls, storage, user_id):
        """Get all servers where user is a member."""
        servers = storage.query('servers', lambda s: user_id in s.get('members', []))
        return [cls.from_dict(server) for server in servers]
        
    def save(self, storage):
        """Save the server to storage."""
        storage.write('servers', self.id, self.to_dict())
        return self
        
    def add_member(self, user_id):
        """Add a member to the server."""
        if user_id not in self.members:
            self.members.append(user_id)
        return self
        
    def remove_member(self, user_id):
        """Remove a member from the server."""
        if user_id in self.members:
            self.members.remove(user_id)
        return self
        
    def is_member(self, user_id):
        """Check if a user is a member of the server."""
        return user_id in self.members
