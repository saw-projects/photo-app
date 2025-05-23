from flask import Flask, render_template, jsonify, send_from_directory, request, abort
import os
import uuid
import ipaddress
import logging
import datetime
import json
from functools import wraps
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__, static_folder='static')

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})


# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Create a custom logger
request_logger = logging.getLogger('request_logger')
request_logger.setLevel(logging.INFO)

# Create handlers
log_file = os.path.join(log_dir, 'requests.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(log_format)

# Add handlers to the logger
request_logger.addHandler(file_handler)

# Prevent propagation to root logger (which would log to console)
request_logger.propagate = False

# IP whitelist and blacklist configuration
WHITELIST_NETWORKS = [
    ipaddress.ip_network('192.168.0.0/24'),  # Local network
    ipaddress.ip_network('127.0.0.0/8'),     # Localhost
]

BLACKLIST_IPS = [
    # Add specific IPs to blacklist here if needed
    # ipaddress.ip_address('192.168.0.100'),
]

def log_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get request information
        timestamp = datetime.datetime.now().isoformat()
        endpoint = request.endpoint
        method = request.method
        path = request.path
        client_ip = request.remote_addr
        headers = dict(request.headers)
        args = dict(request.args)
        
        # Get request body if present, safely handling different content types
        try:
            if request.is_json:
                body = request.get_json()
            elif request.form:
                body = dict(request.form)
            else:
                body = request.get_data(as_text=True)
                if not body:
                    body = 'No body'
        except Exception as e:
            body = f'Error parsing body: {str(e)}'
            
        # Create log entry
        log_entry = {
            'timestamp': timestamp,
            'endpoint': endpoint,
            'method': method,
            'path': path,
            'ip': client_ip,
            'headers': headers,
            'args': args,
            'body': body
        }
        
        # Log the request
        request_logger.info(json.dumps(log_entry, default=str))
        
        return f(*args, **kwargs)
    return decorated_function

def ip_access_control(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get client IP address
        client_ip = request.remote_addr
        ip_obj = ipaddress.ip_address(client_ip)
        
        # Check if IP is in blacklist
        if any(ip_obj == blacklisted_ip for blacklisted_ip in BLACKLIST_IPS):
            request_logger.warning(f'Blocked access from blacklisted IP: {client_ip}')
            abort(403)  # Forbidden
        
        # Check if IP is in whitelist networks
        if not any(ip_obj in network for network in WHITELIST_NETWORKS):
            request_logger.warning(f'Blocked access from non-whitelisted IP: {client_ip}')
            abort(403)  # Forbidden
            
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@ip_access_control
@log_request
def index():
    return render_template('index.html')

@app.route('/photos')
@ip_access_control
@log_request
def get_photos():
    photos_dir = os.path.join(app.static_folder, 'photos')
    if not os.path.exists(photos_dir):
        os.makedirs(photos_dir)
    
    photos = []
    for filename in os.listdir(photos_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
            photos.append('/static/photos/' + filename)
    
    return jsonify(photos)

@app.route('/upload', methods=['POST'])
@ip_access_control
@log_request
def upload_photo():
    if 'photo' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['photo']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.heic')):
        # Generate a unique filename to prevent overwriting
        filename = secure_filename(file.filename)
        unique_filename = f"{str(uuid.uuid4())[:8]}_{filename}"
        
        photos_dir = os.path.join(app.static_folder, 'photos')
        if not os.path.exists(photos_dir):
            os.makedirs(photos_dir)
            
        file_path = os.path.join(photos_dir, unique_filename)
        file.save(file_path)
        
        return jsonify({'success': True, 'filename': unique_filename})
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/online')
@ip_access_control
@log_request
def online():
    return "Service is online."


# This conditional is only used when running with 'python app.py' directly
# When running with Gunicorn, only the Flask 'app' object is used
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
