@echo off
REM Install dependencies globally using pip
pip install -r requirements.txt

REM Set Flask app environment variables
set FLASK_APP=app.py
set FLASK_ENV=development

REM Start the Flask app
flask run --debug

REM Pause to keep the console open after the app stops
pause