import os

# =========================
# Paths
# =========================
workspace_root = r"C:\Users\Colin Tiernan\Documents\GitHub\photography"
pages_dir = workspace_root  # Now points to the root of your repo
nav_include_path = os.path.join(workspace_root, "includes", "nav.html")

# =========================
# Function to Inject Nav into Index Page
# =========================
def inject_nav_into_index():
    page_file = "index.html"
    page_path = os.path.join(pages_dir, page_file)
    print(f"Looking for {page_file} at {page_path}")  # Debugging line
    
    if not os.path.exists(page_path):
        print(f"Page file {page_file} not found, skipping.")
        return

    with open(page_path, "r", encoding="utf-8") as f:
        page_content = f.read()

    # Read the nav content from includes/nav.html
    if os.path.exists(nav_include_path):
        with open(nav_include_path, "r", encoding="utf-8") as f:
            nav_html = f.read()
    else:
        print(f"WARNING: {nav_include_path} not found. Nav will be missing.")
        return

    # Inject the nav into the page by replacing the placeholder
    updated_page_content = page_content.replace("<!-- NAV -->", nav_html)

    if updated_page_content == page_content:
        print("No changes made to the file. The placeholder wasn't found.")
        return

    # Save the updated content back to the page
    with open(page_path, "w", encoding="utf-8") as f:
        f.write(updated_page_content)
    print(f"Injected nav into {page_file}")

# =========================
# Only inject nav into Index Page
# =========================
inject_nav_into_index()

print("Nav injection complete for index.html.")
