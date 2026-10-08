"""Convierte source-prepped.png en ascii.svg animado (SMIL, se imprime una vez).

Cada fila va en un clip horizontal que se revela de izquierda a derecha,
con retraso escalonado de arriba abajo y un pequeño cursor en el borde.

Uso:
    python scripts/make_ascii_svg.py
Salida:
    ascii.svg
"""
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source-prepped.png"
OUT = ROOT / "ascii.svg"

RAMP = " .`:-=+*cs#%@"  # claro (poco denso) -> oscuro (denso)
COLS = 100
ROWS = 53
FONT_SIZE = 9.6
CHAR_W = 6.0
LINE_H = 10.0
FG = "#c9d1d9"  # monocromo gris claro (GitHub light-on-dark text)
BG = "#0d1117"
ROW_DELAY = 0.055  # s entre filas
TYPE_DURATION = 0.35  # s de revelado por fila
CURSOR_DUR = 0.28


def to_ascii(img: Image.Image) -> list[str]:
    gray = img.convert("L").resize((COLS, ROWS), Image.LANCZOS)
    px = list(gray.get_flattened_data()) if hasattr(gray, "get_flattened_data") else list(gray.getdata())
    lines = []
    for r in range(ROWS):
        row = px[r * COLS : (r + 1) * COLS]
        lines.append("".join(RAMP[min(len(RAMP) - 1, (255 - v) * len(RAMP) // 256)] for v in row))
    return lines


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"No existe {SRC}. Ejecuta antes scripts/prep_photo.py")

    img = Image.open(SRC)
    if img.height / img.width > 1.4:
        w, h = img.size
        img = img.crop((0, 0, w, int(w * 1.35)))  # recorta el torso largo

    lines = to_ascii(img)
    width = int(COLS * CHAR_W) + 4
    height = int(ROWS * LINE_H) + 4

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="Consolas, Menlo, monospace" '
        f'font-size="{FONT_SIZE}" fill="{FG}">',
        f'<rect width="{width}" height="{height}" fill="{BG}" rx="8"/>',
    ]

    total = ROW_DELAY * ROWS + TYPE_DURATION + 0.3

    for i, line in enumerate(lines):
        y = 4 + i * LINE_H + FONT_SIZE * 0.85
        cid = f"r{i}"
        begin = i * ROW_DELAY
        # clip horizontal que crece de izquierda a derecha
        parts.append(
            f'<clipPath id="{cid}"><rect x="0" y="{i * LINE_H}" width="0" height="{LINE_H}">'
            f'<animate attributeName="width" from="0" to="{width}" dur="{TYPE_DURATION}s" '
            f'begin="{begin:.3f}s" fill="freeze" calcMode="spline" '
            f'keySplines="0.25 0.1 0.25 1" keyTimes="0;1" values="0;{width}"/></rect></clipPath>'
        )
        text = escape(line.rstrip())
        if text:
            parts.append(
                f'<text x="2" y="{y:.1f}" clip-path="url(#{cid})" '
                f'xml:space="preserve">{text}</text>'
            )
        # cursor que viaja por el borde derecho del clip
        parts.append(
            f'<rect x="0" y="{i * LINE_H}" width="2" height="{LINE_H}" fill="{FG}" opacity="0">'
            f'<animate attributeName="x" from="0" to="{width}" dur="{TYPE_DURATION}s" '
            f'begin="{begin:.3f}s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" dur="{TYPE_DURATION}s" '
            f'begin="{begin:.3f}s" fill="freeze"/>'
            f'<animate attributeName="opacity" from="1" to="0" dur="0.15s" '
            f'begin="{begin + TYPE_DURATION:.3f}s" fill="freeze"/>'
            f"</rect>"
        )

    parts.append("</svg>")

    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"Escrito {OUT.name} ({width}x{height}, {ROWS} filas, duración ~{total:.1f}s)")


if __name__ == "__main__":
    main()
