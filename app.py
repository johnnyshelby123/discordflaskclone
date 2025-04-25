from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, current_user, login_required
from flask_socketio import SocketIO
from utils.json_storage import JSONStorage
from models.user import User
from models.server import Server
from routes.auth import auth_bp
from routes.server import server_bp
from routes.channel import channel_bp
from routes.gg import gg_bp
from routes.user import user_bp
from sockets.events import socketio
import os

# Create Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_flask_discord_clone')

# Initialize JSON storage
storage_path = os.path.join(os.path.dirname(__file__), 'data')
app.config['STORAGE_PATH'] = storage_path
storage = JSONStorage(storage_path)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.get(storage, user_id)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(server_bp, url_prefix='/server')
app.register_blueprint(channel_bp, url_prefix='/channel')
app.register_blueprint(gg_bp, url_prefix='/gg')
app.register_blueprint(user_bp, url_prefix='/user')

# Root route
@app.route('/')
def index():
    """Root route redirects to server list if logged in, otherwise to login page."""
    if current_user.is_authenticated:
        return redirect(url_for('server.list_servers'))
    return redirect(url_for('auth.login'))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error="Internal server error"), 500

# Context processor to make user_servers available in all templates
@app.context_processor
def inject_user_servers():
    if current_user.is_authenticated:
        user_servers = Server.get_by_member(storage, current_user.id)
        return dict(user_servers=user_servers)
    return dict(user_servers=[])

if __name__ == '__main__':
    # Create data directories if they don't exist
    os.makedirs(os.path.join(storage_path, 'users'), exist_ok=True)
    os.makedirs(os.path.join(storage_path, 'servers'), exist_ok=True)
    os.makedirs(os.path.join(storage_path, 'channels'), exist_ok=True)
    os.makedirs(os.path.join(storage_path, 'messages'), exist_ok=True)
    
    # Initialize Socket.IO with the Flask app
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
    
    # Run the app with Socket.IO
    socketio.run(app, debug=True, host='0.0.0.0', port=2500)
