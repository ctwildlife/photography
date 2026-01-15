import os
import shutil
import subprocess

def sort_megafolder():
    leaf_albums = get_leaf_album_folders(ALBUMS_ROOT)

    print("Leaf albums found:")
    for name in sorted(leaf_albums):
        print(f"  - {name}")

    for filename in os.listdir(SOURCE_FOLDER):
        if not filename.lower().endswith(SUPPORTED_EXTENSIONS):
            continue

        src_path = os.path.join(SOURCE_FOLDER, filename)
        tags = get_exif_tags(src_path)

        if not tags:
            continue

        for tag in tags:
            if tag in leaf_albums:
                dest_dir = leaf_albums[tag]
                dest_path = os.path.join(dest_dir, filename)

                if not os.path.exists(dest_path):
                    shutil.copy2(src_path, dest_path)

                print(f"Copied {filename} → {tag}")
