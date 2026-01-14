import os
from PIL import Image
from datetime import datetime
import subprocess
import re

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
# Find gallery folders
# =========================
def find_gallery_folders(base_path):
    gallery_folders = []
    for root, dirs, files in os.walk(base_path):
        images = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        if images:
            gallery_folders.append(root)
    return gallery_folders

# =========================
# Get images in a folder (non-recursive)
# =========================
def get_images_in_folder(folder):
    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

# =========================
# Get EXIF caption
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
# Italicize Latin names in parentheses
# =========================
def italicize_latin_names(caption):
    if not caption:
        return caption
    return re.sub(r"\(([^)]+)\)", r"(<em>\1</em>)", caption)

# =========================
# Get EXIF DateTimeOriginal
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
photos_base = "photos"
web_base = "photos_web"
workspace_root = r"C:\Users\Colin Tiernan\Documents\GitHub\photography"
pages_base = os.path.join(workspace_root, "pages")
os.makedirs(pages_base, exist_ok=True)

# =========================
# Manual nav entries
# =========================
manual_nav = [
    {"title": "Home", "url": "/photography/pages/index.html"},
    #{"title": "About", "url": "/photography/pages/about.html"},
]

# =========================
# Build gallery model
# =========================
gallery_folders = find_gallery_folders(photos_base)
galleries = []

for folder in gallery_folders:
    images = get_images_in_folder(folder)
    if not images:
        continue

    rel_path = os.path.relpath(folder, photos_base)
    path_parts = rel_path.split(os.sep)

    gallery = {
        "folder": folder,
        "rel_path": rel_path,
        "path_parts": path_parts,
        "slug": "-".join(path_parts),
        "title": path_parts[-1].replace("-", " ").title(),
        "images": images
    }
    galleries.append(gallery)

print("\nDetected galleries:")
for g in galleries:
    print(f"- {g['slug']} ({len(g['images'])} images)")

# =========================
# Build nav tree from galleries
# =========================
def build_nav_tree(galleries):
    tree = {}
    for g in galleries:
        node = tree
        for part in g['path_parts']:
            if part not in node:
                node[part] = {}
            node = node[part]
        node['_slug'] = g['slug']
    return tree

def nav_html_from_tree(tree):
    html = "<ul class='nav'>\n"
    def recurse(subtree):
        s = "<ul>\n"
        for key, value in sorted(subtree.items()):
            if key == '_slug':
                continue
            slug = value.get('_slug')
            if slug:
                s += f"<li><a href='/photography/pages/{slug}.html'>{key.title()}</a>"
            else:
                s += f"<li>{key.title()}"
            children = {k:v for k,v in value.items() if k != '_slug'}
            if children:
                s += recurse(children)
            s += "</li>\n"
        s += "</ul>\n"
        return s
    html += recurse(tree)
    html += "</ul>\n"
    return html

# Generate final nav HTML
tree = build_nav_tree(galleries)
dynamic_nav_html = nav_html_from_tree(tree)

manual_html = "<ul class='nav'>\n"
for item in manual_nav:
    manual_html += f"  <li><a href='{item['url']}'>{item['title']}</a></li>\n"
manual_html += "</ul>\n"

nav_html = manual_html + dynamic_nav_html

# =========================
# Generate HTML pages
# =========================
for g in galleries:
    images = g["images"]
    images.sort(key=lambda p: get_date_taken(p) or "", reverse=True)

    html_lines = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        f"    <title>{g['title']}</title>",
        "    <link rel='stylesheet' href='/photography/css/style.css'>",
        "</head>",
        "<body>",
        nav_html,
        f"<h1>{g['title']}</h1>",
        "<div class='gallery'>"
    ]

    for orig_path in images:
        img_file = os.path.basename(orig_path)
        web_path = os.path.join(web_base, g["slug"], img_file)

        resize_for_web_once(orig_path, web_path)

        caption = get_exif_caption(orig_path)
        if not caption:
            caption = os.path.splitext(img_file)[0].replace("-", " ").replace("_", " ").capitalize()
        else:
            caption = italicize_latin_names(caption)

        alt_text = caption.split(".")[0].strip()
        img_src = f"/photography/{web_base}/{g['slug']}/{img_file}"

        html_lines.append("  <figure class='photo-block'>")
        html_lines.append(f"    <img src='{img_src}' alt='{alt_text}' class='wildlife-photo'>")
        html_lines.append(f"    <figcaption class='caption'>{caption}</figcaption>")
        html_lines.append("  </figure>")

    html_lines.append("</div>")
    html_lines.append("</body></html>")

    out_file = os.path.join(pages_base, f"{g['slug']}.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))

    print(f"Generated {g['slug']}.html")

print("All galleries generated successfully.")
