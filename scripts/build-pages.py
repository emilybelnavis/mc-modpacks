"""Build the static Packwiz site for Cloudflare Pages (Python 3.11+)."""
import os
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
manifests = sorted(ROOT.glob("*/pack.toml"))
manifests = [p for p in manifests if p.parent.name != "_site"]
if not manifests:
    raise SystemExit("No Packwiz manifests found in top-level pack directories.")
output = ROOT / "_site"
if output.exists():
    shutil.rmtree(output)
output.mkdir()
for manifest in manifests:
    # Preserve file bytes, relative paths, and indexed hidden files.
    shutil.copytree(manifest.parent, output / manifest.parent.name)

import html
from pathlib import Path
import tomllib
from urllib.parse import quote

links = []
for manifest in sorted(Path("_site").glob("*/pack.toml")):
    pack = tomllib.loads(manifest.read_text())
    href = quote(manifest.relative_to("_site").as_posix())
    name = html.escape(pack.get("name", manifest.parent.name))
    folder = html.escape(manifest.parent.name)
    links.append(f'<li><a href="{href}">{name}</a><br><small>{folder}/pack.toml</small></li>')
page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Emily's Minecraft Modpacks</title>
<style>
body { font: 18px/1.6 system-ui,sans-serif; max-width: 700px; margin: 64px auto; padding: 0 24px; color: #203329; background: #f5f7f2; }
h1 { line-height: 1.2; } a { color: #24613c; } li { margin: 24px 0; } small { color: #54635a; }
</style></head><body>
<h1>Emily's Minecraft Modpacks</h1>
<p>Use a pack's manifest link with the Packwiz installer in Prism Launcher.</p>
<ul>""" + "".join(links) + """</ul>
<p><a href="https://github.com/emilybelnavis/mc-modpacks">View the repository</a></p>
</body></html>
"""
Path("_site/index.html").write_text(page)
# Prevent Cloudflare's SPA fallback from returning HTML for missing pack files.
Path("_site/404.html").write_text(
    '<!doctype html><html lang="en"><meta charset="utf-8">'
    '<title>Not found</title><h1>File not found</h1></html>'
)

files = [path for path in output.rglob("*") if path.is_file()]
oversized = [path for path in files if path.stat().st_size > 25 * 1024 * 1024]
if oversized:
    for path in oversized:
        print(f"Asset exceeds Cloudflare Pages' 25 MiB limit: {path.relative_to(output)}")
    raise SystemExit(1)
if len(files) > 20000:
    raise SystemExit("Site exceeds Cloudflare Pages' Free plan limit of 20,000 files.")
print(f"Built {len(manifests)} packs and {len(files)} files in _site.")
