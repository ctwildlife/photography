import os
import re
import json
import html
import subprocess
from urllib.parse import quote
from PIL import Image, ImageOps

# =========================
# Paths and settings
# =========================
workspace_root = r"C:\Users\Colin Tiernan\Documents\GitHub\photography"

# Source photos live OUTSIDE website-photos, so generate_galleries.py never sees them.
photojournalism_source = r"C:\Users\Colin Tiernan\Desktop\photojournalism"

# Web copies get their own folder, separate from photos_web.
web_base = "photojournalism_web"

pages_base = os.path.join(workspace_root, "pages")
nav_include_path = os.path.join(workspace_root, "includes", "nav.html")

LANDING_FILENAME = "more-photojournalism.html"

# Order here = order of the tiles. "folder" is the folder name on your Desktop.
SECTIONS = [
    {"folder": "environment", "title": "Environment", "focus": "50% 37%"},
    {"folder": "features",    "title": "Features",    "focus": "50% 50%"},
    {"folder": "government",  "title": "Government",  "focus": "10% 50%"},
    {"folder": "dailies",     "title": "Dailies",     "focus": "50% 30%"},
]

MAX_SIZE = (2400, 2400)   # long edge, in pixels
TARGET_MB = 1.5           # max size of each web copy
IMAGE_EXTS = (".jpg", ".jpeg", ".png")
HEADLINE_SEPARATOR = " | "

# =========================
# Page templates
# =========================
HEAD_COMMON = """<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="/photography/css/style.css">
<link rel="icon" type="image/png" sizes="32x32" href="/photography/public/favicon.png">
<link rel="icon" type="image/png" sizes="16x16" href="/photography/public/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/photography/public/apple-touch-icon.png">"""

LANDING_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
%%HEAD%%
<title>Photojournalism</title>
</head>
<body>
%%NAV%%
<main class="pj-main">
  <h1>Photojournalism</h1>
  <div class="pj-grid">
%%TILES%%
  </div>
</main>
</body>
</html>
"""

GALLERY_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
%%HEAD%%
<title>%%TITLE%% | Photojournalism</title>
</head>
<body class="pjg-page">
%%NAV%%
<div class="pjg-viewer">
  <button class="pjg-arrow" id="pjg-prev" aria-label="Previous photo">
    <svg viewBox="0 0 24 24" aria-hidden="true"><polyline points="15 4 7 12 15 20"/></svg>
  </button>
  <div class="pjg-stage">
    <div class="pjg-frame" id="pjg-frame">
      <img id="pjg-img" alt=""/>
      <div class="pjg-caption" id="pjg-caption">
        <div class="pjg-headline" id="pjg-headline"></div>
        <div class="pjg-text" id="pjg-text"></div>
      </div>
    </div>
  </div>
  <button class="pjg-arrow" id="pjg-next" aria-label="Next photo">
    <svg viewBox="0 0 24 24" aria-hidden="true"><polyline points="9 4 17 12 9 20"/></svg>
  </button>
</div>

<script>
  var photos = %%PHOTOS%%;

  var idx = 0;
  var img = document.getElementById("pjg-img");
  var cap = document.getElementById("pjg-caption");
  var head = document.getElementById("pjg-headline");
  var text = document.getElementById("pjg-text");
  var frame = document.getElementById("pjg-frame");

  img.addEventListener("load", function () { img.style.opacity = 1; });

  function preload(i) {
    var n = (i + photos.length) % photos.length;
    var p = new Image();
    p.src = photos[n].src;
  }

  function show(i) {
    idx = (i + photos.length) % photos.length;
    var p = photos[idx];
    img.style.opacity = 0;
    img.src = p.src;
    img.alt = p.headline || p.caption;
    head.textContent = p.headline;
    text.textContent = p.caption;
    cap.style.display = (p.headline || p.caption) ? "" : "none";
    frame.classList.remove("show-caption");
    preload(idx + 1);
    preload(idx - 1);
  }

  document.getElementById("pjg-prev").addEventListener("click", function () { show(idx - 1); });
  document.getElementById("pjg-next").addEventListener("click", function () { show(idx + 1); });

  document.addEventListener("keydown", function (e) {
    if (e.key === "ArrowLeft") show(idx - 1);
    if (e.key === "ArrowRight") show(idx + 1);
  });

  var startX = null;
  frame.addEventListener("touchstart", function (e) { startX = e.touches[0].clientX; }, { passive: true });
  frame.addEventListener("touchend", function (e) {
    if (startX === null) return;
    var dx = e.changedTouches[0].clientX - startX;
    startX = null;
    if (Math.abs(dx) > 50) show(dx > 0 ? idx - 1 : idx + 1);
  });

  if (window.matchMedia("(hover: none)").matches) {
    frame.addEventListener("click", function () { frame.classList.toggle("show-caption"); });
  }

  show(0);
</script>
</body>
</html>
"""

# =========================
# Helper functions
# =========================

def natural_key(path):
    name = os.path.basename(path).lower()
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", name)]

def get_images_in_folder(folder):
    files = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(IMAGE_EXTS)
    ]
    return sorted(files, key=natural_key)

