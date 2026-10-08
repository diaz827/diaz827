"""Prepara la foto para la conversión a ASCII.

1. Quita el fondo con rembg (aisla al sujeto).
2. Aumenta el contraste local con CLAHE (luces y sombras reales).
3. Compone sobre blanco puro (el fondo cae en el espacio de la rampa ASCII).

Uso:
    python scripts/prep_photo.py <ruta-de-la-foto>
Salida:
    source-prepped.png (escala de grises, junto a la foto o en la raíz)
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Uso: python scripts/prep_photo.py <ruta-de-la-foto>")

    src = Path(sys.argv[1])
    if not src.exists():
        sys.exit(f"No existe la foto: {src}")

    print(f"[1/4] Leyendo {src.name} ...")
    img = Image.open(src).convert("RGB")

    print("[2/4] Quitando fondo con rembg (modelo u2netp) ...")
    session = new_session("u2netp")
    cut = remove(img, session=session)

    print("[3/4] CLAHE + composición sobre blanco ...")
    rgba = np.array(cut)
    rgb = rgba[..., :3]
    alpha = rgba[..., 3]

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    contrast = clahe.apply(gray)

    white = np.full_like(contrast, 255)
    a = (alpha.astype(np.float32) / 255.0)[..., None]
    composed = (contrast[..., None].astype(np.float32) * a + 255.0 * (1 - a)).astype(np.uint8)
    composed = composed[..., 0]

    out = src.parent / "source-prepped.png"
    Image.fromarray(composed).save(out)
    print(f"[4/4] Guardado: {out}")


if __name__ == "__main__":
    main()
