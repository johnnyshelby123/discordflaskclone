from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import uuid
from datetime import datetime

class User(UserMixin):
    def __init__(self, id=None, username=None, email=None, password=None, image_url=None):
        self.id = id or str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password) if password else None
        self.image_url = image_url or "/static/images/default_avatar.png"
        self.created_at = datetime.now().isoformat()
        
    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        """Convert user object to dictionary for JSON storage."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'image_url': self.image_url,
            'created_at': self.created_at
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create a user object from dictionary data."""
        user = cls()
        user.id = data.get('id')
        user.username = data.get('username')
        user.email = data.get('email')
        user.password_hash = data.get('password_hash')
        user.image_url = data.get('image_url')
        user.created_at = data.get('created_at')
        return user
        
    @classmethod
    def get(cls, storage, user_id):
        """Get a user by ID from storage."""
        data = storage.read('users', user_id)
        if not data:
            return None
        return cls.from_dict(data)
        
    @classmethod
    def get_by_email(cls, storage, email):
        """Get a user by email from storage."""
        users = storage.query('users', lambda u: u.get('email') == email)
        if not users:
            return None
        return cls.from_dict(users[0])
        
    @classmethod
    def get_by_username(cls, storage, username):
        """Get a user by username from storage."""
        users = storage.query('users', lambda u: u.get('username') == username)
        if not users:
            return None
        return cls.from_dict(users[0])
        
    def save(self, storage):
        """Save the user to storage."""
        storage.write('users', self.id, self.to_dict())
        return self
