"""Собирает весь сайт в один самодостаточный HTML-файл (dist/index.html).

CSS и JS встраиваются внутрь, картинки превращаются в data:URI.
Такой файл можно залить на GitHub одним перетаскиванием — без папок.

    python tools/build_single.py
"""

from __future__ import annotations

import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dist"

MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
}


def data_uri(path: Path) -> str:
    mime = MIME.get(path.suffix.lower(), "application/octet-stream")
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{payload}"


def build() -> Path:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "css" / "style.css").read_text(encoding="utf-8")
    js = (ROOT / "js" / "app.js").read_text(encoding="utf-8")

    html = html.replace(
        '<link rel="stylesheet" href="css/style.css">',
        f"<style>\n{css}\n</style>",
    )
    html = html.replace(
        '<script src="js/app.js" defer></script>',
        f"<script>\n{js}\n</script>",
    )

    def swap(match: re.Match[str]) -> str:
        rel = match.group(1)
        target = ROOT / rel.replace("/", "\\")
        if not target.exists():
            return match.group(0)
        return f'src="{data_uri(target)}"'

    html = re.sub(r'src="(assets/[^"]+)"', swap, html)

    # превью для соцсетей в data:URI бессмысленно — оставляем как есть
    OUT.mkdir(parents=True, exist_ok=True)
    out_file = OUT / "index.html"
    out_file.write_text(html, encoding="utf-8")
    return out_file


if __name__ == "__main__":
    f = build()
    size = f.stat().st_size / 1024
    print(f"ok {f} ({size:.0f} КБ)")
