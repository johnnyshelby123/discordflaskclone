from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models.user import User
from utils.json_storage import JSONStorage
import os
import uuid
from werkzeug.utils import secure_filename

# Create blueprint for user routes
user_bp = Blueprint('user', __name__)

# Initialize JSON storage
storage = JSONStorage(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data'))

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'avatars')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route('/settings')
@login_required
def settings():
    """Display user settings page."""
    return render_template('user/settings.html')

@user_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile information."""
    user = User.get(storage, current_user.id)
    
    if not user:
        flash('User not found.')
        return redirect(url_for('auth.logout'))
    
    # Handle avatar upload
    if 'avatar' in request.files:
        file = request.files['avatar']
        if file and file.filename and allowed_file(file.filename):
            # Generate unique filename
            filename = secure_filename(file.filename)
            filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Save file
            file.save(filepath)
            
            # Update user image URL
            user.image_url = f"/static/uploads/avatars/{filename}"
            user.save(storage)
            
            flash('Profile updated successfully!')
        elif file.filename:
            flash('Invalid file type. Please upload a PNG, JPG, JPEG, or GIF file.')
    
    return redirect(url_for('user.settings'))
