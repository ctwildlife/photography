# nav.py

# =========================
# Manual nav entries
# =========================

manual_nav = [
    {"title": "Home", "url": "/photography/index.html"},
    {"title": "New", "url": "/photography/pages/new.html"},
    {"title": "Search", "url": "/photography/pages/search.html"}
]

# Desired top-level order
top_level_order = ["Home", "New", "Birds", "Mammals", "Landscapes", "More", "Search"]

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
    top_level_order = ["Home", "New", "Birds", "Mammals", "Landscapes", "More", "Search"]

    def recurse(tree, level=0):
        html = "<ul class='dropdown-menu'>\n" if level > 0 else ""
        for key, value in tree.items():
            if key == "_slug":
                continue
            if not isinstance(value, dict):
                value = {"_slug": value}  # wrap leaf string as dict

            children = {k: v for k, v in value.items() if k != "_slug"}
            slug = value.get("_slug")

            if children:
                html += f"<li class='dropdown'><a href='#'>{nav_label_from_key(key)}</a>\n"
                html += recurse(children, level + 1)
                html += "</li>\n"
            elif slug:
                html += f"<li><a href='{slug}'>{nav_label_from_key(key)}</a></li>\n"
        html += "</ul>\n" if level > 0 else ""
        return html


    # Merge manual entries and auto galleries for easy lookup
# Merge manual entries and auto galleries for easy lookup
    top_level_items = {}
    for item in manual_nav:
        top_level_items[item["title"]] = {"_slug": item["url"]}  # wrap URL in dict for consistency
    for key, value in gallery_tree.items():
        # ensure leaves are dicts
        if isinstance(value, str):
            top_level_items[key] = {"_slug": value}
        else:
            top_level_items[key] = value


    html = "<div class='navbar'>\n"
    html += "  <ul class='menu'>\n"

    # Render items in the order specified in top_level_order
    for label in top_level_order:
        item = top_level_items.get(label)
        if not item:
            continue  # skip if this label doesn't exist

        if isinstance(item, dict) and "_slug" in item:  # auto gallery page
            html += f"    <li><a href='/photography/pages/{item['_slug']}.html'>{label}</a></li>\n"
        elif isinstance(item, dict):  # has children folders
            children = {k: v for k, v in item.items() if k != "_slug"}
            html += f"    <li class='dropdown'><a href='#'>{label}</a>\n"
            html += recurse(children, level=1)
            html += "    </li>\n"
        elif "url" in item:  # manual nav
            html += f"    <li><a href='{item['url']}'>{item['title']}</a></li>\n"

    html += "  </ul>\n"
    html += "</div>\n"
    return html
