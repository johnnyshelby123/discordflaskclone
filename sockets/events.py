from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user
from models.message import Message
from models.user import User
from models.server import Server
from models.channel import Channel
from utils.json_storage import JSONStorage
from datetime import datetime
import os

# Initialize Socket.IO
socketio = SocketIO()

# Initialize JSON storage
storage = JSONStorage(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data'))

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    if not current_user.is_authenticated:
        return False
    emit('connection_success', {'user_id': current_user.id})

@socketio.on('join')
def handle_join(data):
    """Handle client joining a channel."""
    if not current_user.is_authenticated:
        return
        
    channel_id = data.get('channel_id')
    join_room(channel_id)
    emit('user_joined', {
        'user_id': current_user.id,
        'username': current_user.username
    }, room=channel_id)

@socketio.on('leave')
def handle_leave(data):
    """Handle client leaving a channel."""
    if not current_user.is_authenticated:
        return
        
    channel_id = data.get('channel_id')
    leave_room(channel_id)
    emit('user_left', {
        'user_id': current_user.id,
        'username': current_user.username
    }, room=channel_id)

@socketio.on('message')
def handle_message(data):
    """Handle new message from client."""
    if not current_user.is_authenticated:
        return
        
    channel_id = data.get('channel_id')
    content = data.get('content')
    
    if not content or not content.strip():
        return
    
    # Create and save message
    message = Message(
        channel_id=channel_id,
        user_id=current_user.id,
        content=content
    )
    message.save(storage)
    
    # Get user data
    user = User.get(storage, current_user.id)
    
    # Broadcast message to all clients in the channel
    emit('new_message', {
        'id': message.id,
        'channel_id': channel_id,
        'user_id': current_user.id,
        'username': user.username,
        'content': content,
        'created_at': message.created_at,
        'image_url': user.image_url
    }, room=channel_id)

@socketio.on('edit_message')
def handle_edit_message(data):
    """Handle message edit from client."""
    if not current_user.is_authenticated:
        return
        
    message_id = data.get('message_id')
    content = data.get('content')
    
    if not content or not content.strip():
        return
    
    # Get message
    message = Message.get(storage, message_id)
    if not message or message.user_id != current_user.id:
        return
        
    # Update message
    message.update(content)
    message.save(storage)
    
    # Broadcast update to all clients in the channel
    emit('message_updated', {
        'id': message.id,
        'content': content,
        'updated_at': message.updated_at
    }, room=message.channel_id)

@socketio.on('delete_message')
def handle_delete_message(data):
    """Handle message deletion from client."""
    if not current_user.is_authenticated:
        return
        
    message_id = data.get('message_id')
    
    # Get message
    message = Message.get(storage, message_id)
    if not message or message.user_id != current_user.id:
        return
        
    channel_id = message.channel_id
    
    # Delete message
    storage.delete('messages', message_id)
    
    # Broadcast deletion to all clients in the channel
    emit('message_deleted', {
        'id': message_id
    }, room=channel_id)

@socketio.on('join_server')
def handle_join_server(data):
    """Handle user joining a server."""
    if not current_user.is_authenticated:
        return
        
    server_id = data.get('server_id')
    
    # Get server
    server = Server.get(storage, server_id)
    if not server:
        return
    
    # Get user data
    user = User.get(storage, current_user.id)
    if not user:
        return
    
    # Join server room
    join_room(f'server_{server_id}')
    
    # Broadcast to all clients in the server
    emit('server_member_joined', {
        'server_id': server_id,
        'user': {
            'id': user.id,
            'username': user.username,
            'image_url': user.image_url
        }
    }, room=f'server_{server_id}')

@socketio.on('leave_server')
def handle_leave_server(data):
    """Handle user leaving a server."""
    if not current_user.is_authenticated:
        return
        
    server_id = data.get('server_id')
    
    # Leave server room
    leave_room(f'server_{server_id}')
    
    # Broadcast to all clients in the server
    emit('server_member_left', {
        'server_id': server_id,
        'user_id': current_user.id
    }, room=f'server_{server_id}')

@socketio.on('get_server_members')
def handle_get_server_members(data):
    """Handle request for server members."""
    if not current_user.is_authenticated:
        return
        
    server_id = data.get('server_id')
    
    # Get server
    server = Server.get(storage, server_id)
    if not server:
        return
    
    # Check if user is a member
    if not server.is_member(current_user.id):
        return
    
    # Get all members
    members = []
    for member_id in server.members:
        user = User.get(storage, member_id)
        if user:
            members.append({
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url
            })
    
    # Send members to the requesting client
    emit('server_members', {
        'server_id': server_id,
        'members': members
    })

@socketio.on('get_server_channels')
def handle_get_server_channels(data):
    """Handle request for server channels."""
    if not current_user.is_authenticated:
        return
        
    server_id = data.get('server_id')
    
    # Get server
    server = Server.get(storage, server_id)
    if not server:
        return
    
    # Check if user is a member
    if not server.is_member(current_user.id):
        return
    
    # Get all channels
    channels = Channel.get_by_server(storage, server_id)
    channel_data = []
    
    for channel in channels:
        channel_data.append({
            'id': channel.id,
            'name': channel.name,
            'server_id': channel.server_id
        })
    
    # Send channels to the requesting client
    emit('server_channels', {
        'server_id': server_id,
        'channels': channel_data
    })

# Add this to routes/channel.py after channel creation
def broadcast_channel_created(channel):
    """Broadcast channel creation to all server members."""
    socketio.emit('channel_created', {
        'server_id': channel.server_id,
        'channel': {
            'id': channel.id,
            'name': channel.name,
            'server_id': channel.server_id
        }
    }, room=f'server_{channel.server_id}')

# Add this to routes/channel.py after channel deletion
def broadcast_channel_deleted(channel_id, server_id):
    """Broadcast channel deletion to all server members."""
    socketio.emit('channel_deleted', {
        'server_id': server_id,
        'channel_id': channel_id
    }, room=f'server_{server_id}')
