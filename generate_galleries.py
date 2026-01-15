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
# Get images in a folder
# =========================
def get_images_in_folder(folder):
    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

# =========================
# EXIF functions
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

def italicize_latin_names(caption):
    if not caption:
        return caption
    return re.sub(r"\(([^)]+)\)", r"(<em>\1</em>)", caption)

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
# Paths
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
    {"title": "Home", "url": "/photography/index.html"},
     {"title": "Recent", "url": "/photography/pages/recent.html"},
]

# =========================
# Build galleries
# =========================
gallery_folders = find_gallery_folders(photos_base)
galleries = []
for folder in gallery_folders:
    images = get_images_in_folder(folder)
    if not images:
        continue
    rel_path = os.path.relpath(folder, photos_base)
    path_parts = rel_path.split(os.sep)
    galleries.append({
        "folder": folder,
        "rel_path": rel_path,
        "path_parts": path_parts,
        "slug": "-".join(path_parts),
        "title": path_parts[-1].replace("-", " ").title(),
        "images": images
    })

# =========================
# Build nav tree
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

# =========================
# Render nav HTML with dropdown classes
# =========================
# =========================
# Render nav HTML with dropdown classes
# =========================
def generate_nav_html(manual_nav, gallery_tree):
    """
    Generate a single navbar with:
      - Manual links (e.g., Home) as top-level items
      - Gallery folders as dropdowns
    """
    def recurse(tree, level=0):
        html = "<ul class='dropdown-menu'>\n" if level > 0 else ""
        for key, value in sorted(tree.items()):
            if key == '_slug':
                continue
            children = {k:v for k,v in value.items() if k != '_slug'}
            slug = value.get('_slug')
            if children:
                html += f"<li class='dropdown'><a href='#'>{key.title()}</a>\n"
                html += recurse(children, level+1)
                html += "</li>\n"
            elif slug:
                html += f"<li><a href='/photography/pages/{slug}.html'>{key.title()}</a></li>\n"
        html += "</ul>\n" if level > 0 else ""
        return html

    # Top-level menu container: manual links + gallery dropdowns
    html = "<div class='navbar'>\n<ul class='menu'>\n"

    # Add manual links first
    for item in manual_nav:
        html += f"  <li><a href='{item['url']}'>{item['title']}</a></li>\n"

    # Add dynamic gallery links
    for key, value in sorted(gallery_tree.items()):
        children = {k:v for k,v in value.items() if k != '_slug'}
        slug = value.get('_slug')
        if children:
            html += f"<li class='dropdown'><a href='#'>{key.title()}</a>\n"
            html += recurse(children, level=1)
            html += "</li>\n"
        elif slug:
            html += f"<li><a href='/photography/pages/{slug}.html'>{key.title()}</a></li>\n"

    html += "</ul>\n</div>\n"
    return html

# =========================
# Combine manual + dynamic nav
# =========================
tree = build_nav_tree(galleries)
nav_html = generate_nav_html(manual_nav, tree)

# =========================
# Write shared nav include
# =========================
includes_dir = os.path.join(workspace_root, "includes")
os.makedirs(includes_dir, exist_ok=True)

nav_include_path = os.path.join(includes_dir, "nav.html")
with open(nav_include_path, "w", encoding="utf-8") as f:
    f.write(nav_html)

print(f"Nav written to {nav_include_path}")

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
