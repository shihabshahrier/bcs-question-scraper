import os
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

# 1. CONFIGURATION

# Years to scrape
YEARS = list(range(10, 44))  # 10 through 43
BASE_URL = "https://10minuteschool.com/content/{slug}/"
DOWNLOAD_DIR = "downloaded_html"
OUTPUT_CSV = "bcs_10_to_43.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"
    )
}

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def ordinal_suffix(n):
    if 11 <= n % 100 <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def try_download(year):
    """
    Try slug variants for a given year:
    1) question-bank
    2) preli-question-bank
    3) mcq-question-bank 
    Returns the slug used or None.
    """
    suffix = ordinal_suffix(year)
    base = f"{year}{suffix}-bcs"
    candidates = [
        f"{base}-question-bank",
        f"{base}-preli-question-bank",
        f"{base}-mcq-question-bank"
    ]
    if year == 33:
        candidates.append(f"33nd-bcs-mcq-question-bank")
    if year == 39:
        candidates.append(f"39st-bcs-preli-question-bank")
    if year == 41:
        candidates.append(f"41st-bcs-mcq-qbank")

    for slug in candidates:
        url = BASE_URL.format(slug=slug)
        local_path = os.path.join(DOWNLOAD_DIR, f"{year}.html")

        if os.path.exists(local_path):
            print(f"[SKIP] {year}.html already exists (slug `{slug}`)")
            return slug

        print(f"[TRY] Download BCS {year} with slug `{slug}` → {url}")
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code == 200:
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(resp.text)
            print(f"[OK]  Saved as {year}.html")
            time.sleep(2)
            return slug
        else:
            print(f"  ↳ Failed ({resp.status_code}) with `{slug}`")

    print(f"[ERROR] Could not download BCS {year} with any slug")
    return None


def download_all():
    used = {}
    for year in YEARS:
        slug = try_download(year)
        if slug:
            used[year] = slug
    return used


def parse_all(used_slugs):
    records = []
    for year in sorted(used_slugs):
        path = os.path.join(DOWNLOAD_DIR, f"{year}.html")
        if not os.path.exists(path):
            continue

        print(f"[PARSE] {year}.html")
        soup = BeautifulSoup(open(path, encoding="utf-8"), "html.parser")
        table = soup.find("table")
        if not table:
            print(f"  → No <table> found in {year}.html")
            continue

        rows = table.find_all("tr")
        question, options, correct = None, [], None

        for row in rows:
            cols = row.find_all("td")
            # Single-cell: question or explanation
            if len(cols) == 1 and cols[0].get("colspan") == "4":
                text = cols[0].get_text(strip=True)
                if text.startswith("Explanation"):
                    records.append({
                        "bcs_number": year,
                        "question": question,
                        "option_a": options[0] if len(options)>0 else "",
                        "option_b": options[1] if len(options)>1 else "",
                        "option_c": options[2] if len(options)>2 else "",
                        "option_d": options[3] if len(options)>3 else "",
                        "correct_option": correct,
                        "explanation": text.replace("Explanation :", "").strip(),
                    })
                    question, options, correct = None, [], None
                else:
                    question = text
            # Four-cell row: options
            elif len(cols) == 4:
                for idx, col in enumerate(cols):
                    opt = col.get_text(strip=True)
                    options.append(opt)
                    if col.find("strong"):
                        correct = ["A","B","C","D"][idx]

    return records


if __name__ == "__main__":
    slugs_used = download_all()
    data = parse_all(slugs_used)
    df = pd.DataFrame(data)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"\nDone: {len(df)} questions saved to {OUTPUT_CSV}")
