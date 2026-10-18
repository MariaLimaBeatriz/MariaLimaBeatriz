"""Prepara a foto: remove o fundo (GrabCut), realça o contraste local (CLAHE)
e coloca o sujeito sobre fundo branco puro. Saída: source-prepped.png (cinza).

Uso: python scripts/prep_photo.py minha-foto.png
"""
import sys
import cv2
import numpy as np
from PIL import Image


def main(path, out="source-prepped.png"):
    im = Image.open(path).convert("RGBA")
    alpha = np.array(im)[:, :, 3]
    rgb = np.array(im.convert("RGB"))
    h, w = rgb.shape[:2]

    # Fora do recorte circular (se houver) = fundo certo
    mask = np.full((h, w), cv2.GC_PR_BGD, np.uint8)
    mask[alpha < 10] = cv2.GC_BGD
    # Região central provavelmente é o rosto/corpo
    mask[int(h * 0.12):int(h * 0.95), int(w * 0.25):int(w * 0.80)] = cv2.GC_PR_FGD
    mask[int(h * 0.25):int(h * 0.75), int(w * 0.38):int(w * 0.68)] = cv2.GC_FGD

    bgd = np.zeros((1, 65), np.float64)
    fgd = np.zeros((1, 65), np.float64)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    cv2.grabCut(bgr, mask, None, bgd, fgd, 6, cv2.GC_INIT_WITH_MASK)
    fg = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((15, 15), np.uint8))
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    # mantém só o maior bloco conectado (o sujeito) e descarta restos do fundo
    n, labels, stats, _ = cv2.connectedComponentsWithStats((fg > 127).astype(np.uint8))
    if n > 1:
        biggest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        fg = np.where(labels == biggest, 255, 0).astype(np.uint8)
    # limpeza manual de restos do fundo (ajuste os valores se trocar a foto)
    fg[: int(h * 0.40), : int(w * 0.47)] = 0       # objeto cinza atrás do cabelo
    fg[int(h * 0.76):, : int(w * 0.30)] = 0        # borda do recorte circular
    fg = cv2.GaussianBlur(fg, (7, 7), 0)

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(6, 6))
    gray = clahe.apply(gray)

    a = (fg.astype(np.float32) / 255.0)
    out_img = (gray * a + 255 * (1 - a)).astype(np.uint8)
    Image.fromarray(out_img).save(out)
    print("salvo:", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "source-photo.png")
