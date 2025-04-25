from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from models.server import Server
from models.channel import Channel
from models.message import Message
from models.user import User
from utils.json_storage import JSONStorage
import os
from sockets.events import broadcast_channel_created, broadcast_channel_deleted

# Create blueprint for channel routes
channel_bp = Blueprint('channel', __name__)

# Initialize JSON storage
storage = JSONStorage(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data'))

@channel_bp.route('/create/<server_id>', methods=['GET', 'POST'])
@login_required
def create_channel(server_id):
    """Create a new channel in a server."""
    server = Server.get(storage, server_id)
    
    if not server:
        flash('Server not found.')
        return redirect(url_for('server.list_servers'))
        
    # Check if user is the owner or a member
    if not server.is_member(current_user.id):
        flash('You are not a member of this server.')
        return redirect(url_for('server.list_servers'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        
        # Validate input
        if not name:
            flash('Channel name is required.')
            return render_template('chat/create_channel.html', server=server)
            
        # Create channel
        channel = Channel(
            name=name,
            server_id=server.id
        )
        channel.save(storage)
        
        # Broadcast channel creation to all server members
        broadcast_channel_created(channel)
        
        # Removed flash message to eliminate notification header
        return redirect(url_for('server.view_server', server_id=server.id))
        
    return render_template('chat/create_channel.html', server=server)

@channel_bp.route('/<channel_id>')
@login_required
def view_channel(channel_id):
    """View a channel and its messages."""
    channel = Channel.get(storage, channel_id)
    
    if not channel:
        flash('Channel not found.')
        return redirect(url_for('server.list_servers'))
        
    server = Server.get(storage, channel.server_id)
    
    if not server:
        flash('Server not found.')
        return redirect(url_for('server.list_servers'))
        
    # Check if user is a member of the server
    if not server.is_member(current_user.id):
        flash('You are not a member of this server.')
        return redirect(url_for('server.list_servers'))
        
    # Get messages for this channel
    messages = Message.get_by_channel(storage, channel_id)
    
    # Get all channels for this server (for sidebar)
    channels = Channel.get_by_server(storage, server.id)
    
    # Get user data for each message
    for message in messages:
        message.user = User.get(storage, message.user_id)
    
    # Get all members of the server
    members = []
    for member_id in server.members:
        user = User.get(storage, member_id)
        if user:
            members.append(user)
    
    return render_template('chat/channel.html', 
                          server=server, 
                          channel=channel, 
                          channels=channels, 
                          messages=messages,
                          members=members)

@channel_bp.route('/<channel_id>/delete')
@login_required
def delete_channel(channel_id):
    """Delete a channel."""
    channel = Channel.get(storage, channel_id)
    
    if not channel:
        flash('Channel not found.')
        return redirect(url_for('server.list_servers'))
        
    server = Server.get(storage, channel.server_id)
    
    if not server:
        flash('Server not found.')
        return redirect(url_for('server.list_servers'))
        
    # Check if user is the server owner
    if server.owner_id != current_user.id:
        flash('Only the server owner can delete channels.')
        return redirect(url_for('channel.view_channel', channel_id=channel_id))
        
    # Check if this is the last channel
    channels = Channel.get_by_server(storage, server.id)
    if len(channels) <= 1:
        flash('Cannot delete the last channel in a server.')
        return redirect(url_for('channel.view_channel', channel_id=channel_id))
        
    # Store server_id before deletion
    server_id = channel.server_id
    
    # Delete the channel
    storage.delete('channels', channel_id)
    
    # Broadcast channel deletion to all server members
    broadcast_channel_deleted(channel_id, server_id)
    
    # Removed flash message to eliminate notification header
    return redirect(url_for('server.view_server', server_id=server.id))