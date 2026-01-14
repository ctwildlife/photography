import os
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
import subprocess
import re

# =========================
# Base paths
# =========================
photos_base = "photos"  # originals
web_base = "photos_web" # resized copies for web

workspace_root = r"C:\Users\Colin Tiernan\Documents\GitHub\photography"
pages_base = os.path.join(workspace_root, "pages")
os.makedirs(pages_base, exist_ok=True)

# =========================
# Function to ...
# =========================

def find_gallery_folders(base_path):
    """
    Returns a list of folders that contain image files.
    """
    gallery_folders = []

    for root, dirs, files in os.walk(base_path):
        images = [
            f for f in files
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        if images:
            gallery_folders.append(root)

    return gallery_folders

gallery_folders = find_gallery_folders(photos_base)

print("Detected gallery folders:")
for folder in gallery_folders:
    print(" -", os.path.relpath(folder, photos_base))
