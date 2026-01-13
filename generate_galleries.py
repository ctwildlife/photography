import os
from PIL import Image
from PIL.ExifTags import TAGS

#git add Pages/* or git add . 
#git commit -m "Updated gallery with new photos" 
#git push 
#python generate_galleries

# =========================
# Function to get image caption from EXIF metadata
# =========================
def get_exif_caption(image_path):
    """Read EXIF metadata to get image caption from common fields."""
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        if not exif_data:
            return None

        exif = {TAGS.get(tag_id, tag_id): value for tag_id, value in exif_data.items()}

        for tag_name in ["ImageDescription", "XPTitle", "UserComment", "XPComment"]:
            if tag_name in exif:
                value = exif[tag_name]
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

# =========================
# Function to get EXIF DateTimeOriginal for sorting
# =========================
def get_date_taken(img_path):
    """Return the DateTimeOriginal from EXIF, or None if missing."""
    try:
        img = Image.open(img_path)
        exif_data = img._getexif()
        if not exif_data:
            return None
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "DateTimeOriginal":
                return value  # format "YYYY:MM:DD HH:MM:SS"
    except:
        return None

# =========================
# Base paths
# =========================
photos_base = "photos"     # folder where your images live
pages_base = "pages"       # folder for generated HTML
categories = ["birds", "mammals", "herps", "landscapes", "arthropods"]

# =========================
# Loop over categories
# =========================
for category in categories:
    folder = os.path.join(photos_base, category)
    images = [f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))]

    # -------------------------
    # Sort images newest-first by EXIF DateTimeOriginal
    # -------------------------
    images.sort(key=lambda f: get_date_taken(os.path.join(folder, f)) or "", reverse=True)

    # -------------------------
    # Begin HTML
    # -------------------------
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
            caption = os.path.splitext(img_file)[0].replace("-", " ").replace("_", " ").capitalize()

        # Alt = species (text before first period)
        alt_text = caption.split(".")[0].strip()

        # Absolute path for GitHub Pages
        img_src = f"/photography/photos/{category}/{img_file}"

        # Generate HTML matching your CSS conventions
        html_lines.append("  <figure class='photo-block'>")
        html_lines.append(f"    <img src='{img_src}' alt='{alt_text}' class='wildlife-photo'>")
        html_lines.append(f"    <figcaption class='caption'>{caption}</figcaption>")
        html_lines.append("  </figure>")

    # -------------------------
    # Close HTML
    # -------------------------
    html_lines.append("</div>")  # close gallery
    html_lines.append("</body></html>")

    # -------------------------
    # Write to file
    # -------------------------
    out_file = os.path.join(pages_base, f"{category}.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))

    print(f"Generated gallery for {category} with {len(images)} images.")
