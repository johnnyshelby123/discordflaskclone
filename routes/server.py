from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models.server import Server
from utils.json_storage import JSONStorage
import os

# Create blueprint for server routes
server_bp = Blueprint('server', __name__)

# Initialize JSON storage
storage = JSONStorage(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data'))

@server_bp.route('/')
@login_required
def list_servers():
    """List all servers for the current user."""
    # Get servers where user is a member
    user_servers = Server.get_by_member(storage, current_user.id)
    return render_template('chat/servers.html', servers=user_servers)

@server_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_server():
    """Create a new server."""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        is_private = 'is_private' in request.form
        
        # Validate input
        if not name:
            flash('Server name is required.')
            return render_template('chat/create_server.html')
            
        # Create server
        server = Server(
            name=name,
            description=description,
            owner_id=current_user.id,
            is_private=is_private
        )
        # Add the creator as a member
        server.add_member(current_user.id)
        server.save(storage)
        
        # Create default "general" channel
        from models.channel import Channel
        channel = Channel(
            name="general",
            server_id=server.id
        )
        channel.save(storage)
        
        flash(f'Server "{name}" has been created with a #general channel.')
        return redirect(url_for('server.view_server', server_id=server.id))
        
    return render_template('chat/create_server.html')

@server_bp.route('/<server_id>')
@login_required
def view_server(server_id):
    """View a server and its channels."""
    server = Server.get(storage, server_id)
    
    if not server:
        flash('Server not found.')
        return redirect(url_for('server.list_servers'))
        
    # Check if user is a member
    if not server.is_member(current_user.id):
        flash('You are not a member of this server.')
        return redirect(url_for('server.list_servers'))
        
    # Get channels for this server
    from models.channel import Channel
    channels = Channel.get_by_server(storage, server_id)
    
    # If there are no channels, create a default one
    if not channels:
        channel = Channel(
            name="general",
            server_id=server.id
        )
        channel.save(storage)
        channels = [channel]
    
    return render_template('chat/server.html', server=server, channels=channels)

@server_bp.route('/<server_id>/join')
@login_required
def join_server(server_id):
    """Join a server."""
    server = Server.get(storage, server_id)
    
    if not server:
        flash('Server not found.')
        return redirect(url_for('server.list_servers'))
        
    # Check if server is private
    if server.is_private and server.owner_id != current_user.id:
        flash('This server is private. You need an invitation to join.')
        return redirect(url_for('server.list_servers'))
        
    # Add user to server members
    server.add_member(current_user.id)
    server.save(storage)
    
    flash(f'You have joined the server: {server.name}')
    return redirect(url_for('server.view_server', server_id=server.id))

@server_bp.route('/<server_id>/leave')
@login_required
def leave_server(server_id):
    """Leave a server."""
    server = Server.get(storage, server_id)
    
    if not server:
        flash('Server not found.')
        return redirect(url_for('server.list_servers'))
        
    # Check if user is the owner
    if server.owner_id == current_user.id:
        flash('Server owners cannot leave their own server. You can delete the server instead.')
        return redirect(url_for('server.view_server', server_id=server.id))
        
    # Remove user from server members
    server.remove_member(current_user.id)
    server.save(storage)
    
    flash(f'You have left the server: {server.name}')
    return redirect(url_for('server.list_servers'))

@server_bp.route('/<server_id>/delete')
@login_required
def delete_server(server_id):
    """Delete a server."""
    server = Server.get(storage, server_id)
    
    if not server:
        flash('Server not found.')
        return redirect(url_for('server.list_servers'))
        
    # Check if user is the owner
    if server.owner_id != current_user.id:
        flash('Only the server owner can delete the server.')
        return redirect(url_for('server.view_server', server_id=server.id))
        
    # Delete all channels for this server
    from models.channel import Channel
    channels = Channel.get_by_server(storage, server_id)
    for channel in channels:
        storage.delete('channels', channel.id)
        
    # Delete the server
    storage.delete('servers', server_id)
    
    flash(f'Server "{server.name}" has been deleted.')
    return redirect(url_for('server.list_servers'))
