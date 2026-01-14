import os
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
import subprocess

#git add Pages/* or git add . 
#git commit -m "Updated gallery with new photos" 
#git push 
#python generate_galleries

# =========================
# Resize function
# =========================
def resize_for_web_once(original_path, web_path, max_size=(1920, 1920)):
    """
    Resize an image for the web if it doesn't exist yet or is larger than max_size.
    """
    if os.path.exists(web_path):
        img = Image.open(web_path)
        if img.width <= max_size[0] and img.height <= max_size[1]:
            # Already resized
            return

    # Ensure the folder exists
    os.makedirs(os.path.dirname(web_path), exist_ok=True)

    # Resize
    try:
        img = Image.open(original_path)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        img.save(web_path, format="JPEG", quality=85, optimize=True)
        print(f"Created/resized web image: {web_path}")
    except Exception as e:
        print(f"Error resizing {original_path}: {e}")

# =========================
# Function to get image caption from EXIF metadata
# =========================
def get_exif_caption(image_path):
    try:
        result = subprocess.run(
            ["exiftool", "-Description", "-s3", image_path],
            capture_output=True,
            text=True
        )
        caption = result.stdout.strip()
        return caption if caption else None
    except Exception as e:
        print(f"ExifTool error on {image_path}: {e}")
        return None

# =========================
# Function to get EXIF DateTimeOriginal
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
        date_part = date_str.split(" ")[0]
        return datetime.strptime(date_part, "%Y:%m:%d").date()
    except Exception as e:
        print(f"ExifTool error on {image_path}: {e}")
        return None

# =========================
# Base paths
# =========================
photos_base = "photos"  # originals
web_base = "photos_web" # resized copies for web

workspace_root = r"C:\Users\Colin Tiernan\Documents\GitHub\photography"
pages_base = os.path.join(workspace_root, "pages")
os.makedirs(pages_base, exist_ok=True)

categories = ["birds", "mammals", "herps", "landscapes", "arthropods"]

# =========================
# Loop over categories
# =========================
for category in categories:
    folder = os.path.join(photos_base, category)
    images = [f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))]

    # Sort by DateTimeOriginal
    images.sort(key=lambda f: get_date_taken(os.path.join(folder, f)) or "", reverse=True)

    # Begin HTML
    html_lines = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        f"    <title>{category.capitalize()} Gallery</title>",
        "    <link rel='stylesheet' href='/photography/css/style.css'>",
        "</head>",
        "<body>",
        f"<h1>{category.capitalize()}</h1>",
        "<div class='gallery'>"
    ]

    for img_file in images:
        orig_path = os.path.join(folder, img_file)
        web_path = os.path.join(web_base, category, img_file)

        # Resize if needed
        resize_for_web_once(orig_path, web_path)

        # Caption
        caption = get_exif_caption(orig_path)
        if not caption:
            caption = os.path.splitext(img_file)[0].replace("-", " ").replace("_", " ").capitalize()

        alt_text = caption.split(".")[0].strip()
        img_src = f"/photography/{web_base}/{category}/{img_file}"  # use resized copy

        # HTML
        html_lines.append("  <figure class='photo-block'>")
        html_lines.append(f"    <img src='{img_src}' alt='{alt_text}' class='wildlife-photo'>")
        html_lines.append(f"    <figcaption class='caption'>{caption}</figcaption>")
        html_lines.append("  </figure>")

    # Close HTML
    html_lines.append("</div>")
    html_lines.append("</body></html>")

    # Write file
    out_file = os.path.join(pages_base, f"{category}.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))
    print(f"Generated {category}.html at {out_file}")

print("All galleries generated successfully.")
