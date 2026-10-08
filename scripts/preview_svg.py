"""Validación local: inlinea un SVG en HTML, salta el reloj SMIL al final
y captura PNG con Chrome headless (solo para previsualizar; no va al repo).

Uso: python scripts/preview_svg.py <archivo.svg> <salida.png>
"""
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("Uso: python scripts/preview_svg.py <svg> <png>")
    svg_path = Path(sys.argv[1]).resolve()
    png_path = Path(sys.argv[2]).resolve()
    svg = svg_path.read_text(encoding="utf-8")

    # tamaño del viewBox
    import re
    m = re.search(r'width="(\d+)" height="(\d+)"', svg)
    w, h = (int(m.group(1)), int(m.group(2))) if m else (800, 600)

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>body{{margin:0;background:#0d1117}}</style></head><body>{svg}
<script>document.querySelectorAll('svg').forEach(s=>{{try{{s.setCurrentTime(99)}}catch(e){{}}}});</script>
</body></html>"""

    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
        html_path = f.name

    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", f"--screenshot={png_path}",
         f"--window-size={w},{h}", "--virtual-time-budget=10000",
         f"file:///{html_path.replace(chr(92), '/')}"],
        check=True, capture_output=True,
    )
    print(f"OK {png_path} ({w}x{h})")


if __name__ == "__main__":
    main()
