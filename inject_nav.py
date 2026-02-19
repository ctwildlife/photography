import os
import re

# =========================
# Paths
# =========================
workspace_root = r"C:\Users\Colin Tiernan\Documents\GitHub\photography"
nav_include_path = os.path.join(workspace_root, "includes", "nav.html")

# List of pages with their relative paths
pages_to_inject = [
    "index.html",  # root of repo
    os.path.join("pages", "more-contact.html"),  # pages folder
    os.path.join("pages", "more-flickr.html")
]

# =========================
# Function to Inject Nav into a Page (idempotent)
# =========================
def inject_nav_into_page(relative_page_path):
    page_path = os.path.join(workspace_root, relative_page_path)
    print(f"Looking for {relative_page_path} at {page_path}")  # Debugging
    
    if not os.path.exists(page_path):
        print(f"Page file {relative_page_path} not found, skipping.")
        return

    # Read page content
    with open(page_path, "r", encoding="utf-8") as f:
        page_content = f.read()

    # Read nav content
    if os.path.exists(nav_include_path):
        with open(nav_include_path, "r", encoding="utf-8") as f:
            nav_html = f.read()
    else:
        print(f"WARNING: {nav_include_path} not found. Nav will be missing.")
        return

    # Wrap nav in markers
    nav_html_wrapped = f"<!-- NAV_START -->\n{nav_html}\n<!-- NAV_END -->"

    # Replace existing markers if present
    if "<!-- NAV_START -->" in page_content and "<!-- NAV_END -->" in page_content:
        updated_page_content = re.sub(
            r'<!-- NAV_START -->.*<!-- NAV_END -->',
            nav_html_wrapped,
            page_content,
            flags=re.DOTALL
        )
    else:
        # Insert at placeholder or after <body> if markers not found
        if "<!-- NAV -->" in page_content:
            updated_page_content = page_content.replace("<!-- NAV -->", nav_html_wrapped)
        else:
            updated_page_content = page_content.replace(
                "<body>",
                f"<body>\n{nav_html_wrapped}"
            )

    # Write back only if changed
    if updated_page_content != page_content:
        with open(page_path, "w", encoding="utf-8") as f:
            f.write(updated_page_content)
        print(f"Injected/updated nav into {relative_page_path}")
    else:
        print(f"No changes made. Nav already up to date in {relative_page_path}.")

# =========================
# Run injection for all pages
# =========================
for page_file in pages_to_inject:
    inject_nav_into_page(page_file)

print("Nav injection complete for all specified pages.")
