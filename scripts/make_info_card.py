"""Gera o cartão estilo neofetch (assets/info-card.svg) com linhas que
aparecem uma a uma. Edite a lista ROWS para mudar o conteúdo.

Uso: python scripts/make_info_card.py        (animado)
     STATIC=1 python scripts/make_info_card.py   (quadro final, sem animação)
"""
import os
from html import escape

OUT = "assets/info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

W, H = 490, 362
USER = "bia@github"

# (chave, [linhas do valor])
ROWS = [
    ("Nome", ["Bia"]),
    ("Agora", ["Estudante de ADS desbravando o", "mundo do desenvolvimento"]),
    ("Foco", ["Java + IA"]),
    ("Stack", ["Java · SQL · IA generativa"]),
    ("Bootcamp", ["Elastech · SoulCode Academy", "em parceria com o PagBank"]),
    ("LinkedIn", ["in/maria-beatrizlima"]),
    ("E-mail", ["beatrizlima086@gmail.com"]),
]

BG, BORDER = "#0d1117", "#30363d"
KEY, VAL, DIM = "#58a6ff", "#c9d1d9", "#8b949e"
ACCENT = "#3fb950"
LH = 25
X0 = 22


def main():
    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Cartão de informações da Bia">')
    p.append("<style>")
    p.append("text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:14px}")
    if not STATIC:
        p.append(".l{opacity:0;animation:in .45s ease-out forwards}")
        p.append("@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}")
    p.append("</style>")
    p.append(f'<rect width="{W}" height="{H}" rx="10" fill="{BG}" stroke="{BORDER}"/>')
    p.append('<circle cx="16" cy="14" r="4.5" fill="#ff5f56"/><circle cx="32" cy="14" r="4.5" fill="#ffbd2e"/><circle cx="48" cy="14" r="4.5" fill="#27c93f"/>')
    p.append(f'<text x="{W/2}" y="18" text-anchor="middle" fill="{DIM}" style="font-size:11px">neofetch</text>')

    n = 0

    def line(y, inner):
        nonlocal n
        delay = 0.3 + n * 0.16
        n += 1
        style = "" if STATIC else f' style="animation-delay:{delay:.2f}s"'
        p.append(f'<g class="l"{style}>{inner}</g>')

    y = 52
    line(y, f'<text x="{X0}" y="{y}" fill="{ACCENT}" font-weight="bold">{USER}</text>')
    y += 8
    line(y, f'<text x="{X0}" y="{y + 8}" fill="{DIM}">{"─" * 36}</text>')
    y += 28
    KEYW = 10  # largura da coluna das chaves, em caracteres
    for key, vals in ROWS:
        for i, v in enumerate(vals):
            k = f"{key}:" if i == 0 else ""
            inner = (f'<text x="{X0}" y="{y}" xml:space="preserve">'
                     f'<tspan fill="{KEY}" font-weight="bold">{escape(k.ljust(KEYW))}</tspan>'
                     f'<tspan fill="{VAL}">{escape(v)}</tspan></text>')
            line(y, inner)
            y += LH
        y += 2
    # paleta de cores, como no neofetch
    y += 4
    colors = ["#ff5f56", "#ffbd2e", "#27c93f", "#58a6ff", "#bc8cff", "#39c5cf", "#c9d1d9"]
    blocks = "".join(f'<rect x="{X0 + i * 26}" y="{y - 12}" width="24" height="14" rx="2" fill="{c}"/>' for i, c in enumerate(colors))
    line(y, blocks)
    open(OUT, "w", encoding="utf-8").write("\n".join(p) + "\n</svg>")
    print(f"ok: {OUT} (altura útil até y={y + 6}, H={H})")


if __name__ == "__main__":
    main()
