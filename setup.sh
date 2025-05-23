#!/bin/bash

# setup and install dependencies
cd ~/projects/photo-kiosk
source venv/bin/activate
pip install -r requirements.txt

# run the app with Gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 3 'app:app'
