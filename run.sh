#!/bin/bash

# Script to run the Flask Discord Clone application

# Create data directories if they don't exist
mkdir -p data/users
mkdir -p data/servers
mkdir -p data/channels
mkdir -p data/messages

# Install required packages
pip install flask flask-socketio flask-login werkzeug

# Set Flask environment variables
export FLASK_APP=app.py
export FLASK_ENV=production
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(16))')

# Run the application
python app.py
