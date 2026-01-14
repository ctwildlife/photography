import os
from PIL import Image
from datetime import datetime
import subprocess
import json

# =========================
# Config
# =========================
photos_base = "photos"
web_base = "photos_web"
output_file = "pages/recent.html"
max_photos = 15

# =========================
# Resize function
# =========================
def resize_for_web_once(original_path, web_path, max_size=(1920, 1920), target_mb=1.0):
    if os.path.exists(web_path) and os.path.getsize(web_path) <= target_mb * 1024 * 1024:
        return
    os.makedirs(os.path.dirname(web_path), exist_ok=True)
    try:
        img = Image.open(original_path)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        quality = 85
        while quality >= 30:
            img.save(web_path, format="JPEG", quality=quality, optimize=True)
            size_mb = os.path.getsize(web_path) / (1024 * 1024)
            if size_mb <= target_mb:
                break
            quality -= 5
        print(f"Created/resized web image: {web_path} ({size_mb:.2f} MB, quality={quality})")
    except Exception as e:
        print(f"Error resizing {original_path}: {e}")

# =========================
# EXIF functions
# =========================
def get_date_taken(image_path):
    try:
        result = subprocess.run(
            ["exiftool", "-DateTimeOriginal", "-s3", image_path],
            capture_output=True,
            text=True
        )
        date_str = result.stdout.strip()
        if not date_str:
            return None
        return datetime.strptime(date_str.split(" ")[0], "%Y:%m:%d")
    except Exception:
        return None

def get_caption(image_path):
    try:
        result = subprocess.run(
            ["exiftool", "-Description", "-s3", image_path],
            capture_output=True,
            text=True
        )
        caption = result.stdout.strip()
        if caption:
            return caption
        else:
            return os.path.splitext(os.path.basename(image_path))[0].replace("-", " ").capitalize()
    except Exception:
        return os.path.basename(image_path)

# =========================
# Gather all images
# =========================
def get_all_images(base_path):
    images = []
    for root, dirs, files in os.walk(base_path):
        for f in files:
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                images.append(os.path.join(root, f))
    return images

# =========================
# Main
# =========================
all_images = get_all_images(photos_base)
all_images.sort(key=lambda p: get_date_taken(p) or datetime.min, reverse=True)
recent_images = all_images[:max_photos]

# Resize and build JSON data
recent_photos_data = []
for img_path in recent_images:
    img_file = os.path.basename(img_path)
    web_path = os.path.join(web_base, img_file)
    resize_for_web_once(img_path, web_path)
    caption = get_caption(img_path)
    recent_photos_data.append({
        "src": f"/photography/{web_base}/{img_file}",
        "caption": caption
    })

# =========================
# Generate HTML page
# =========================
html_lines = [
    "<!DOCTYPE html>",
    "<html lang='en'>",
    "<head>",
    "    <meta charset='utf-8'>",
    "    <title>Recent Photos</title>",
    "    <link rel='stylesheet' href='/photography/css/style.css'>",
    "</head>",
    "<body>",
    "<h1>Recent Photos</h1>",
    "<div class='gallery'>"
]

for item in recent_photos_data:
    html_lines.append("  <figure class='photo-block'>")
    html_lines.append(f"    <img src='{item['src']}' alt='{item['caption']}' class='wildlife-photo'>")
    html_lines.append(f"    <figcaption class='caption'>{item['caption']}</figcaption>")
    html_lines.append("  </figure>")

html_lines.append("</div>")
html_lines.append("</body></html>")

os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(html_lines))

print(f"Recent photos page generated at {output_file}")

# =========================
# Save JSON for slideshow
# =========================
json_path = "recent_photos.json"  # save directly in photography root
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(recent_photos_data, f, indent=2)

print(f"Saved recent photos JSON to {json_path}")