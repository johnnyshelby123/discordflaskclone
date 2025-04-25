from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from utils.json_storage import JSONStorage
import os

# Create blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

# Initialize JSON storage
storage = JSONStorage(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('server.list_servers'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Validate input
        if not username or not password:
            flash('Please enter both username and password.')
            return render_template('auth/login.html')
            
        # Get user by username
        user = User.get_by_username(storage, username)
        
        # Check if user exists and password is correct
        if not user or not user.check_password(password):
            flash('Invalid username or password.')
            return render_template('auth/login.html')
            
        # Log in user
        login_user(user)
        
        # Redirect to server list
        return redirect(url_for('server.list_servers'))
        
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('server.list_servers'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not username or not email or not password:
            flash('Please fill in all required fields.')
            return render_template('auth/register.html')
            
        if password != confirm_password:
            flash('Passwords do not match.')
            return render_template('auth/register.html')
            
        # Check if username already exists
        existing_user = User.get_by_username(storage, username)
        if existing_user:
            flash('Username already exists.')
            return render_template('auth/register.html')
            
        # Check if email already exists
        existing_email = User.get_by_email(storage, email)
        if existing_email:
            flash('Email already registered.')
            return render_template('auth/register.html')
            
        # Create new user
        user = User(
            username=username,
            email=email,
            password=password
        )
        user.save(storage)
        
        # Log in new user
        login_user(user)
        
        # Redirect to server list
        flash('Registration successful! Welcome to Flask Discord Clone.')
        return redirect(url_for('server.list_servers'))
        
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))
