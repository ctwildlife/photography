# nav.py

# =========================
# Manual nav entries
# =========================

manual_nav = [
    {"title": "Home", "url": "/photography/index.html"},
    {"title": "New", "url": "/photography/pages/new.html"},
    {"title": "Search", "url": "/photography/pages/search.html"}
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


def generate_nav_html(manual_nav, gallery_tree):
    def recurse(tree, level=0):
        html = "<ul class='dropdown-menu'>\n" if level > 0 else ""
        for key, value in tree.items():
            if key == "_slug":
                continue

            children = {k: v for k, v in value.items() if k != "_slug"}
            slug = value.get("_slug")

            if children:
                html += (
                    f"<li class='dropdown'>"
                    f"<a href='#'>{nav_label_from_key(key)}</a>\n"
                )
                html += recurse(children, level + 1)
                html += "</li>\n"
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

    for key, value in gallery_tree.items():
        children = {k: v for k, v in value.items() if k != "_slug"}
        slug = value.get("_slug")

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

    html += f"    <li class='nav-right'><a href='{manual_nav[2]['url']}'>{manual_nav[2]['title']}</a></li>\n"

    html += "  </ul>\n"
    html += "</div>\n"
    return html
