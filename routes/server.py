from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from models.server import Server
from utils.json_storage import JSONStorage
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import io

server_bp = Blueprint('server', __name__)

storage = JSONStorage(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data'))

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'server_icons')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(file):
    try:
        img = Image.open(file)
        
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[3])
            else:
                background.paste(img)
            img = background
        
        width, height = img.size
        size = max(width, height)
        
        square_img = Image.new('RGB', (size, size), (255, 255, 255))
        paste_x = (size - width) // 2
        paste_y = (size - height) // 2
        square_img.paste(img, (paste_x, paste_y))
        
        square_img = square_img.resize((128, 128), Image.LANCZOS)
        
        output = io.BytesIO()
        square_img.save(output, format='PNG')
        output.seek(0)
        
        return output
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

@server_bp.route('/')
@login_required
def list_servers():
    user_servers = Server.get_by_member(storage, current_user.id)
    return render_template('chat/servers.html', servers=user_servers)

@server_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_server():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        is_private = 'is_private' in request.form
        
        if not name:
            flash('Server name is required.')
            return render_template('chat/create_server.html')
        
        image_url = None
        if 'server_image' in request.files:
            file = request.files['server_image']
            if file and file.filename and allowed_file(file.filename):
                processed_file = process_image(file)
                if processed_file:
                    filename = secure_filename(f"{uuid.uuid4()}.png")
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(processed_file.read())
                    
                    image_url = f"/static/uploads/server_icons/{filename}"
            
        server = Server(
            name=name,
            description=description,
            owner_id=current_user.id,
            is_private=is_private,
            image_url=image_url
        )
        server.add_member(current_user.id)
        server.save(storage)
        
        from models.channel import Channel
        channel = Channel(
            name="general",
            server_id=server.id
        )
        channel.save(storage)
        
        return redirect(url_for('server.view_server', server_id=server.id))
        
    return render_template('chat/create_server.html')

@server_bp.route('/<server_id>')
@login_required
def view_server(server_id):
    server = Server.get(storage, server_id)
    
    if not server:
        flash('Server not found.')
        return redirect(url_for('server.list_servers'))
        
    if not server.is_member(current_user.id):
        flash('You are not a member of this server.')
        return redirect(url_for('server.list_servers'))
        
    from models.channel import Channel
    channels = Channel.get_by_server(storage, server_id)
    
    if not channels:
        channel = Channel(
            name="general",
            server_id=server.id
        )
        channel.save(storage)
        channels = [channel]
    
    return render_template('chat/server.html', server=server, channels=channels)

@server_bp.route('/<server_id>/settings')
@login_required
def server_settings(server_id):
    server = Server.get(storage, server_id)
    
    if not server:
        flash('Server not found.')
        return redirect(url_for('server.list_servers'))
        
    if server.owner_id != current_user.id:
        flash('Only the server owner can access server settings.')
        return redirect(url_for('server.view_server', server_id=server.id))
    
    return render_template('chat/server_settings.html', server=server)

@server_bp.route('/<server_id>/settings/update', methods=['POST'])
@login_required
def update_settings(server_id):
    server = Server.get(storage, server_id)
    
    if not server:
        flash('Server not found.')
        return redirect(url_for('server.list_servers'))
        
    if server.owner_id != current_user.id:
        flash('Only the server owner can update server settings.')
        return redirect(url_for('server.view_server', server_id=server.id))
    
    server.name = request.form.get('name', server.name)
    server.description = request.form.get('description', server.description)
    
    if 'server_image' in request.files:
        file = request.files['server_image']
        if file and file.filename and allowed_file(file.filename):
            processed_file = process_image(file)
            if processed_file:
                filename = secure_filename(f"{uuid.uuid4()}.png")
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(processed_file.read())
                
                server.image_url = f"/static/uploads/server_icons/{filename}"
    
    server.save(storage)
    
    flash('Server settings updated successfully.')
    return redirect(url_for('server.server_settings', server_id=server.id))

@server_bp.route('/<server_id>/join')
@login_required
def join_server(server_id):
    server = Server.get(storage, server_id)
    
    if not server:
        flash('Server not found.')
        return redirect(url_for('server.list_servers'))
        
    if server.is_private and server.owner_id != current_user.id:
        flash('This server is private. You need an invitation to join.')
        return redirect(url_for('server.list_servers'))
        
    server.add_member(current_user.id)
    server.save(storage)
    
    return redirect(url_for('server.view_server', server_id=server.id))

@server_bp.route('/<server_id>/leave')
@login_required
def leave_server(server_id):
    server = Server.get(storage, server_id)
    
    if not server:
        flash('Server not found.')
        return redirect(url_for('server.list_servers'))
        
    if server.owner_id == current_user.id:
        flash('Server owners cannot leave their own server. You can delete the server instead.')
        return redirect(url_for('server.view_server', server_id=server.id))
        
    server.remove_member(current_user.id)
    server.save(storage)
    
    return redirect(url_for('server.list_servers'))

@server_bp.route('/<server_id>/delete')
@login_required
def delete_server(server_id):
    server = Server.get(storage, server_id)
    
    if not server:
        flash('Server not found.')
        return redirect(url_for('server.list_servers'))
        
    if server.owner_id != current_user.id:
        flash('Only the server owner can delete the server.')
        return redirect(url_for('server.view_server', server_id=server.id))
        
    from models.channel import Channel
    channels = Channel.get_by_server(storage, server_id)
    for channel in channels:
        storage.delete('channels', channel.id)
        
    storage.delete('servers', server_id)
    
    return redirect(url_for('server.list_servers'))
