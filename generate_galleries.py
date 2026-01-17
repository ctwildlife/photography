import os
from PIL import Image
from datetime import datetime
import subprocess
import re
import json
from nav import manual_nav, build_nav_tree, generate_nav_html

# =========================
# Paths
# =========================
photos_base = "photos"
web_base = "photos_web"
workspace_root = r"C:\Users\Colin Tiernan\Documents\GitHub\photography"
pages_base = os.path.join(workspace_root, "pages")
includes_dir = os.path.join(workspace_root, "includes")

os.makedirs(pages_base, exist_ok=True)
os.makedirs(includes_dir, exist_ok=True)

# =========================
# Helper functions
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

def find_gallery_folders(base_path):
    gallery_folders = []
    for root, dirs, files in os.walk(base_path):
        images = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        if images:
            gallery_folders.append(root)
    return gallery_folders

def get_images_in_folder(folder):
    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

def get_exif_caption(image_path):
    try:
        result = subprocess.run(
            ["exiftool", "-Description", "-s3", image_path],
            capture_output=True, text=True
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
            capture_output=True, text=True
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
# Build galleries & nav
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

nav_tree = build_nav_tree(galleries)
nav_html = generate_nav_html(manual_nav, nav_tree)

# Write nav HTML to includes/nav.html for static pages
nav_include_path = os.path.join(includes_dir, "nav.html")
with open(nav_include_path, "w", encoding="utf-8") as f:
    f.write(nav_html)
print(f"Updated includes/nav.html with latest nav")

# =========================
# Generate gallery pages
# =========================

all_photos = []

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

        caption = get_exif_caption(orig_path) or os.path.splitext(img_file)[0].replace("-", " ").replace("_", " ").capitalize()
        caption = italicize_latin_names(caption)
        alt_text = caption.split(".")[0].strip()
        img_src = f"/photography/{web_base}/{g['slug']}/{img_file}"

        date_taken = get_date_taken(orig_path)
        date_str = date_taken.isoformat() if date_taken else ""

        all_photos.append({
            "caption": caption,
            "url": img_src,
            "date": date_str
        })

        html_lines.append("  <figure class='photo-block'>")
        html_lines.append(
        f"    <img src='{img_src}' alt='{alt_text}' class='wildlife-photo' loading='lazy'>")
        html_lines.append(f"    <figcaption class='caption'>{caption}</figcaption>")
        html_lines.append("  </figure>")

    html_lines.append("</div></body></html>")

    out_file = os.path.join(pages_base, f"{g['slug']}.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))
    print(f"Generated {g['slug']}.html")

# =========================
# Write photos_index.json
# =========================

json_path = os.path.join(workspace_root, "photos_index.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(all_photos, f, indent=2, ensure_ascii=False)
print(f"Photo index JSON written to {json_path}")

# =========================
# Generate search page
# =========================

search_html_lines = [
    "<!DOCTYPE html>",
    "<html lang='en'>",
    "<head>",
    "    <meta charset='UTF-8'>",
    "    <title>Search</title>",
    "    <link rel='stylesheet' href='/photography/css/style.css'>",
    "</head>",
    "<body>",
    nav_html,
    "<h1>Search</h1>",
    "<div class='search-container' style='text-align: center;'>",
    "  <p style='max-width: 400px; margin: 0 auto 1rem;'>",
    "    Use this to filter photos. For instance, type &ldquo;Wyoming&rdquo; to see all pictures taken in Wyoming.",
    "  </p>",
    "  <input type='text' id='searchBox' placeholder='Search photos ...' style='display: block; margin: 0 auto;'>",
    "</div>",
    "<div id='searchResults' class='gallery'></div>",
    "<script>",
    "fetch('/photography/photos_index.json')",
    "  .then(res => res.json())",
    "  .then(allPhotos => {",
    "    const searchBox = document.getElementById('searchBox');",
    "    const resultsDiv = document.getElementById('searchResults');",
    "    searchBox.addEventListener('input', () => {",
    "      const query = searchBox.value.toLowerCase();",
    "      const filtered = allPhotos",
    "        .filter(photo => photo.caption.toLowerCase().includes(query))",
    "        .sort((a, b) => new Date(b.date) - new Date(a.date));",
    "      resultsDiv.innerHTML = filtered.map(photo =>",
    "        `<figure class='photo-block'>` +",
    "        `<img src='${photo.url}' alt='${photo.caption}' class='wildlife-photo' loading='lazy'>` +",
    "        `<figcaption class='caption'>${photo.caption}</figcaption>` +",
    "        `</figure>`",
    "      ).join('');",
    "    });",
    "  });",
    "</script>",
    "</body>",
    "</html>"
]

search_out_file = os.path.join(pages_base, "search.html")
with open(search_out_file, "w", encoding="utf-8") as f:
    f.write("\n".join(search_html_lines))
print(f"Generated search.html with updated nav at {search_out_file}")

print("All galleries and search page generated successfully.")
