"""Converte source-prepped.png em um SVG de arte ASCII monocromática que
'digita' linha por linha (SMIL). GitHub renderiza essa animação em <img>.

Uso: python scripts/make_ascii_svg.py   ->  escreve assets/bia-ascii.svg
"""
import numpy as np
from html import escape
from PIL import Image

SRC = "source-prepped.png"
OUT = "assets/bia-ascii.svg"
COLS = 96                       # largura em caracteres
RAMP = " .`:-=+*cs#%@"          # claro (esparso) -> escuro (denso); espaço = fundo
FONT = 8                        # px
CW = 4.8                        # largura de cada caractere (px)
LH = 9                          # altura da linha (px)
FILL = "#c9d1d9"                # um tom só: evita o efeito "ruído"
BG = "#0d1117"
PAD = 14
CROP = (100, 8, 312, 250)      # x0, y0, x1, y1 na imagem preparada


def to_rows():
    im = Image.open(SRC).convert("L")
    a = np.array(im)
    # recorta em volta do sujeito (tudo que não é branco puro)
    # recorte em rosto + ombros (x0, y0, x1, y1) -- ajuste se trocar a foto
    x0, y0, x1, y1 = CROP
    a = a[y0:y1, x0:x1]
    # estica o contraste usando só os pixels do sujeito (não-branco)
    subj = a[a < 245]
    lo, hi = np.percentile(subj, 3), np.percentile(subj, 97)
    a = np.clip((a.astype(float) - lo) / (hi - lo), 0, 1)
    a = np.where(a > 0.96, 1.0, a)
    a = (a * 255).astype(np.uint8)
    h, w = a.shape
    rows = int(COLS * (h / w) * (CW / LH))
    small = np.array(Image.fromarray(a).resize((COLS, rows), Image.LANCZOS)).astype(float) / 255.0
    small = np.clip(small, 0, 1) ** 1.1
    out = []
    for r in small:
        line = "".join(RAMP[int(round((1 - v) * (len(RAMP) - 1)))] for v in r)
        out.append(line.rstrip())
    return out


def main():
    rows = to_rows()
    W = COLS * CW
    width = int(W + PAD * 2)
    height = int(len(rows) * LH + PAD * 2 + 22)
    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Retrato em arte ASCII">')
    p.append(f'<rect width="{width}" height="{height}" rx="10" fill="{BG}" stroke="#30363d"/>')
    # barra de título estilo terminal
    p.append('<circle cx="16" cy="14" r="4.5" fill="#ff5f56"/><circle cx="32" cy="14" r="4.5" fill="#ffbd2e"/><circle cx="48" cy="14" r="4.5" fill="#27c93f"/>')
    p.append(f'<g transform="translate({PAD},{PAD + 18})">')
    p.append("<defs>")
    for i in range(len(rows)):
        begin = 0.2 + i * 0.045
        p.append(f'<clipPath id="c{i}"><rect x="0" y="{i * LH}" height="{LH}" width="0">'
                 f'<animate attributeName="width" from="0" to="{W:.1f}" dur="0.55s" begin="{begin:.3f}s" fill="freeze"/></rect></clipPath>')
    p.append("</defs>")
    for i, line in enumerate(rows):
        begin = 0.2 + i * 0.045
        y = i * LH + FONT + 0.5
        n = max(len(line), 1)
        p.append(f'<text x="0" y="{y:.1f}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" '
                 f'font-size="{FONT}" fill="{FILL}" xml:space="preserve" textLength="{n * CW:.1f}" lengthAdjust="spacing" '
                 f'clip-path="url(#c{i})">{escape(line)}</text>')
        # cursor (bloquinho) que acompanha a "digitação" e some no fim da linha
        p.append(f'<rect x="0" y="{i * LH + 1}" width="{CW:.1f}" height="{LH - 2}" fill="{FILL}" opacity="0">'
                 f'<animate attributeName="x" from="0" to="{n * CW:.1f}" dur="0.55s" begin="{begin:.3f}s" fill="freeze"/>'
                 f'<animate attributeName="opacity" values="0;0.9;0.9;0" keyTimes="0;0.02;0.95;1" dur="0.55s" begin="{begin:.3f}s" fill="freeze"/></rect>')
    p.append("</g></svg>")
    open(OUT, "w", encoding="utf-8").write("\n".join(p))
    print(f"ok: {OUT} ({width}x{height}, {len(rows)} linhas)")
    return rows


if __name__ == "__main__":
    for l in main():
        print(l)
