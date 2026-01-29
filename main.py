import json
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

HN_URL = "https://news.ycombinator.com/"
MICROLINK_API = "https://r.jina.ai/http://r.jina.ai/https://api.microlink.io/?url="  # proxy-friendly fallback

# Nëse s'do proxy, përdor direkt: "https://api.microlink.io/?url="
DIRECT_MICROLINK_API = "https://api.microlink.io/?url="

USER_AGENT = "Mozilla/5.0 (compatible; WebScrapingCourse/1.0)"


def scrape_hackernews(limit: int = 10) -> list[dict]:
    """Scrape top stories from Hacker News front page."""
    r = requests.get(HN_URL, headers={"User-Agent": USER_AGENT}, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")
    rows = soup.select("tr.athing")[:limit]

    items = []
    for row in rows:
        title_link = row.select_one("span.titleline a")
        if not title_link:
            continue

        title = title_link.get_text(strip=True)
        url = title_link.get("href", "").strip()

        # HN ndonjëherë ka link relativ; e normalizojmë
        if url.startswith("item?id="):
            url = HN_URL + url

        items.append(
            {
                "source": "HackerNews",
                "scraped_title": title,
                "url": url,
            }
        )
    return items


def enrich_with_microlink(url: str) -> dict:
    """
    Call Microlink API to fetch metadata for a URL.
    Returns safe fields even if request fails.
    """
    # Provo direkt API
    try:
        r = requests.get(
            DIRECT_MICROLINK_API + requests.utils.quote(url, safe=""),
            headers={"User-Agent": USER_AGENT},
            timeout=20,
        )
        if r.status_code == 429:
            # Nëse rate limited, provojmë fallback
            raise RuntimeError("Rate limited, trying fallback.")
        r.raise_for_status()
        data = r.json()
    except Exception:
        # Fallback (shpesh ndihmon në mjedise ku ka bllokime)
        try:
            r = requests.get(
                MICROLINK_API + requests.utils.quote(url, safe=""),
                headers={"User-Agent": USER_AGENT},
                timeout=20,
            )
            r.raise_for_status()
            data = r.json()
        except Exception:
            data = {"status": "error", "data": {}}

    d = data.get("data", {}) if isinstance(data, dict) else {}

    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    return {
        "api_title": d.get("title"),
        "description": d.get("description"),
        "image": (d.get("image", {}) or {}).get("url") if isinstance(d.get("image"), dict) else d.get("image"),
        "publisher": d.get("publisher"),
        "lang": d.get("lang"),
        "domain": domain,
        "api_status": data.get("status") if isinstance(data, dict) else "error",
    }


def main():
    limit = 10     

    scraped = scrape_hackernews(limit=limit)

    final_rows = []
    for i, item in enumerate(scraped, start=1):
        url = item["url"]
        api_data = enrich_with_microlink(url)

        merged = {
            **item,
            **api_data,
            "scraped_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        final_rows.append(merged)

        # delay i vogël për të shmangur rate limits
        time.sleep(0.6)

        print(f"[{i}/{len(scraped)}] OK - {item['scraped_title']}")

    df = pd.DataFrame(final_rows)

    # Ruaj CSV
    df.to_csv("output.csv", index=False, encoding="utf-8")

    # Ruaj JSON
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(final_rows, f, ensure_ascii=False, indent=2)

    print("\nSaved: output.csv and output.json")


if __name__ == "__main__":
    main()
