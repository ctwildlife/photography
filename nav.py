# nav.py

# =========================
# Manual nav entries
# =========================

manual_nav = [
    {"title": "Home", "url": "/photography/index.html"},
    {"title": "New", "url": "/photography/pages/new.html"},
    {"title": "Birds", "slug": "birds"},
    {"title": "Mammals", "slug": "mammals"},
    {"title": "Landscapes", "slug": "landscapes"},
    {"title": "More", "slug": "more"},
    {"title": "Search", "url": "/photography/pages/search.html"},
]

def build_nav_tree(galleries):
    tree = {}
    for g in galleries:
        node = tree
        for part in g["path_parts"]:
            if part not in node:
                node[part] = {}
            node = node[part]

        # Check if the gallery has any photos
        if g["image_count"] > 0:
            node["_slug"] = g["slug"]
            node["_image_count"] = g["image_count"]

    return tree

def nav_label_from_key(key):
    label = key.replace("-", " ")
    return label[:1].upper() + label[1:]

def generate_nav_html(manual_nav, gallery_tree):
    def recurse(tree):
        html = "<ul class='dropdown-menu'>\n"

        # Only sort items where value is a dict
        items_to_sort = [(k, v) for k, v in tree.items() if isinstance(v, dict) and not k.startswith("_")]

        for key, value in sorted(
            items_to_sort,
            key=lambda item: item[1].get("_image_count", 0),
            reverse=True,
        ):
            children = {k: v for k, v in value.items() if k != "_slug"}

            slug = value.get("_slug")

            if children:
                html += (
                    f"<li class='dropdown'>"
                    f"<a href='#'>{nav_label_from_key(key)}</a>\n"
                )
                html += recurse(children)
                html += "</li>\n"
            elif slug:
                html += (
                    f"<li><a href='/photography/pages/{slug}.html'>"
                    f"{nav_label_from_key(key)}</a></li>\n"
                )

        html += "</ul>\n"
        return html

    html = "<div class='navbar'>\n"
    html += "  <ul class='menu'>\n"

    for item in manual_nav:
        title = item["title"]

        # Simple link (Home, New, Search)
        if "url" in item:
            html += f"    <li><a href='{item['url']}'>{title}</a></li>\n"
            continue

        # Gallery-backed item
        slug = item["slug"]
        if slug not in gallery_tree:
            continue

        node = gallery_tree[slug]
        children = {k: v for k, v in node.items() if k != "_slug"}

        if children:
            html += (
                f"    <li class='dropdown'>"
                f"<a href='#'>{title}</a>\n"
            )
            html += recurse(children)
            html += "    </li>\n"
        else:
            html += (
                f"    <li><a href='/photography/pages/{slug}.html'>"
                f"{title}</a></li>\n"
            )

    html += "  </ul>\n"
    html += "</div>\n"
    return html
