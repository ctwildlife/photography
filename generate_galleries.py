import os
from PIL import Image
from PIL.ExifTags import TAGS

# Configuration
PHOTOS_DIR = 'Photos'
PAGES_DIR = 'Pages'
CSS_PATH = '/CSS/style.css'
JS_PATH = '/JS/script.js'

# HTML template
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>{category} Gallery</title>
    <link rel="stylesheet" href="{css}">
    <script src="{js}" defer></script>
    <style>
        .gallery {{ display: flex; flex-wrap: wrap; gap: 15px; }}
        .photo {{ width: 250px; text-align: center; }}
        img {{ width: 100%; height: auto; border-radius: 8px; }}
        p {{ margin: 5px 0 0 0; font-style: italic; }}
    </style>
</head>
<body>
    <h1>{category} Gallery</h1>
    <div class="gallery">
        {images}
    </div>
</body>
</html>"""

# Function to get EXIF caption if available
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

# Loop through categories
for category in os.listdir(PHOTOS_DIR):
    folder_path = os.path.join(PHOTOS_DIR, category)
    if not os.path.isdir(folder_path):
        continue

    images_html = ""
    for filename in sorted(os.listdir(folder_path)):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = f'/Photos/{category}/{filename}'
            caption = get_image_caption(os.path.join(folder_path, filename))
            images_html += f'<div class="photo"><img src="{image_path}" alt="{caption}"><p>{caption}</p></div>\n'

    html_content = HTML_TEMPLATE.format(category=category.capitalize(),
                                        css=CSS_PATH,
                                        js=JS_PATH,
                                        images=images_html)

    # Save HTML file
    os.makedirs(PAGES_DIR, exist_ok=True)
    output_file = os.path.join(PAGES_DIR, f'{category}.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Generated gallery for {category}: {output_file}")

print("All galleries generated successfully!")
