@echo off
echo Installing Flask Discord Clone dependencies...
pip install flask flask-socketio flask-login werkzeug

echo Creating data directories...
mkdir data\users
mkdir data\servers
mkdir data\channels
mkdir data\messages

echo Setting environment variables...
set FLASK_APP=app.py
set FLASK_ENV=production
set SECRET_KEY=dev_key_for_flask_discord_clone

echo Starting Flask Discord Clone...
python app.py

pause
