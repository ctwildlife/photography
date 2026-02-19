import os

# Define the path where your HTML files are stored
html_dir = "pages"  # Change this to the directory where your HTML files are located
nav_file_path = "Includes/nav.html"  # Path to the navigation file

# Function to remove all occurrences of &amp; in HTML files
def remove_ampersands_from_html(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    # Replace all occurrences of &amp; with &
    html_content = html_content.replace('&amp;', '&')

    # Write the updated HTML content back to the file
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html_content)
    print(f"Removed &amp; from {file_path}")

# Iterate through each HTML file in the directory and remove &amp; occurrences
def remove_ampersands_from_all_files():
    # Process all HTML files in the "pages" directory
    for filename in os.listdir(html_dir):
        if filename.endswith(".html"):
            file_path = os.path.join(html_dir, filename)
            remove_ampersands_from_html(file_path)

    # Also remove &amp; from the "Includes/nav.html" file
    remove_ampersands_from_html(nav_file_path)

# Run the script to process all HTML files and nav.html
remove_ampersands_from_all_files()
