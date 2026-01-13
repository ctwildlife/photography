from flask import Flask, render_template, send_from_directory
import os
from PIL import Image
from PIL.ExifTags import TAGS

app = Flask(__name__, template_folder='Pages', static_folder='')

PHOTOS_DIR = 'Photos'

def get_image_caption(image_path):
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        if exif_data:
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == 'ImageDescription':
                    return value
    except:
        pass
    return ""

@app.route('/')
def index():
    # Serve your standalone index page
    return send_from_directory('Index', 'index.html')

@app.route('/<category>')
def gallery(category):
    folder_path = os.path.join(PHOTOS_DIR, category)
    if not os.path.exists(folder_path):
        return f"Category '{category}' not found", 404

    images = []
    for filename in sorted(os.listdir(folder_path)):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            path = f'/Photos/{category}/{filename}'
            caption = get_image_caption(os.path.join(folder_path, filename))
            images.append({'path': path, 'caption': caption})

    return render_template('gallery.html', category=category, images=images)

# Serve photos dynamically
@app.route('/Photos/<category>/<filename>')
def serve_image(category, filename):
    return send_from_directory(os.path.join(PHOTOS_DIR, category), filename)

# Serve CSS and JS from your folders
@app.route('/CSS/<filename>')
def serve_css(filename):
    return send_from_directory('CSS', filename)

@app.route('/JS/<filename>')
def serve_js(filename):
    return send_from_directory('JS', filename)

if __name__ == '__main__':
    app.run(debug=True)