def web_filename(original_path):
    return os.path.splitext(os.path.basename(original_path))[0] + ".jpg"

def resize_for_web_once(original_path, web_path):
    if os.path.exists(web_path):
        original_mtime = os.path.getmtime(original_path)
        web_mtime = os.path.getmtime(web_path)
        size_ok = os.path.getsize(web_path) <= TARGET_MB * 1024 * 1024
        if web_mtime >= original_mtime and size_ok:
            return
    os.makedirs(os.path.dirname(web_path), exist_ok=True)
    try:
        img = Image.open(original_path)
        img = ImageOps.exif_transpose(img)
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
        quality = 90
        size_mb = 0
        while quality >= 30:
            img.save(web_path, format="JPEG", quality=quality, optimize=True)
            size_mb = os.path.getsize(web_path) / (1024 * 1024)
            if size_mb <= TARGET_MB:
                break
            quality -= 5
        print(f"  Created web image: {web_path} ({size_mb:.2f} MB, quality={quality})")
    except Exception as e:
        print(f"  Error resizing {original_path}: {e}")

def get_metadata_batch(image_paths, batch_size=150):
    metadata = {}
    for i in range(0, len(image_paths), batch_size):
        chunk = image_paths[i:i + batch_size]
        try:
            result = subprocess.run(
                ["exiftool", "-j", "-Description", *chunk],
                capture_output=True, text=True, encoding="utf-8", timeout=60
            )
            for entry in json.loads(result.stdout):
                metadata[os.path.normpath(entry["SourceFile"])] = entry
        except Exception as e:
            print(f"  Batch ExifTool error: {e}", flush=True)
    return metadata

def resolve_caption(entry):
    return str(entry.get("Description") or "").strip()

def split_headline(caption):
    if HEADLINE_SEPARATOR in caption:
        headline, body = caption.split(HEADLINE_SEPARATOR, 1)
        return headline.strip(), body.strip()
    return "", caption

def read_nav():
    if os.path.exists(nav_include_path):
        with open(nav_include_path, "r", encoding="utf-8") as f:
            return f.read()
    print("WARNING: includes/nav.html not found. Run generate_galleries.py first. Pages will have no nav.")
    return ""

def write_page(filename, content):
    os.makedirs(pages_base, exist_ok=True)
    out_path = os.path.join(pages_base, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {filename}")

# =========================
# Main
# =========================

def main():
    nav_html = read_nav()
    landing_url = f"/photography/pages/{LANDING_FILENAME}"
    tiles = []

    for section in SECTIONS:
        folder = os.path.join(photojournalism_source, section["folder"])
        title = section["title"]

        if not os.path.isdir(folder):
            print(f"Skipping {title}: folder not found at {folder}")
            continue

        images = get_images_in_folder(folder)
        if not images:
            print(f"Skipping {title}: no photos in {folder}")
            continue

        print(f"Fetching captions for {title} ({len(images)} photos)...", flush=True)
        metadata = get_metadata_batch(images)

        photos = []
        cover_src = None

        for orig_path in images:
            wname = web_filename(orig_path)
            web_path = os.path.join(workspace_root, web_base, section["folder"], wname)
            resize_for_web_once(orig_path, web_path)

            caption = resolve_caption(metadata.get(os.path.normpath(orig_path), {}))
            if not caption:
                print(f"  NO CAPTION: {os.path.basename(orig_path)}")

            src = f"/photography/{web_base}/{section['folder']}/{quote(wname)}"
            headline, body = split_headline(caption)
            photos.append({"src": src, "headline": headline, "caption": body})

            if cover_src is None and "cover" in os.path.basename(orig_path).lower():
                cover_src = src

        if cover_src is None:
            cover_src = photos[0]["src"]
            print(f"  No file with 'cover' in its name for {title}; using the first photo.")

        photos_json = json.dumps(photos, ensure_ascii=False).replace("</", "<\\/")
        page_name = f"photojournalism-{section['folder']}.html"

        gallery_html = (GALLERY_TEMPLATE
                        .replace("%%HEAD%%", HEAD_COMMON)
                        .replace("%%TITLE%%", html.escape(title))
                        .replace("%%NAV%%", nav_html)
                        .replace("%%BACKURL%%", landing_url)
                        .replace("%%PHOTOS%%", photos_json))
        write_page(page_name, gallery_html)

        focus = section.get("focus", "50% 50%")
        tiles.append(
            f'    <a class="pj-tile" href="/photography/pages/{page_name}">\n'
            f'      <img src="{cover_src}" alt="{html.escape(title)} photojournalism" style="object-position: {focus};">\n'
            f'      <h2>{html.escape(title)}</h2>\n'
            f'    </a>'
        )

    landing_html = (LANDING_TEMPLATE
                    .replace("%%HEAD%%", HEAD_COMMON)
                    .replace("%%NAV%%", nav_html)
                    .replace("%%TILES%%", "\n".join(tiles)))
    write_page(LANDING_FILENAME, landing_html)

    print("Photojournalism pages generated successfully.")

if __name__ == "__main__":
    main()