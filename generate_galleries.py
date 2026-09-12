import os
from PIL import Image
from datetime import datetime, date
import subprocess
import re
import json
from nav import manual_nav, build_nav_tree, generate_nav_html

print("SILHOUETTE CODE VERSION - TEST MARKER")

# =========================
# Paths
# =========================
workspace_root = r"C:\Users\Colin Tiernan\Documents\GitHub\photography"
photos_base = r"C:\Users\Colin Tiernan\Desktop\website-photos"
web_base = "photos_web"

showcase_photos = []
silhouette_photos = []
fave_photos = []
portrait_photos = []
birds_in_flight_photos = []

KEYWORD_GALLERIES = [
    {"match": ["showcase"],              "photos": showcase_photos,        "title": "Showcase",         "filename": "more-showcase.html"},
    {"match": ["silhouette"],            "photos": silhouette_photos,      "title": "Silhouettes",      "filename": "more-silhouettes.html"},
    {"match": ["faves"],                 "photos": fave_photos,            "title": "Faves", "nav_title": "Favorites", "filename": "more-faves.html"},
    {"match": ["portrait", "portraits"], "photos": portrait_photos,        "title": "Portraits",        "filename": "more-portraits.html"},
    {"match": ["birds in flight", "bif"],"photos": birds_in_flight_photos, "title": "Birds in flight",  "filename": "more-birds-in-flight.html"},
]

pages_base = os.path.join(workspace_root, "pages")
includes_dir = os.path.join(workspace_root, "includes")

os.makedirs(pages_base, exist_ok=True)
os.makedirs(includes_dir, exist_ok=True)

# =========================
# Helper functions
# =========================

def resize_for_web_once(original_path, web_path, max_size=(1920, 1920), target_mb=1.0):
    if os.path.exists(web_path):
        original_mtime = os.path.getmtime(original_path)
        web_mtime = os.path.getmtime(web_path)
        web_size_ok = os.path.getsize(web_path) <= target_mb * 1024 * 1024
        if web_mtime >= original_mtime and web_size_ok:
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
        elif dirs and not images:
            continue
    return gallery_folders

def get_images_in_folder(folder):
    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

def count_images_recursive(folder):
    return sum(
        1
        for root, dirs, files in os.walk(folder)
        for f in files
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    )

MONTHS = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}

def get_date_from_caption(caption):
    if not caption:
        return None
    match = re.search(r'([A-Za-z]+)\.?\s+(\d{1,2}),\s+(\d{4})', caption)
    if not match:
        return None
    month_str, day_str, year_str = match.groups()
    month = MONTHS.get(month_str.lower().rstrip("."))
    if not month:
        return None
    try:
        return date(int(year_str), month, int(day_str))
    except ValueError:
        return None

def italicize_latin_names(caption):
    if not caption:
        return caption
    return re.sub(r"\(([^)]+)\)", r"(<em>\1</em>)", caption)

# -------------------------
# Batched EXIF metadata (one exiftool call per chunk, not per photo per tag)
# -------------------------

def get_metadata_batch(image_paths, batch_size=150):
    metadata = {}
    for i in range(0, len(image_paths), batch_size):
        chunk = image_paths[i:i + batch_size]
        try:
            result = subprocess.run(
                ["exiftool", "-j", "-Description", "-Keywords", "-DateTimeOriginal", *chunk],
                capture_output=True, text=True, timeout=60
            )
            entries = json.loads(result.stdout)
            for entry in entries:
                metadata[os.path.normpath(entry["SourceFile"])] = entry
        except Exception as e:
            print(f"Batch ExifTool error: {e}", flush=True)
    return metadata

def resolve_caption(entry):
    caption = (entry.get("Description") or "").strip()
    return caption if caption else None

def resolve_keywords(entry):
    kw = entry.get("Keywords")
    if not kw:
        return []
    if isinstance(kw, list):
        return [k.strip().lower() for k in kw]
    return [k.strip().lower() for k in str(kw).split(",")]

def resolve_date(entry):
    caption_date = get_date_from_caption(resolve_caption(entry))
    if caption_date:
        return caption_date
    date_str = entry.get("DateTimeOriginal")
    if date_str:
        try:
            return datetime.strptime(date_str.split(" ")[0], "%Y:%m:%d").date()
        except ValueError:
            pass
    return None

# =========================
# Build galleries & nav
# =========================

gallery_order = {
    "Birds": 1,
    "Mammals": 2,
    "Landscapes": 3,
    "More": 4,
}

gallery_folders = find_gallery_folders(photos_base)
galleries = []

