"""Lê data/contributions.json e desenha o calendário de contribuições
(53 semanas x 7 dias) como SVG animado: assets/contrib-heatmap.svg.

Uso: python scripts/render_heatmap_svg.py
     python scripts/render_heatmap_svg.py --placeholder   (cria um quadro vazio inicial)
"""
import json
import os
import sys
from datetime import date, timedelta

DATA = "data/contributions.json"
OUT = "assets/contrib-heatmap.svg"
STATIC = os.environ.get("STATIC") == "1"
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
BOX, GAP = 13, 3
STEP = BOX + GAP
LEFT, TOP = 14, 34
W = 860


def placeholder_data(user="MariaLimaBeatriz"):
    end = date.today()
    start = end - timedelta(days=364)
    start -= timedelta(days=(start.weekday() + 1) % 7)   # volta para o domingo
    days, d = [], start
    while d <= end:
        days.append({"date": d.isoformat(), "count": 0, "level": 0})
        d += timedelta(days=1)
    return {"user": user, "placeholder": True, "days": days, "total": 0,
            "current_streak": 0, "longest_streak": 0, "best_day": {"date": "", "count": 0}}


def fmt(n):
    return f"{n:,}".replace(",", ".")


def render(data):
    days = data["days"]
    first = date.fromisoformat(days[0]["date"])
    first_sunday = first - timedelta(days=(first.weekday() + 1) % 7)
    weeks = (date.fromisoformat(days[-1]["date"]) - first_sunday).days // 7 + 1
    H = TOP + 7 * STEP + 46
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Gráfico de contribuições no GitHub">']
    p.append("<style>")
    p.append("text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:11px;fill:#8b949e}")
    if not STATIC:
        p.append(".b{opacity:0;transform-box:fill-box;animation:pop .5s ease-out forwards}")
        p.append("@keyframes pop{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}")
    p.append("</style>")
    p.append(f'<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>')

    last_month = None
    for d in days:
        dt = date.fromisoformat(d["date"])
        col = (dt - first_sunday).days // 7
        row = (dt.weekday() + 1) % 7
        x, y = LEFT + col * STEP, TOP + row * STEP
        if row == 0 and dt.month != last_month:
            if col < weeks - 2:
                p.append(f'<text x="{x}" y="{TOP - 10}">{MESES[dt.month - 1]}</text>')
            last_month = dt.month
        lvl = max(0, min(5, d["level"]))
        delay = "" if STATIC else f' style="animation-delay:{(col + row) * 0.022:.3f}s"'
        p.append(f'<rect class="b" x="{x}" y="{y}" width="{BOX}" height="{BOX}" rx="3" fill="{PALETTE[lvl]}"{delay}/>')

    yb = TOP + 7 * STEP + 24
    if data.get("placeholder"):
        info = "aguardando a primeira atualização automática"
    else:
        info = (f"{fmt(data['total'])} contribuições no último ano · sequência atual: "
                f"{data['current_streak']} dias · maior sequência: {data['longest_streak']} dias")
    p.append(f'<text x="{LEFT}" y="{yb}">{info}</text>')
    # legenda Menos -> Mais
    lx = W - LEFT - (6 * STEP + 70)
    p.append(f'<text x="{lx}" y="{yb}">menos</text>')
    for i, c in enumerate(PALETTE):
        p.append(f'<rect x="{lx + 40 + i * STEP}" y="{yb - 11}" width="{BOX}" height="{BOX}" rx="3" fill="{c}"/>')
    p.append(f'<text x="{lx + 44 + 6 * STEP}" y="{yb}">mais</text>')
    p.append("</svg>")
    return "\n".join(p)


def main():
    os.makedirs("assets", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    if "--placeholder" in sys.argv:
        data = placeholder_data()
        json.dump(data, open(DATA, "w", encoding="utf-8"), ensure_ascii=False)
    else:
        data = json.load(open(DATA, encoding="utf-8"))
    open(OUT, "w", encoding="utf-8").write(render(data))
    print(f"ok: {OUT}")


if __name__ == "__main__":
    main()
