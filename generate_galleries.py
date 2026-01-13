#git add Pages/* or git add .
#git commit -m "Updated gallery with new photos"
#git push

#python generate_galleries

# git add Pages/*
# git commit -m "Updated gallery with new photos"
# git push

# python generate_galleries.py

import os
from PIL import Image
from PIL.ExifTags import TAGS

# Base paths
photos_base = "photos"     # folder where your images live
pages_base = "pages"       # folder for generated HTML
categories = ["birds", "mammals", "herps", "landscapes", "arthropods"]

from PIL import Image
from PIL.ExifTags import TAGS

def get_exif_caption(image_path):
    """Read EXIF metadata to get image caption from common fields."""
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        if not exif_data:
            return None

        # Convert EXIF tag IDs to names
        exif = {TAGS.get(tag_id, tag_id): value for tag_id, value in exif_data.items()}

        # Look for common caption fields
        for tag_name in ["ImageDescription", "XPTitle", "UserComment", "XPComment"]:
            if tag_name in exif:
                value = exif[tag_name]
                # Decode bytes if needed (XP fields are usually UTF-16LE)
                if isinstance(value, bytes):
                    try:
                        value = value.decode("utf-16le").strip()
                    except:
                        value = value.decode("utf-8", errors="ignore").strip()
                return value.strip() if value else None

        return None

    except Exception as e:
        print(f"Warning: Could not read EXIF from {image_path}: {e}")
        return None

for category in categories:
    folder = os.path.join(photos_base, category)
    images = [f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))]

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
        img_path = os.path.join(folder, img_file)

        # Pull caption from EXIF metadata if available
        caption = get_exif_caption(img_path)
        if not caption:
            # Fallback to filename if no metadata
            caption = os.path.splitext(img_file)[0].replace("-", " ").replace("_", " ").capitalize()

        # Absolute path for GitHub Pages
        img_src = f"/photography/photos/{category}/{img_file}"
        alt_text = caption.split(".")[0].strip()  # alt can mirror caption or be customized

        # Generate HTML matching your CSS conventions
        html_lines.append("  <figure class='photo-block'>")
        html_lines.append(f"    <img src='{img_src}' alt='{alt_text}' class='wildlife-photo'>")
        html_lines.append(f"    <figcaption class='caption'>{caption}</figcaption>")
        html_lines.append("  </figure>")


    html_lines.append("</div>")  # close gallery
    html_lines.append("</body></html>")

    # Write HTML file
    out_file = os.path.join(pages_base, f"{category}.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))

    print(f"Generated gallery for {category} with {len(images)} images.")