for folder in gallery_folders:
    images = get_images_in_folder(folder)
    rel_path = os.path.relpath(folder, photos_base)
    path_parts = rel_path.split(os.sep)

    galleries.append({
        "folder": folder,
        "rel_path": rel_path,
        "path_parts": path_parts,
        "slug": "-".join(path_parts),
        "title": path_parts[-1].replace("-", " ").capitalize(),
        "images": images,
        "image_count": count_images_recursive(folder)
    })

galleries.sort(key=lambda g: gallery_order.get(g['title'], 999))

print("Gallery order by custom defined order:")
for g in galleries:
    print(f"{g['title']}: {g['image_count']}")

nav_tree = build_nav_tree(galleries)
nav_html = generate_nav_html(manual_nav, nav_tree, gallery_order, keyword_galleries=KEYWORD_GALLERIES)

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
    print(f"Fetching metadata for {g['title']} ({len(images)} photos)...", flush=True)
    metadata = get_metadata_batch(images)

    def lookup(p):
        return metadata.get(os.path.normpath(p), {})

    for p in images:
        d = resolve_date(lookup(p))
        if d is None:
            print(f"MISSING/BAD DATE: {p}")

    images.sort(key=lambda p: resolve_date(lookup(p)) or date.min, reverse=True)

    html_lines = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        f"    <title>{g['title']}</title>",
        "    <link rel='stylesheet' href='/photography/css/style.css'>",
        "    <link rel='icon' type='image/png' sizes='32x32' href='/photography/public/favicon.png'>",
        "    <link rel='icon' type='image/png' sizes='16x16' href='/photography/public/favicon-16x16.png'>",
        "    <link rel='apple-touch-icon' sizes='180x180' href='/photography/public/apple-touch-icon.png'>",
        "</head>",
        "<body>",
        nav_html,
        f"<h1>{g['title']}</h1>",
        "<div class='gallery'>"
    ]

    for orig_path in images:
        img_file = os.path.basename(orig_path)
        print(f"Processing: {orig_path}", flush=True)
        web_path = os.path.join(web_base, g["slug"], img_file)
        resize_for_web_once(orig_path, web_path)

        entry = lookup(orig_path)

        caption = resolve_caption(entry) or img_file.rsplit(".", 1)[0].replace("-", " ").replace("_", " ").capitalize()
        caption = italicize_latin_names(caption)
        alt_text = caption.split(".")[0].strip()
        img_src = f"/photography/{web_base}/{g['slug']}/{img_file}"

        date_taken = resolve_date(entry)
        date_str = date_taken.isoformat() if date_taken else ""

        keywords = resolve_keywords(entry)

        photo_data = {
            "caption": caption,
            "url": img_src,
            "date": date_str
        }

        all_photos.append(photo_data)

        photo_entry = {
            "img_src": img_src,
            "alt_text": alt_text,
            "caption": caption,
            "date": date_taken
        }

        for gallery in KEYWORD_GALLERIES:
            if any(k in keywords for k in gallery["match"]):
                gallery["photos"].append(photo_entry)

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

showcase_json_path = os.path.join(workspace_root, "showcase.json")
with open(showcase_json_path, "w", encoding="utf-8") as f:
    json.dump([
        {
            "caption": p["caption"],
            "url": p["img_src"],
            "date": p["date"].isoformat() if p["date"] else ""
        }
        for p in showcase_photos
    ], f, indent=2, ensure_ascii=False)
print(f"Showcase JSON written to {showcase_json_path}")

# =========================
# Keyword-filtered gallery pages
# =========================

def write_keyword_gallery(title, photos, out_filename):
    photos = sorted(photos, key=lambda p: p["date"] or date.min, reverse=True)

    lines = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        f"    <title>{title}</title>",
        "    <link rel='stylesheet' href='/photography/css/style.css'>",
        "    <link rel='icon' type='image/png' sizes='32x32' href='/photography/public/favicon.png'>",
        "    <link rel='icon' type='image/png' sizes='16x16' href='/photography/public/favicon-16x16.png'>",
        "    <link rel='apple-touch-icon' sizes='180x180' href='/photography/public/apple-touch-icon.png'>",
        "</head>",
        "<body>",
        nav_html,
        f"<h1>{title}</h1>",
        "<div class='gallery'>"
    ]

    for item in photos:
        lines.append("  <figure class='photo-block'>")
        lines.append(
            f"    <img src='{item['img_src']}' alt='{item['alt_text']}' class='wildlife-photo' loading='lazy'>")
        lines.append(f"    <figcaption class='caption'>{item['caption']}</figcaption>")
        lines.append("  </figure>")

    lines.append("</div></body></html>")

    out_path = os.path.join(pages_base, out_filename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Generated {out_filename} with {len(photos)} photos")


for gallery in KEYWORD_GALLERIES:
    write_keyword_gallery(gallery["title"], gallery["photos"], gallery["filename"])

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