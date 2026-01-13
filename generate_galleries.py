#git add Pages/*
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

def get_exif_caption(image_path):
    """Read EXIF metadata to get image caption, fallback to None."""
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        if not exif_data:
            return None
        # Look for ImageDescription or XPTitle fields
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag in ["ImageDescription", "XPTitle"]:
                if isinstance(value, bytes):
                    value = value.decode('utf-16', errors='ignore')
                return value
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

        html_lines.append("  <div class='photo'>")
        html_lines.append(f"    <img src='{img_src}' alt='{alt_text}'>")
        html_lines.append(f"    <p>{caption}</p>")
        html_lines.append("  </div>")

    html_lines.append("</div>")  # close gallery
    html_lines.append("</body></html>")

    # Write HTML file
    out_file = os.path.join(pages_base, f"{category}.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))

    print(f"Generated gallery for {category} with {len(images)} images.")
