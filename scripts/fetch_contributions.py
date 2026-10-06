#!/usr/bin/env python3
"""Scrape the public contribution calendar (github.com/users/<user>/contributions,
the same HTML fragment the profile page uses) and write data/contributions.json
with the daily counts plus derived stats. No token, no API."""
import datetime as dt, json, os, re, sys
import requests
from bs4 import BeautifulSoup

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CFG = json.load(open(os.path.join(ROOT, "profile.json")))
USER = os.environ.get("GH_USER", CFG["username"])
OUT = os.path.join(ROOT, "data", "contributions.json")


def scrape():
    r = requests.get(f"https://github.com/users/{USER}/contributions",
                     headers={"User-Agent": "profile-readme-bot"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    tips = {t.get("for"): t.get_text(strip=True) for t in soup.find_all("tool-tip")}
    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        date = td.get("data-date")
        if not date:
            continue
        m = re.match(r"(\d[\d,]*) contribution", tips.get(td.get("id"), ""))
        days.append({"date": date,
                     "count": int(m.group(1).replace(",", "")) if m else 0,
                     "level": int(td.get("data-level") or 0)})
    if not days:
        sys.exit("No calendar cells found — GitHub markup may have changed.")
    return sorted(days, key=lambda d: d["date"])


def streaks(days):
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)
    i = len(days) - 1
    if days[i]["count"] == 0:      # today isn't over yet
        i -= 1
    current = 0
    while i >= 0 and days[i]["count"]:
        current += 1
        i -= 1
    return current, longest


def main():
    days = scrape()
    current, longest = streaks(days)
    best = max(days, key=lambda d: d["count"])
    out = {
        "username": USER,
        "updated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"),
        "total": sum(d["count"] for d in days),
        "active_days": sum(1 for d in days if d["count"]),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
        "days": days,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1)
    print(f"{USER}: {out['total']} contributions, streak {current}, longest {longest}")


if __name__ == "__main__":
    main()
