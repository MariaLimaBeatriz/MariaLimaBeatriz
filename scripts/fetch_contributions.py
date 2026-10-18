"""Busca o calendário público de contribuições (sem token) e grava
data/contributions.json com os dias e algumas estatísticas.

Uso: python scripts/fetch_contributions.py [usuario]
"""
import json
import re
import sys
from collections import defaultdict
from datetime import date, timedelta

import requests
from bs4 import BeautifulSoup

USER = sys.argv[1] if len(sys.argv) > 1 else "MariaLimaBeatriz"
OUT = "data/contributions.json"


def fetch_days(user):
    url = f"https://github.com/users/{user}/contributions"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    tips = {t.get("for"): t.get_text(" ", strip=True) for t in soup.find_all("tool-tip")}
    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        d = td.get("data-date")
        if not d:
            continue
        level = int(td.get("data-level", 0))
        m = re.match(r"(\d+)\s+contribution", tips.get(td.get("id"), ""))
        count = int(m.group(1)) if m else (level if level else 0)
        days.append({"date": d, "count": count, "level": level})
    days.sort(key=lambda x: x["date"])
    return days


def stats(days):
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"]) if days else {"date": "", "count": 0}
    longest = cur = 0
    prev = None
    for d in days:
        dt = date.fromisoformat(d["date"])
        if d["count"] > 0:
            cur = cur + 1 if prev and dt - prev == timedelta(days=1) else 1
            longest = max(longest, cur)
            prev = dt
        else:
            cur, prev = 0, None
    # sequência atual: conta de trás para frente (hoje ainda pode estar zerado)
    current = 0
    for i, d in enumerate(reversed(days)):
        if d["count"] > 0:
            current += 1
        elif i == 0:
            continue
        else:
            break
    months = defaultdict(int)
    for d in days:
        months[d["date"][:7]] += d["count"]
    return {"total": total, "current_streak": current, "longest_streak": longest,
            "best_day": best, "months": dict(months)}


def main():
    days = fetch_days(USER)
    if not days:
        sys.exit("Nenhum dia encontrado: o HTML do GitHub pode ter mudado. Nada foi alterado.")
    data = {"user": USER, "placeholder": False, "days": days, **stats(days)}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    print(f"ok: {len(days)} dias, {data['total']} contribuições")


if __name__ == "__main__":
    main()
