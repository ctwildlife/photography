import os
from bs4 import BeautifulSoup

# Define the path where your HTML files are stored
html_dir = "pages"
nav_file_path = "Includes/nav.html"  # Path to the navigation file

# Define the static pages you want to add to the nav
static_pages = [
    {"name": "Flickr", "url": "/photography/pages/more-flickr.html"},
    {"name": "Contact", "url": "/photography/pages/more-contact.html"}
]

# Function to create the static pages HTML content
def generate_static_page_links(pages):
    links = ""
    for page in pages:
        links += f'<li><a href="{page["url"]}">{page["name"]}</a></li>\n'
    return links

# Function to check if static pages are already present in the HTML
def are_static_pages_already_added(soup, static_links):
    # Parse the static_links string into individual URLs
    urls_in_links = [link['href'] for link in soup.find_all('a', href=True)]
    
    # Check if any of the static pages' URLs are already in the nav
    for page in static_pages:
        if page['url'] in urls_in_links:
            return True  # Already added
    return False  # Not added yet

# Function to inject static pages into the HTML after the "Wildflowers" link
def inject_static_pages(file_path, static_links):
    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Check if static pages are already injected
    if are_static_pages_already_added(soup, static_links):
        print(f"Static pages already added to {file_path}, skipping.")
        return

    # Find the <a> tag for the "Wildflowers" page
    wildflowers_link = soup.find('a', string='Wildflowers')

    if wildflowers_link:
        # Find the <li> that contains the "Wildflowers" link
        wildflowers_li = wildflowers_link.find_parent('li')

        # If we found the <li> tag, insert the new static pages after it
        if wildflowers_li:
            # Generate new <li> elements for each static page
            for page in static_pages:
                new_item = soup.new_tag('li')
                new_link = soup.new_tag('a', href=page['url'])  # Use URL directly
                new_link.string = page['name']
                new_item.append(new_link)

                # Insert the new item after the "Wildflowers" list item
                wildflowers_li.insert_after(new_item)

                # Manually add a newline after each static page insertion for better formatting
                wildflowers_li.insert_after("\n")  # Adds a newline after the new item

            print(f"Injected static pages after 'Wildflowers' in {file_path}")
        else:
            print(f"Could not find the <li> containing the 'Wildflowers' link in {file_path}")
    else:
        print(f"No link found for 'Wildflowers' in {file_path}")

    # Write the updated HTML content back to the file
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(str(soup))
    print(f"Saved updated HTML file: {file_path}")

# Function to inject static pages into the nav.html file
def inject_static_pages_into_nav(static_links):
    # Read the nav.html file from the Includes folder
    with open(nav_file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Check if static pages are already injected
    if are_static_pages_already_added(soup, static_links):
        print(f"Static pages already added to {nav_file_path}, skipping.")
        return

    # Find the <a> tag for the "Wildflowers" page
    wildflowers_link = soup.find('a', string='Wildflowers')

    if wildflowers_link:
        # Find the <li> that contains the "Wildflowers" link
        wildflowers_li = wildflowers_link.find_parent('li')

        # If we found the <li> tag, insert the new static pages after it
        if wildflowers_li:
            # Generate new <li> elements for each static page
            for page in static_pages:
                new_item = soup.new_tag('li')
                new_link = soup.new_tag('a', href=page['url'])  # Use URL directly
                new_link.string = page['name']
                new_item.append(new_link)

                # Insert the new item after the "Wildflowers" list item
                wildflowers_li.insert_after(new_item)

                # Manually add a newline after each static page insertion for better formatting
                wildflowers_li.insert_after("\n")  # Adds a newline after the new item

            print(f"Injected static pages into nav.html")
        else:
            print(f"Could not find the <li> containing the 'Wildflowers' link in nav.html")
    else:
        print(f"No link found for 'Wildflowers' in nav.html")

    # Write the updated HTML content back to the nav.html file
    with open(nav_file_path, "w", encoding="utf-8") as file:
        file.write(str(soup))
    print(f"Saved updated nav.html file in {nav_file_path}")

# Generate the static links from the list of static pages
static_links = generate_static_page_links(static_pages)

# Iterate through each HTML file in the "pages" directory and inject the static pages
for filename in os.listdir(html_dir):
    if filename.endswith(".html"):
        file_path = os.path.join(html_dir, filename)
        inject_static_pages(file_path, static_links)

# Also inject static pages into the "Includes/nav.html" file
inject_static_pages_into_nav(static_links)
