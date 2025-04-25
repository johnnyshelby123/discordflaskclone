from flask import Blueprint, redirect, url_for, flash
from flask_login import login_required, current_user
from models.server import Server
from utils.json_storage import JSONStorage
import os

# Create blueprint for invite code routes
gg_bp = Blueprint('gg', __name__)

# Initialize JSON storage
storage = JSONStorage(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data'))

@gg_bp.route('/<invite_code>')
@login_required
def join_by_invite(invite_code):
    """Join a server using an invite code."""
    # Find server with this invite code
    servers = storage.query('servers', lambda s: s.get('invite_code') == invite_code)
    
    if not servers:
        flash('Invalid invite code or server not found.')
        return redirect(url_for('server.list_servers'))
    
    server_data = servers[0]
    server = Server.from_dict(server_data)
    
    # Check if user is already a member
    if server.is_member(current_user.id):
        return redirect(url_for('server.view_server', server_id=server.id))
    
    # Add user to server members
    server.add_member(current_user.id)
    server.save(storage)
    
    flash(f'You have joined the server: {server.name}')
    return redirect(url_for('server.view_server', server_id=server.id))
