"""Crea info-card.svg: tarjeta estilo neofetch con animación línea a línea.

Contenido de ejemplo (cámbialo aquí cuando quieras):
    Now / Prev / Stack / Highlights

Cada línea aparece con fundido + desplazamiento, retraso escalonado,
una sola vez (fill="freeze", sin bucle).

Uso:
    python scripts/make_info_card.py            # con animación
    STATIC=1 python scripts/make_info_card.py   # fotograma congelado
Salida:
    info-card.svg
"""
import os
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "info-card.svg"

STATIC = os.environ.get("STATIC") == "1"
USER = "diaz827"
BG = "#0d1117"
FG = "#c9d1d9"
CYAN = "#39b9cf"
BLUE = "#58a6ff"
GREEN = "#39d353"
GRAY = "#8b949e"
FONT_SIZE = 14
CHAR_W = 8.4  # ancho aproximado por glifo monoespaciado a 14px
LINE_H = 26
PAD = 18

# (clave, valor, color del valor)
ROWS = [
    ("Name", "Daniel Díaz Canosa", FG),
    ("Now", "Estudiante de DAW en A Coruña \U0001f1ea\U0001f1f8", GREEN),
    ("Email", "canosadiaz6@gmail.com", BLUE),
    ("LinkedIn", "linkedin.com/in/dani-díaz-canosa-4465793b2", BLUE),
    ("Web", "soydiaz.pages.dev", CYAN),
    ("Blog", "midiazrio.blog", CYAN),
]


def calc_width() -> int:
    """Ancho mínimo para que quepa la fila más larga (clave + ' : ' + valor)."""
    longest = max(len(k) + 3 + len(v) for k, v, _ in ROWS)
    return max(480, int(PAD * 2 + 28 + longest * CHAR_W) + 12)


W = calc_width()

LINE_DELAY = 0.18
FADE = 0.45


def open_g(idx: int) -> str:
    """<g> de una línea: animada (opacity 0 + translate) o estático."""
    if STATIC:
        return "<g>"
    begin = 0.25 + idx * LINE_DELAY
    return (
        '<g opacity="0">'
        f'<animate attributeName="opacity" from="0" to="1" dur="{FADE}s" '
        f'begin="{begin:.2f}s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" '
        f'from="10 0" to="0 0" dur="{FADE}s" begin="{begin:.2f}s" '
        f'fill="freeze" calcMode="spline" keySplines="0.25 0.1 0.25 1" keyTimes="0;1"/>'
    )


def main() -> None:
    n_lines = 1 + len(ROWS)
    h = PAD * 2 + 30 + n_lines * LINE_H + 10

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" '
        f'viewBox="0 0 {W} {h}" font-family="Consolas, Menlo, monospace" '
        f'font-size="{FONT_SIZE}">',
        f'<rect width="{W}" height="{h}" rx="8" fill="{BG}"/>',
        # barra de título
        '<g>',
        f'<rect width="{W}" height="30" rx="8" fill="#161b22"/>',
        f'<rect y="14" width="{W}" height="16" fill="#161b22"/>',
        '<circle cx="18" cy="15" r="5" fill="#ff5f57"/>',
        '<circle cx="36" cy="15" r="5" fill="#febc2e"/>',
        '<circle cx="54" cy="15" r="5" fill="#28c840"/>',
        f'<text x="{W // 2}" y="20" text-anchor="middle" fill="{GRAY}" font-size="12">'
        f"{USER}@github:~</text>",
        "</g>",
    ]

    # prompt + neofetch (un solo <text> con tspans: sin solapes)
    y0 = 30 + PAD + FONT_SIZE
    parts.append(
        f"{open_g(0)}"
        f'<text x="{PAD}" y="{y0}">'
        f'<tspan fill="{GREEN}">{USER}@github</tspan>'
        f'<tspan fill="{FG}">:</tspan>'
        f'<tspan fill="{BLUE}">~</tspan>'
        f'<tspan fill="{FG}">$ neofetch</tspan>'
        "</text></g>"
    )
    # separador
    sep_y = y0 + 8
    parts.append(f'<line x1="{PAD}" y1="{sep_y}" x2="{W - PAD}" y2="{sep_y}" stroke="#21262d"/>')

    # bloque de "logo" simple (un cuadrillo por fila, alineado con el texto)
    logo_x = PAD
    logo_y = sep_y + 24
    logo_colors = [BLUE, GREEN, CYAN, "#d2a8ff", "#f778ba", "#ffa657", "#8b949e", GRAY]
    for i in range(len(ROWS)):
        parts.append(
            f'<rect x="{logo_x}" y="{logo_y + i * LINE_H + 1}" width="12" height="12" '
            f'rx="3" fill="{logo_colors[i % len(logo_colors)]}"/>'
        )

    # filas clave/valor
    text_x = logo_x + 28
    for i, (key, val, color) in enumerate(ROWS):
        y = logo_y + i * LINE_H + 11
        parts.append(
            f"{open_g(i + 1)}"
            f'<text x="{text_x}" y="{y}">'
            f'<tspan fill="{CYAN}" font-weight="bold">{escape(key)}</tspan>'
            f'<tspan fill="{FG}"> : </tspan>'
            f'<tspan fill="{color}">{escape(val)}</tspan>'
            "</text></g>"
        )

    parts.append("</svg>")
    OUT.write_text("\n".join(parts), encoding="utf-8")
    mode = "STATIC" if STATIC else "animado"
    print(f"Escrito {OUT.name} ({W}x{h}, {mode})")


if __name__ == "__main__":
    main()
