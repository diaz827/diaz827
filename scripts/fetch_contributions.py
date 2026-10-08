"""Descarga el calendario de contribuciones público de GitHub (sin token).

GitHub sirve el calendar como HTML en:
    https://github.com/users/<username>/contributions

Parsea las celdas de día con BeautifulSoup y escribe
data/contributions.json con los días en bruto + estadísticas derivadas
(racha actual, racha más larga, mejor día, totales por mes).

Uso:
    python scripts/fetch_contributions.py [username]
"""
import calendar
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "contributions.json"
DEFAULT_USER = "diaz827"

DAY_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
MONTHS_ES = {m: calendar.month_abbr[m] for m in range(1, 13)}


def fetch_days(username: str) -> list[dict]:
    url = f"https://github.com/users/{username}/contributions"
    resp = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 (profile-readme-contribution-fetcher)"},
        timeout=30,
    )
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    days = []
    for rect in soup.select("td[id]"):
        date_attr = rect.get("data-date") or ""
        level_attr = rect.get("data-level") or "0"
        if not DAY_RE.fullmatch(date_attr):
            continue
        tooltip = rect.get("tool-tip") or rect.get("data-tooltip") or ""
        count = 0
        m = re.search(r"(\d+)\s+contribution", tooltip)
        if m:
            count = int(m.group(1))
        elif level_attr == "0":
            count = 0
        else:
            count = int(level_attr)  # fallback aproximado
        days.append({"date": date_attr, "level": int(level_attr), "count": count})

    days.sort(key=lambda d: d["date"])
    return days


def stats(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)

    # rachas (días consecutivos con >=1 contribución)
    streak = best_streak = 0
    prev = None
    for d in days:
        day = date.fromisoformat(d["date"])
        if d["count"] > 0:
            streak = streak + 1 if prev == day - timedelta(days=1) else 1
            best_streak = max(best_streak, streak)
        else:
            streak = 0
        prev = day

    current_streak = streak  # el bucle termina en el último día

    # mejor día
    best = max(days, key=lambda d: d["count"], default=None)

    # totales por mes (clave "YYYY-MM")
    by_month: dict[str, int] = {}
    for d in days:
        key = d["date"][:7]
        by_month[key] = by_month.get(key, 0) + d["count"]

    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": best_streak,
        "best_day": best,
        "by_month": dict(sorted(by_month.items())),
    }


def main() -> None:
    username = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_USER
    print(f"Descargando contribuciones de {username} ...")
    days = fetch_days(username)
    if not days:
        sys.exit("No se encontraron celdas de día (¿cambió el HTML de GitHub?)")

    s = stats(days)
    payload = {
        "username": username,
        "year_total": s["total"],
        "current_streak": s["current_streak"],
        "longest_streak": s["longest_streak"],
        "best_day": s["best_day"],
        "by_month": s["by_month"],
        "days": days,
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        f"OK: {len(days)} días, {s['total']} contribuciones, "
        f"racha actual {s['current_streak']}, máxima {s['longest_streak']}"
    )
    print(f"Escrito {OUT}")


if __name__ == "__main__":
    main()
