import os
import re
import subprocess
from datetime import datetime

# =========================
# Config
# =========================
folder = r"C:\Users\Colin Tiernan\Desktop\website-photos\landscapes\cellphone-landscapes"

PREVIEW_ONLY = False

# =========================
# Helpers
# =========================

def get_all_images(base_path):
    images = []
    for root, dirs, files in os.walk(base_path):
        for f in files:
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                images.append(os.path.join(root, f))
    return images

def extract_date_from_filename(filename):
    # Matches leading 6 digits, e.g. "021222" at the start of the filename
    match = re.match(r'^(\d{2})(\d{2})(\d{2})-', filename)
    if not match:
        return None
    month, day, year = match.groups()
    try:
        full_year = 2000 + int(year)  # assumes all photos are 2000s
        date_obj = datetime(full_year, int(month), int(day))
        return date_obj.strftime("%B %#d, %Y")  # Windows-style day-without-leading-zero
    except ValueError:
        return None

def get_existing_description(image_path):
    result = subprocess.run(
        ["exiftool", "-Description", "-s3", image_path],
        capture_output=True, text=True
    )
    return result.stdout.strip()

def set_exif_description(image_path, new_description):
    subprocess.run(
        ["exiftool", f"-Description={new_description}", "-overwrite_original", image_path],
        capture_output=True, text=True
    )

# =========================
# Main
# =========================
images = get_all_images(folder)
print(f"Found {len(images)} image(s) to check.\n")

for img_path in images:
    filename = os.path.basename(img_path)
    date_str = extract_date_from_filename(filename)

    if not date_str:
        print(f"SKIP (no date found in filename): {filename}")
        continue

    existing_description = get_existing_description(img_path)

    if not existing_description:
        print(f"SKIP (no existing Description to append to): {filename}")
        continue

    if existing_description.rstrip(".").endswith(date_str):
        print(f"ALREADY DONE, skipping: {filename}")
        continue

    combined = f"{existing_description.rstrip('.')}. {date_str}."

    print(f"{filename} -> \"{combined}\"")

    if not PREVIEW_ONLY:
        set_exif_description(img_path, combined)
        print("  -> Written to file.")