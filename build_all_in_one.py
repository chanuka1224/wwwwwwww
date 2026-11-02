import os
import base64
import re

base_dir = r"C:\Users\Chanuka\.gemini\antigravity\scratch\wayatronic"
assets_dir = os.path.join(base_dir, "assets")
images_dir = os.path.join(assets_dir, "images")
css_dir = os.path.join(base_dir, "css")
js_dir = os.path.join(base_dir, "js")

# 1. Base64 Encode all SVG Assets
assets = {}
for f in os.listdir(assets_dir):
    p = os.path.join(assets_dir, f)
    if os.path.isfile(p):
        content = open(p, "rb").read()
        assets[f] = "data:image/svg+xml;base64," + base64.b64encode(content).decode("ascii")

for f in os.listdir(images_dir):
    p = os.path.join(images_dir, f)
    if os.path.isfile(p):
        content = open(p, "rb").read()
        assets[f] = "data:image/svg+xml;base64," + base64.b64encode(content).decode("ascii")

print(f"Loaded {len(assets)} assets.")

# 2. Combine All CSS
css_content = ""
for f in ["styles.css", "components.css", "admin.css"]:
    p = os.path.join(css_dir, f)
    css_content += f"\n/* ===== {f} ===== */\n" + open(p, encoding="utf-8").read()

# Replace any asset paths in CSS if any
for asset_name, data_uri in assets.items():
    css_content = css_content.replace(f"assets/images/{asset_name}", data_uri)
    css_content = css_content.replace(f"assets/{asset_name}", data_uri)

# 3. Read JS files
db_js = open(os.path.join(js_dir, "db.js"), encoding="utf-8").read()
auth_js = open(os.path.join(js_dir, "auth.js"), encoding="utf-8").read()
cart_js = open(os.path.join(js_dir, "cart.js"), encoding="utf-8").read()
products_js = open(os.path.join(js_dir, "products.js"), encoding="utf-8").read()
checkout_js = open(os.path.join(js_dir, "checkout.js"), encoding="utf-8").read()
admin_js = open(os.path.join(js_dir, "admin.js"), encoding="utf-8").read()
app_js = open(os.path.join(js_dir, "app.js"), encoding="utf-8").read()

# Replace asset URLs in db.js with data URIs
for asset_name, data_uri in assets.items():
    db_js = db_js.replace(f"'assets/images/{asset_name}'", f"'{data_uri}'")
    db_js = db_js.replace(f'"assets/images/{asset_name}"', f"'{data_uri}'")
    db_js = db_js.replace(f"'assets/{asset_name}'", f"'{data_uri}'")
    db_js = db_js.replace(f'"assets/{asset_name}"', f"'{data_uri}'")

# Replace in products_js, cart_js, app_js, admin_js
for js in [products_js, cart_js, app_js, admin_js, checkout_js]:
    for asset_name, data_uri in assets.items():
        js = js.replace(f"'assets/images/{asset_name}'", f"'{data_uri}'")
        js = js.replace(f"'assets/{asset_name}'", f"'{data_uri}'")

# In app.js, support 'admin' route
admin_route_hook = """
      case 'admin':
        const siteHeader = document.querySelector('.site-header');
        const siteFooter = document.querySelector('.site-footer');
        const announcementBar = document.querySelector('.top-announcement-bar');
        if (siteHeader) siteHeader.style.display = 'none';
        if (siteFooter) siteFooter.style.display = 'none';
        if (announcementBar) announcementBar.style.display = 'none';
        if (window.WayaAdmin) window.WayaAdmin.checkAdminSession();
        return;
"""
app_js = app_js.replace("case 'track':", admin_route_hook + "      case 'track':")

# Restore header & footer when leaving admin
restore_hook = """
    // Show header & footer if returning from admin
    if (viewName !== 'admin') {
      const siteHeader = document.querySelector('.site-header');
      const siteFooter = document.querySelector('.site-footer');
      const announcementBar = document.querySelector('.top-announcement-bar');
      if (siteHeader) siteHeader.style.display = '';
      if (siteFooter) siteFooter.style.display = '';
      if (announcementBar) announcementBar.style.display = '';
    }
"""
app_js = app_js.replace("// Hide all view containers", restore_hook + "\n    // Hide all view containers")

# Make admin return to storefront work seamlessly in app.js
admin_js = admin_js.replace("location.reload();", "window.WayaApp.navigateTo('home');")

# Construct JS Bundle
js_bundle = f"""
// Embedded WayaTronic In-Memory Asset Dictionary
window.WAYA_ASSETS = {{
{', '.join([f'  "{k}": "{v}"' for k, v in assets.items()])}
}};

// 1. Database & Cryptographic Engine
{db_js}

// 2. Authentication & Session Manager
{auth_js}

// 3. Shopping Cart Engine
{cart_js}

// 4. Products Catalog & Filter Engine
{products_js}

// 5. Checkout & Order Processing Controller
{checkout_js}

// 6. Admin Management Suite Controller
{admin_js}

// 7. Main Application & UI Controller
{app_js}
"""

print("JS Bundle length:", len(js_bundle))

# 4. Extract Admin HTML Markup to embed inside index.html
admin_html_raw = open(os.path.join(base_dir, "admin.html"), encoding="utf-8").read()

