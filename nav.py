# nav.py

manual_nav = [
    {"title": "Home", "url": "/photography/index.html"},
    {"title": "New", "url": "/photography/pages/new.html"},
    {"title": "Search", "url": "/photography/pages/search.html"}
]

manual_more_links = [
    {"title": "Flickr", "url": "/photography/pages/more-flickr.html"},
    {"title": "Contact", "url": "/photography/pages/more-contact.html"},
]


def build_nav_tree(galleries):
    tree = {}
    for g in galleries:
        node = tree
        for part in g["path_parts"]:
            if part not in node:
                node[part] = {}
            node = node[part]
        node["_slug"] = g["slug"]
    return tree


def nav_label_from_key(key):
    label = key.replace("-", " ")
    return label[:1].upper() + label[1:]


def generate_nav_html(manual_nav, gallery_tree, gallery_order, keyword_galleries=None):
    def recurse(tree, level=0):
        html = "<ul class='dropdown-menu'>\n" if level > 0 else ""
        for key, value in tree.items():
            if key in ("_slug", "_url"):
                continue

            children = {k: v for k, v in value.items() if k not in ("_slug", "_url")}
            slug = value.get("_slug")
            url = value.get("_url")

            if children:
                html += (
                    f"<li class='dropdown'>"
                    f"<a href='#'>{nav_label_from_key(key)}</a>\n"
                )
                html += recurse(children, level + 1)
                html += "</li>\n"
            elif url:
                html += f"<li><a href='{url}'>{key}</a></li>\n"
            elif slug:
                html += (
                    f"<li><a href='/photography/pages/{slug}.html'>"
                    f"{nav_label_from_key(key)}</a></li>\n"
                )

        html += "</ul>\n" if level > 0 else ""
        return html

    html = "<div class='navbar'>\n"
    html += "  <ul class='menu'>\n"

    html += f"    <li><a href='{manual_nav[0]['url']}'>{manual_nav[0]['title']}</a></li>\n"
    html += f"    <li><a href='{manual_nav[1]['url']}'>{manual_nav[1]['title']}</a></li>\n"

    ordered_keys = sorted(
        gallery_tree.keys(),
        key=lambda k: gallery_order.get(nav_label_from_key(k), 999)
    )

    # Build the extra entries (manual links + keyword galleries) that belong
    # under "More", keyed by title so they can merge into a real "More"
    # folder's children if one exists.
    extra_more_children = {}
    if keyword_galleries:
        for kg in keyword_galleries:
            label = kg.get("nav_title", kg["title"])
            extra_more_children[label] = {"_url": f"/photography/pages/{kg['filename']}"}
    for link in manual_more_links:
        extra_more_children[link["title"]] = {"_url": link["url"]}

    more_folder_rendered = False

    for key in ordered_keys:
        if key in ['Songbirds', 'Flora']:
            continue

        value = gallery_tree[key]
        children = {k: v for k, v in value.items() if k != "_slug"}
        slug = value.get("_slug")

        if nav_label_from_key(key) == "More":
            # Merge manual/keyword links into the real "More" folder instead
            # of creating a second dropdown.
            children = {**children, **extra_more_children}
            more_folder_rendered = True

        if children:
            html += (
                f"    <li class='dropdown'>"
                f"<a href='#'>{nav_label_from_key(key)}</a>\n"
            )
            html += recurse(children, level=1)
            html += "    </li>\n"
        elif slug:
            html += (
                f"    <li><a href='/photography/pages/{slug}.html'>"
                f"{nav_label_from_key(key)}</a></li>\n"
            )

    # Fallback: no real "More" folder exists, so create one from scratch.
    if not more_folder_rendered and extra_more_children:
        html += "    <li class='dropdown'><a href='#'>More</a>\n"
        html += recurse(extra_more_children, level=1)
        html += "    </li>\n"

    html += f"    <li class='nav-right'><a href='{manual_nav[2]['url']}'>{manual_nav[2]['title']}</a></li>\n"
    html += "  </ul>\n"
    html += "</div>\n"
    return html