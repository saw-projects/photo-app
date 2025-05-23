from flask import Flask, render_template, jsonify, send_from_directory
import os

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/photos')
def get_photos():
    photos_dir = os.path.join(app.static_folder, 'photos')
    if not os.path.exists(photos_dir):
        os.makedirs(photos_dir)
    
    photos = []
    for filename in os.listdir(photos_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
            photos.append('/static/photos/' + filename)
    
    return jsonify(photos)

@app.route('/online')
def online():
    return "Success"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
