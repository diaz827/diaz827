"""Renderiza data/contributions.json como contrib-heatmap.svg animado.

- Calendario clásico 53 semanas x 7 dias, cajas redondeadas.
- Paleta azul/cyan (nivel 5 = neon).
- Revelado unico en diagonal con CSS keyframes (fill-mode forwards, sin bucle).
- Leyenda Menos -> Mas y pie con estadisticas.

Uso:
    python scripts/render_heatmap_svg.py
Salida:
    contrib-heatmap.svg
"""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0d3b66", "#1565c0", "#1e88e5", "#4fc3f7", "#67f4ff"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

CELL = 12
GAP = 3
STEP = CELL + GAP
LEFT = 34          # margen para etiquetas de día
TOP = 28           # margen para etiquetas de mes
PAD_R = 31         # W total = 860 (igual que 370 + 490 del README)
W = LEFT + 53 * STEP + PAD_R
FOOT_Y_TOP = TOP + 7 * STEP + 14   # leyenda
FOOT_Y = FOOT_Y_TOP + 30           # stats
H = FOOT_Y + 16

CELL_DELAY = 0.012   # s por columna (diagonal)
ROW_DELAY = 0.02     # s extra por fila
DUR = 0.3


def level_from_count(count: int) -> int:
    if count <= 0:
        return 0
    if count <= 1:
        return 1
    if count <= 3:
        return 2
    if count <= 6:
        return 3
    if count <= 9:
        return 4
    return 5


def main() -> None:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    days = {d["date"]: d for d in data["days"]}

    first = date.fromisoformat(data["days"][0]["date"])
    # alinea la primera columna al domingo de la semana del primer dia
    start = first.fromordinal(first.toordinal() - first.weekday() - 1)

    total = data["year_total"]
    n_total = f"{total:,}".replace(",", ",")

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="Consolas, Menlo, monospace" font-size="11">',
        "<style>",
        f"rect.c{{opacity:0;animation:pop {DUR}s ease-out forwards;}}",
        "@keyframes pop{to{opacity:1}}",
        "text{fill:#8b949e;}",
        "</style>",
        f'<rect width="{W}" height="{H}" rx="8" fill="#0d1117"/>',
    ]

    # etiquetas de mes (sobre la primera semana de cada mes visible; sin solapes)
    prev_month = None
    last_label_week = -99
    cells = []
    for week in range(53):
        col_date = start.fromordinal(start.toordinal() + week * 7)
        if col_date.month != prev_month and week - last_label_week >= 2:
            x = LEFT + week * STEP
            parts.append(f'<text x="{x}" y="14">{MONTHS[col_date.month - 1]}</text>')
            last_label_week = week
            prev_month = col_date.month
        elif col_date.month != prev_month:
            prev_month = col_date.month  # etiqueta omitida por falta de espacio
        for row in range(7):
            d = col_date.fromordinal(col_date.toordinal() + row)
            iso = d.isoformat()
            info = days.get(iso)
            if info is None and d > date.fromisoformat(data["days"][-1]["date"]):
                continue  # dias futuros de la ultima columna
            count = info["count"] if info else 0
            lv = level_from_count(count)
            x = LEFT + week * STEP
            y = TOP + row * STEP
            delay = week * CELL_DELAY + row * ROW_DELAY
            cells.append(
                f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{PALETTE[lv]}" style="animation-delay:{delay:.3f}s">'
                f"<title>{d.isoformat()}: {count} contribution{'s' if count != 1 else ''}</title>"
                "</rect>"
            )

    parts.extend(cells)

    # etiquetas de día
    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(f'<text x="4" y="{TOP + row * STEP + 10}">{label}</text>')

    # leyenda
    lx = W - 5 * STEP - 60
    parts.append(f'<text x="{lx - 34}" y="{FOOT_Y_TOP + 10}">Menos</text>')
    for i, c in enumerate(PALETTE):
        parts.append(
            f'<rect x="{lx + i * STEP}" y="{FOOT_Y_TOP}" width="{CELL}" height="{CELL}" '
            f'rx="2.5" fill="{c}"/>'
        )
    parts.append(f'<text x="{lx + 6 * STEP + 6}" y="{FOOT_Y_TOP + 10}">Mas</text>')

    # pie con estadisticas
    streak = data["current_streak"]
    parts.append(
        f'<text x="{LEFT}" y="{FOOT_Y}">{n_total} contributions in the last year'
        f"  ·  current streak: {streak}d  ·  longest: {data['longest_streak']}d</text>"
    )

    parts.append("</svg>")
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"Escrito {OUT.name} ({W}x{H}, {len(cells)} celdas, {n_total} contribuciones)")


if __name__ == "__main__":
    main()
