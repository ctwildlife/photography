import os
import re

# =========================
# Paths
# =========================
workspace_root = r"C:\Users\Colin Tiernan\Documents\GitHub\photography"
pages_dir = workspace_root  # Root of your repo
nav_include_path = os.path.join(workspace_root, "includes", "nav.html")

# =========================
# Function to Inject Nav into Index Page (idempotent)
# =========================
def inject_nav_into_index():
    page_file = "index.html"
    page_path = os.path.join(pages_dir, page_file)
    print(f"Looking for {page_file} at {page_path}")  # Debugging
    
    if not os.path.exists(page_path):
        print(f"Page file {page_file} not found, skipping.")
        return

    # Read index.html
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

    # If markers exist, replace everything between them
    if "<!-- NAV_START -->" in page_content and "<!-- NAV_END -->" in page_content:
        updated_page_content = re.sub(
            r'<!-- NAV_START -->.*<!-- NAV_END -->',
            nav_html_wrapped,
            page_content,
            flags=re.DOTALL
        )
    else:
        # Insert nav at placeholder or at top of body if no markers found
        if "<!-- NAV -->" in page_content:
            updated_page_content = page_content.replace("<!-- NAV -->", nav_html_wrapped)
        else:
            # Fallback: insert after opening <body>
            updated_page_content = page_content.replace(
                "<body>",
                f"<body>\n{nav_html_wrapped}"
            )

    # Write back only if changes were made
    if updated_page_content != page_content:
        with open(page_path, "w", encoding="utf-8") as f:
            f.write(updated_page_content)
        print(f"Injected/updated nav into {page_file}")
    else:
        print("No changes made. Nav already up to date.")

# =========================
# Run injection
# =========================
inject_nav_into_index()
print("Nav injection complete for index.html.")