# Extract sections and modals from admin.html
admin_sections_match = re.search(r'(<!-- ADMIN LOGIN SECTION.*?<!-- MODALS -->.*?)(?=<!-- Toast Container -->)', admin_html_raw, re.DOTALL)
admin_markup = admin_sections_match.group(1) if admin_sections_match else ""

# Replace asset references in admin_markup
for asset_name, data_uri in assets.items():
    admin_markup = admin_markup.replace(f'src="assets/{asset_name}"', f'src="{data_uri}"')
    admin_markup = admin_markup.replace(f'src="assets/images/{asset_name}"', f'src="{data_uri}"')

# Also replace links to index.html with javascript:window.WayaApp.navigateTo('home');
admin_markup = admin_markup.replace('href="index.html"', 'href="javascript:void(0)" onclick="window.WayaApp.navigateTo(\'home\');"')
admin_markup = admin_markup.replace('href="index.html" target="_blank"', 'href="javascript:void(0)" onclick="window.WayaApp.navigateTo(\'home\');"')

# Wrap admin markup inside a view_admin container
admin_view_container = f"""
    <!-- VIEW 10: INTEGRATED DEDICATED ADMIN PORTAL -->
    <div id="view_admin" class="view-section" style="display: none;">
      <div style="background: #060b18; padding: 0.5rem 1rem; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center;">
        <span style="font-size: 0.8rem; color: var(--brand-cyan); font-weight: 700;">🔒 WayaTronic Internal Operations Suite</span>
        <button class="btn btn-secondary btn-xs" onclick="window.WayaApp.navigateTo('home');">← Return to Customer Storefront</button>
      </div>
      {admin_markup}
    </div>
"""

# Read existing index.html
index_html_raw = open(os.path.join(base_dir, "index.html"), encoding="utf-8").read()

# Replace stylesheets in index.html with inline <style>
style_tag = f"<style>\n{css_content}\n</style>"
index_html_mod = re.sub(r'<link rel="stylesheet" href="css/styles\.css" />\s*<link rel="stylesheet" href="css/components\.css" />', style_tag, index_html_raw)

# Replace scripts in index.html with inline <script>
script_tag = f"<script>\n{js_bundle}\n</script>"
index_html_mod = re.sub(r'<!-- JavaScript Modules -->[\s\S]*?</body>', f"<!-- Single-File Self-Contained JavaScript Engine -->\n{script_tag}\n</body>", index_html_mod)

# Insert the admin view container inside <main class="main-content-flow">
index_html_mod = index_html_mod.replace("</main>", f"{admin_view_container}\n  </main>")

# Replace logo.svg and favicon.svg in HTML markup with data URIs
for asset_name, data_uri in assets.items():
    index_html_mod = index_html_mod.replace(f'src="assets/{asset_name}"', f'src="{data_uri}"')
    index_html_mod = index_html_mod.replace(f'href="assets/{asset_name}"', f'href="{data_uri}"')
    index_html_mod = index_html_mod.replace(f'content="assets/{asset_name}"', f'content="{data_uri}"')
    index_html_mod = index_html_mod.replace(f'src="assets/images/{asset_name}"', f'src="{data_uri}"')

# Update admin link in footer and mobile menu to navigate directly
index_html_mod = index_html_mod.replace('href="admin.html" target="_blank" class="admin-portal-link"', 'href="#admin" onclick="window.WayaApp.navigateTo(\'admin\');" class="admin-portal-link"')
index_html_mod = index_html_mod.replace('href="admin.html" target="_blank" class="mobile-admin-link"', 'href="#admin" onclick="window.WayaApp.navigateTo(\'admin\');" class="mobile-admin-link"')

# Write the new self-contained index.html
with open(os.path.join(base_dir, "index.html"), "w", encoding="utf-8") as out:
    out.write(index_html_mod)

print("Updated index.html written successfully. Size:", len(index_html_mod))

# Also write a self-contained admin.html
admin_standalone = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>WayaTronic Admin Suite | Operations &amp; Inventory Management</title>
  <link rel="icon" type="image/svg+xml" href="{assets.get('favicon.svg', '')}" />
  <style>
{css_content}
  </style>
</head>
<body>
{admin_markup}
<div id="toastContainer" class="toast-container"></div>
<script>
{js_bundle}
window.WayaApp = {{
  showToast(msg, type = 'info') {{
    const c = document.getElementById('toastContainer');
    if (!c) return;
    const t = document.createElement('div');
    t.className = `toast toast-${{type}}`;
    t.innerHTML = `<span class="toast-icon">${{type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}}</span><span class="toast-message">${{msg}}</span>`;
    c.appendChild(t);
    setTimeout(() => t.classList.add('show'), 10);
    setTimeout(() => {{ t.classList.remove('show'); setTimeout(() => t.remove(), 400); }}, 3500);
  }}
}};
document.addEventListener('DOMContentLoaded', () => {{
  window.WayaAdmin.init();
}});
</script>
</body>
</html>"""

with open(os.path.join(base_dir, "admin.html"), "w", encoding="utf-8") as out:
    out.write(admin_standalone)

print("Updated admin.html written successfully. Size:", len(admin_standalone))
