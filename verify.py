import re

index_content = open(r'C:\Users\Chanuka\.gemini\antigravity\scratch\wayatronic\index.html', encoding='utf-8').read()
admin_content = open(r'C:\Users\Chanuka\.gemini\antigravity\scratch\wayatronic\admin.html', encoding='utf-8').read()

def verify(name, html):
    css_links = re.findall(r'<link[^>]*rel=["\']stylesheet["\'][^>]*>', html)
    script_srcs = re.findall(r'<script[^>]*src=["\'][^>]*>', html)
    style_count = len(re.findall(r'<style>', html))
    script_count = len(re.findall(r'<script', html))
    print(f"[{name}]")
    print(f"  Total size: {len(html)} bytes")
    print(f"  External CSS links: {len(css_links)} -> {css_links}")
    print(f"  External Script tags: {len(script_srcs)} -> {script_srcs}")
    print(f"  Inline <style> tags: {style_count}")
    print(f"  Inline <script> tags: {script_count}")
    assert len(css_links) == 0, f"Found external CSS links in {name}!"
    assert len(script_srcs) == 0, f"Found external scripts in {name}!"

verify("index.html", index_content)
verify("admin.html", admin_content)

print("\nALL VERIFICATIONS PASSED SUCCESSFULLY! Both files are 100% self-contained.")
